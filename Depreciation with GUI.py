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

cursor.execute("CREATE TABLE IF NOT EXISTS CapEx (AssetID Int Primary Key, Name Varchar(50) Not Null, Category Varchar (20) Not Null, Cost Decimal(12,2) Not Null, Month Int Not Null, Year Int Not Null, Life Int Not Null)")
cursor.execute("CREATE TABLE IF NOT EXISTS BookValue (DeprID Int Primary Key, AssetID Int Not Null, Month Int Not Null, Year Int Not Null, NetValue Decimal(12,2) Not Null, BookValue Decimal(12,2) Not Null, Depr Decimal(12,2) Not Null)")
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

    def refresh_table(self):
        gallery.close()
        gallery.empty_tables()
        gallery.new_asset_entry()
        gallery.current_asset_table()
        gallery.__init__()
        gallery.repaint()
        gallery.update()
        gallery.setGeometry(100, 100, 1500, 900)
        gallery.show()


    def empty_data():
        cursor.execute("Delete from startupfinancials.capex;")
        cursor.execute("Delete from startupfinancials.bookvalue;")
        db.commit()
        gallery.refresh_table()

    def remove_asset():
        a_number = str(asset_number.text())

        cursor.execute("delete from startupfinancials.capex where AssetID =" + str(a_number))
        cursor.execute("delete from startupfinancials.bookvalue where AssetID =" + str(a_number))
        db.commit()
        gallery.refresh_table()


    def asset_input():

        cursor.execute("select count(AssetID) from startupfinancials.capex;")
        id_check = cursor.fetchone()[0]
        if id_check == 0:
            id_num = 1
        else:
            cursor.execute("select max(AssetID) from startupfinancials.capex;")
            id_num = cursor.fetchone()[0] + 1


        a_name = str(asset_name.text())
        a_cat = str(asset_category.text())
        a_cost = float(asset_cost.text())
        a_month = month_conversions[month_options.currentText().lower()]
        a_year = int(year_options.currentText())
        a_life = int(life_options.currentText()) * 12


        sql = "insert into startupfinancials.capex (AssetID, Name, Category, Cost, Month, Year, Life) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (id_num, a_name, a_cat, a_cost, a_month, a_year, a_life)
        cursor.execute(sql, val)
        db.commit()

        cursor.execute("select count(DeprID) from startupfinancials.bookvalue;")
        depr_id_check = cursor.fetchone()[0]
        if depr_id_check == 0:
            depr_id_num = 1
        else:
            cursor.execute("select max(DeprID) from startupfinancials.bookvalue;")
            depr_id_num = cursor.fetchone()[0] + 1

        book_value = a_cost
        net_value = a_cost
        depr_month = int(a_month)
        depr_year = a_year
        depr = a_cost / a_life

        sql = "insert into startupfinancials.BookValue (DeprID, AssetID, Month, Year, NetValue, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
        val = (depr_id_num, id_num, depr_month, depr_year, net_value, book_value, 0)
        cursor.execute(sql, val)
        db.commit()
        book_value = book_value - depr
        depr_month = depr_month + 1
        depr_id_num = depr_id_num + 1

        while book_value > -1:
            if depr_month == 13:
                depr_month = 1
                depr_year = depr_year + 1
                sql = "insert into startupfinancials.BookValue (DeprID, AssetID, Month, Year, NetValue, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
                val = (depr_id_num, id_num, depr_month, depr_year, net_value, book_value, depr)
                cursor.execute(sql, val)
                db.commit()
                book_value = book_value - depr
                depr_month = depr_month + 1
                depr_id_num = depr_id_num + 1

            else:
                sql = "insert into startupfinancials.BookValue (DeprID, AssetID, Month, Year, NetValue, BookValue, Depr) values (%s, %s, %s, %s, %s, %s, %s)"
                val = (depr_id_num, id_num, depr_month, depr_year, net_value, book_value, depr)
                cursor.execute(sql, val)
                db.commit()
                book_value = book_value - depr
                depr_month = depr_month + 1
                depr_id_num = depr_id_num + 1

        gallery.refresh_table()


    def __init__(self, parent=None):

        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        line_1 = QLabel("Please use the table below to add\n"
                        "new assets to your list.\n"
                        "\n"
                        "The tabs on the right display:\n"
                        "\n"
                        "1. Fixed Asset List - All the assets that\n"
                        "have been entered into the application\n"
                        "so far.\n"
                        "\n"
                        "2. Summary Monthly Depreciation - Total\n"
                        "depreciation and book value by month\n"
                        "\n"
                        "3. Detailed Monthly Depreciation - Monthly\n"
                        "depreciation and book value by each\n"
                        "month")


        self.new_asset_entry()
        self.empty_tables()
        self.remove_asset_table()
        self.current_asset_table()


        summary = QVBoxLayout()
        summary.addWidget(line_1)
        summary.addStretch(1)


        mainLayout = QGridLayout()
        mainLayout.addLayout(summary, 0, 0)
        mainLayout.addWidget(self.new_asset_box, 1, 0)
        mainLayout.addWidget(self.remove_asset_box, 2, 0)
        mainLayout.addWidget(self.empty_table_box, 3, 0)
        mainLayout.addWidget(self.asset_table_box, 0, 1, 5, 5)
        self.setLayout(mainLayout)

    def new_asset_entry(self):
        self.new_asset_box = QGroupBox("New Assets")
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
        self.new_asset_box.setLayout(entries)

        add_new_asset_button.clicked.connect(WidgetGallery.asset_input)

    def empty_tables(self):
        self.empty_table_box = QGroupBox("Empty Tables")

        empty_table_button = QPushButton("Delete All Data")
        empty_table_button.setDefault(True)


        clear = QGridLayout()
        clear.addWidget(empty_table_button, 0, 0)
        self.empty_table_box.setLayout(clear)

        empty_table_button.clicked.connect(WidgetGallery.empty_data)

    def remove_asset_table(self):
        self.remove_asset_box = QGroupBox("Remove an Assets")
        global asset_number

        asset_number = QLineEdit()
        asset_number_labol = QLabel("Asset Number: ")

        delete_asset_button = QPushButton("Delete This Asset")
        delete_asset_button.setDefault(True)

        delete_item = QGridLayout()
        delete_item.addWidget(asset_number_labol, 0, 0)
        delete_item.addWidget(asset_number, 0, 1, 1, 5)
        delete_item.addWidget(delete_asset_button, 1, 1, 1, 5)
        self.remove_asset_box.setLayout(delete_item)

        delete_asset_button.clicked.connect(WidgetGallery.remove_asset)

    def current_asset_table(self):
        self.asset_table_box = QTabWidget()
        self.asset_table_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)

        cursor.execute("select * from startupfinancials.capex;")
        current_asset = cursor.fetchall()

        current_row = (len(current_asset))

        current_tab = QWidget()
        current_size = QTableWidget(current_row, 7)
        current_size.setHorizontalHeaderLabels(["Asset\n#", "Asset Name","Asset Category", "Purchase\nCost", "Purchase\nMonth", "Purchase\nYear", "Asset\nLife"])
        current_size.setColumnWidth(0, 60)
        current_size.setColumnWidth(1, 200)
        current_size.setColumnWidth(2, 200, )
        current_size.setColumnWidth(3, 100)
        current_size.setColumnWidth(4, 80)
        current_size.setColumnWidth(5, 80)
        current_size.setColumnWidth(6, 70)
        current_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        current_table = QHBoxLayout()
        current_table.setContentsMargins(5, 5, 5, 5)
        current_table.addWidget(current_size)
        current_tab.setLayout(current_table)

        cursor.execute("select Year, Month, format(sum(NetValue),2), format(sum(BookValue),2), format(sum(Depr),2) from startupfinancials.bookvalue group by Year, Month order by Year, Month;")
        current_sum_depr = cursor.fetchall()

        depr_sum_row = (len(current_sum_depr))

        expense_sum_tab = QWidget()
        expense_sum_size = QTableWidget(depr_sum_row, 5)
        expense_sum_size.setHorizontalHeaderLabels(["Year", "Month", "Net\nValue", "Book\nValue", "Monthly\nDepreciation"])
        expense_sum_size.setColumnWidth(0, 70)
        expense_sum_size.setColumnWidth(1, 70)
        expense_sum_size.setColumnWidth(2, 120)
        expense_sum_size.setColumnWidth(3, 120)
        expense_sum_size.setColumnWidth(4, 120)
        expense_sum_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        expense_sum_table = QHBoxLayout()
        expense_sum_table.setContentsMargins(5, 5, 5, 5)
        expense_sum_table.addWidget(expense_sum_size)
        expense_sum_tab.setLayout(expense_sum_table)

        cursor.execute("select startupfinancials.bookvalue.Year, startupfinancials.bookvalue.Month, startupfinancials.capex.Category, format(sum(startupfinancials.bookvalue.NetValue),2), format(sum(startupfinancials.bookvalue.BookValue),2), format(sum(startupfinancials.bookvalue.Depr),2) FROM startupfinancials.bookvalue INNER JOIN startupfinancials.capex On startupfinancials.bookvalue.AssetID = startupfinancials.capex.AssetID group by startupfinancials.bookvalue.Year, startupfinancials.bookvalue.Month, startupfinancials.capex.Category order by Category, Year, Month;")

        category_sum_depr = cursor.fetchall()

        category_sum_row = (len(category_sum_depr))

        category_sum_tab = QWidget()
        category_sum_size = QTableWidget(category_sum_row, 6)
        category_sum_size.setHorizontalHeaderLabels(["Year", "Month", "Category", "Net\nValue", "Book\nValue", "Monthly\nDepreciation"])
        category_sum_size.setColumnWidth(0, 70)
        category_sum_size.setColumnWidth(1, 70)
        category_sum_size.setColumnWidth(2, 200)
        category_sum_size.setColumnWidth(3, 120)
        category_sum_size.setColumnWidth(4, 120)
        category_sum_size.setColumnWidth(5, 120)
        category_sum_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        category_sum_table = QHBoxLayout()
        category_sum_table.setContentsMargins(5, 5, 5, 5)
        category_sum_table.addWidget(category_sum_size)
        category_sum_tab.setLayout(category_sum_table)


        cursor.execute("select AssetID, Month, Year, format(NetValue,2), format(BookValue,2), format(Depr,2) from startupfinancials.bookvalue;")
        current_depr = cursor.fetchall()

        depr_row = (len(current_depr))

        expense_tab = QWidget()
        expense_size = QTableWidget(depr_row, 6)
        expense_size.setHorizontalHeaderLabels(["Asset #", "Month", "Year", "Net\nValue", "Book\nValue", "Monthly\nDepreciation"])
        expense_size.setColumnWidth(0, 75)
        expense_size.setColumnWidth(1, 60)
        expense_size.setColumnWidth(2, 60)
        expense_size.setColumnWidth(3, 150)
        expense_size.setColumnWidth(4, 150)
        expense_size.setColumnWidth(5, 150)
        expense_size.setEditTriggers(QAbstractItemView.NoEditTriggers)

        expense_table = QHBoxLayout()
        expense_table.setContentsMargins(5, 5, 5, 5)
        expense_table.addWidget(expense_size)
        expense_tab.setLayout(expense_table)

        self.asset_table_box.addTab(current_tab, " Fixed Asset List")
        self.asset_table_box.addTab(expense_sum_tab, " Total Monthly Depreciation")
        self.asset_table_box.addTab(category_sum_tab, "Monthly Depreciation by Category")
        self.asset_table_box.addTab(expense_tab, " Detailed Monthly Depreciation")

        for row_number, row_data in enumerate(current_asset):
            for column_number, data in enumerate(row_data):
                current_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(current_sum_depr):
            for column_number, data in enumerate(row_data):
                expense_sum_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(category_sum_depr):
            for column_number, data in enumerate(row_data):
                category_sum_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(current_depr):
            for column_number, data in enumerate(row_data):
                expense_size.setItem(row_number, column_number, QTableWidgetItem(str(data)))

if __name__ == '__main__':
    ex = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setGeometry(100, 100, 1500, 900)
    gallery.show()
    sys.exit(ex.exec_())

cursor.close()
db.close()
