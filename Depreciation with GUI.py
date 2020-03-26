from PyQt5.QtWidgets import *
import sys
import mysql.connector
import config

# Create the database if it doesn't exist
db = mysql.connector.connect(
    host=config.host_finance,
    user=config.user_finance,
    passwd=config.password_finance,
)
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS startupfinancials")
cursor.close()
db.close()


# Connect the the database and create the tables if they don't exist
db = mysql.connector.connect(
    host=config.host_finance,
    user=config.user_finance,
    passwd=config.password_finance,
    database=config.database_finance
)

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS CapEx (ID Int Primary Key, Name Varchar(50) Not Null, Category Varchar (20) Not Null, Cost Decimal(12,2) Not Null, Month Int Not Null, Year Int Not Null, Life Int Not Null)")
cursor.execute("CREATE TABLE IF NOT EXISTS BookValue (ID Int Primary Key, AssetID Int Not Null, Name Varchar(50) Not Null, Month Int Not Null, Year Int Not Null, BookValue Decimal(12,2) Not Null,Depr Decimal(12,2) Not Null)")
db.commit()


# Convert monthly text values to number values for depreciation calculation
month_conversions = {
    "jan": "1",
    "feb": "2",
    "mar": "3",
    "apr": "4",
    "may": "5",
    "jun": "6",
    "jul": "7",
    "aug": "8",
    "sep": "9",
    "oct": "10",
    "nov": "11",
    "dec": "12",
    "january": "1",
    "february": "2",
    "march": "3",
    "april": "4",
    "june": "6",
    "july": "7",
    "august": "8",
    "september": "9",
    "october": "10",
    "november": "11",
    "december": "12"
}


class WidgetGallery(QDialog):

    def asset_input():

        cursor.execute("select count(ID) from startupfinancials.capex;")
        id_check = cursor.fetchone()[0]
        if id_check == 0:
            id_num = 1
        else:
            cursor.execute("select max(ID) from startupfinancials.capex;")
            id_num = cursor.fetchone()[0] + 1


        a_name = str(asset_name.text())
        a_cat = str(asset_category.text())
        a_cost = float(asset_cost.text())
        a_month = month_conversions[month_options.currentText().lower()]
        a_year = int(year_options.currentText())
        a_life = int(life_options.currentText()) * 12


        sql = "insert into startupfinancials.capex (ID, Name, Category, Cost, Month, Year, Life) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (id_num, a_name, a_cat, a_cost, a_month, a_year, a_life)
        cursor.execute(sql, val)
        db.commit()

        cursor.execute("select count(ID) from startupfinancials.bookvalue;")
        depr_id_num = cursor.fetchone()[0] + 1
        book_value = a_cost
        depr_month = int(a_month)
        depr_year = a_year
        depr = a_cost / a_life

        sql = "insert into startupfinancials.BookValue (ID, AssetID, Name, Month, Year, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (depr_id_num, id_num, a_name, depr_month, depr_year, book_value, 0)
        cursor.execute(sql, val)
        db.commit()
        book_value = book_value - depr
        depr_month = depr_month + 1
        depr_id_num = depr_id_num + 1

        while book_value > -1:
            if depr_month == 13:
                depr_month = 1
                depr_year = depr_year + 1
                sql = "insert into startupfinancials.BookValue (ID, AssetID, Name, Month, Year, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
                val = (depr_id_num, id_num, a_name, depr_month, depr_year, book_value, depr)
                cursor.execute(sql, val)
                db.commit()
                book_value = book_value - depr
                depr_month = depr_month + 1
                depr_id_num = depr_id_num + 1

            else:
                sql = "insert into startupfinancials.BookValue (ID, AssetID, Name, Month, Year, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
                val = (depr_id_num, id_num, a_name, depr_month, depr_year, book_value, depr)
                cursor.execute(sql, val)
                db.commit()
                book_value = book_value - depr
                depr_month = depr_month + 1
                depr_id_num = depr_id_num + 1


    def __init__(self, parent=None):

        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        line_1 = QLabel("The fixed asset tab on the right shows\n"
                        "your current assets entered into the system.\n"
                        "The monthly expense tab shows your depreciation\n"
                        "expense and book value by each month based on\n"
                        "your current asset listed.\n"
                        "Please use the box below to add any\n"
                        "additional assets to your list.")

        refresh_button = QPushButton("Refresh Tables")
        refresh_button.setDefault(True)


        self.new_asset_entry()
        self.current_asset_table()


        summary = QVBoxLayout()
        summary.addWidget(line_1)
        summary.addWidget(refresh_button)
        summary.addStretch(1)


        mainLayout = QGridLayout()
        mainLayout.addLayout(summary, 0, 0)
        mainLayout.addWidget(self.topLeftGroupBox, 1,0)
        mainLayout.addWidget(self.bottomLeftTabWidget, 0, 1, 5, 5)
        self.setLayout(mainLayout)

    def new_asset_entry(self):
        self.topLeftGroupBox = QGroupBox("New Assets")
        global month_options, year_options, life_options, asset_name, asset_cost, asset_category

        month_options = QComboBox()
        month_options.addItems(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        month_labol = QLabel("Purchase Month:")

        year_options = QComboBox()
        year_options.addItems(["2008","2009", "2010", "2011", "2012", "2013","2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"])
        year_labol = QLabel("Purchase Year: ")

        life_options = QComboBox()
        life_options.addItems(["1","2","3", "5", "7", "10", "15","20", "30"])
        life_labol = QLabel("Asset Life In Years: ")

        asset_name = QLineEdit()
        name_labol = QLabel("Asset Name: ")

        asset_cost = QLineEdit()
        cost_labol = QLabel("Asset Cost: ")

        asset_category = QLineEdit()
        category_labol = QLabel("Asset Category: ")

        add_new_asset_button = QPushButton("Add New Asset")
        add_new_asset_button.setDefault(True)


        entries = QGridLayout()
        entries.addWidget(name_labol, 0, 0)
        entries.addWidget(asset_name, 0, 1, 1, 5)
        entries.addWidget(category_labol, 1, 0)
        entries.addWidget(asset_category, 1, 1, 1, 5)
        entries.addWidget(cost_labol, 2, 0)
        entries.addWidget(asset_cost, 2, 1, 1, 5)
        entries.addWidget(month_labol, 3, 0)
        entries.addWidget(month_options, 3, 1, 1, 5)
        entries.addWidget(year_labol, 4, 0)
        entries.addWidget(year_options, 4, 1, 1, 5)
        entries.addWidget(life_labol, 5, 0)
        entries.addWidget(life_options, 5, 1, 1, 5)
        entries.addWidget(cost_labol, 6, 0)
        entries.addWidget(asset_cost, 6, 1, 1, 5)
        entries.addWidget(add_new_asset_button, 7, 1, 1, 5)
        self.topLeftGroupBox.setLayout(entries)

        add_new_asset_button.clicked.connect(WidgetGallery.asset_input)


    def current_asset_table(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        cursor.execute("select * from startupfinancials.capex;")
        current_asset = cursor.fetchall()

        current_row = (len(current_asset))

        current_tab = QWidget()
        current_size = QTableWidget(current_row, 7)
        current_size.setHorizontalHeaderLabels(["Asset #", "Asset Name","Category", "Purchase Cost", "Purchase Month", "Purchase Year", "Asset Life"])
        current_size.setColumnWidth(0, 100)
        current_size.setColumnWidth(1, 200)
        current_size.setColumnWidth(2, 200)
        current_size.setColumnWidth(3, 150)
        current_size.setColumnWidth(4, 150)
        current_size.setColumnWidth(5, 150)
        current_size.setColumnWidth(6, 150)
        current_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        current_table = QHBoxLayout()
        current_table.setContentsMargins(5, 5, 5, 5)
        current_table.addWidget(current_size)
        current_tab.setLayout(current_table)


        cursor.execute("select * from startupfinancials.bookvalue;")
        current_depr = cursor.fetchall()

        depr_row = (len(current_depr))

        expense_tab = QWidget()
        expense_size = QTableWidget(depr_row, 7)
        expense_size.setHorizontalHeaderLabels(["Primary #", "Asset #", "Asset Name", "Month", "Year", "Book Value", "Depr Amount"])
        expense_size.setColumnWidth(0, 75)
        expense_size.setColumnWidth(1, 75)
        expense_size.setColumnWidth(2, 200)
        expense_size.setColumnWidth(3, 60)
        expense_size.setColumnWidth(4, 60)
        expense_size.setColumnWidth(5, 150)
        expense_size.setColumnWidth(6, 150)
        expense_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        expense_table = QHBoxLayout()
        expense_table.setContentsMargins(5, 5, 5, 5)
        expense_table.addWidget(expense_size)
        expense_tab.setLayout(expense_table)

        self.bottomLeftTabWidget.addTab(current_tab, " Fixed Asset List")
        self.bottomLeftTabWidget.addTab(expense_tab, " Monthly Expense")

        for row_number, row_data in enumerate(current_asset):
            for column_number, data in enumerate(row_data):
                current_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(current_depr):
            for column_number, data in enumerate(row_data):
                expense_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))




if __name__ == '__main__':
    ex = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setGeometry(200, 200, 1500, 400)
    gallery.show()
    sys.exit(ex.exec_())

cursor.close()
db.close()


