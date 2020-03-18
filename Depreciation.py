import mysql.connector
import config

db = mysql.connector.connect(
    host=config.host_finance,
    user=config.user_finance,
    passwd=config.password_finance,
    database=config.database_finance
)

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS startupfinancials")
cursor.execute("CREATE TABLE IF NOT EXISTS CapEx (ID Int Primary Key, Name Varchar(50) Not Null, Category Varchar (20) Not Null, Cost Decimal(12,2) Not Null, Month Int Not Null, Year Int Not Null, Life Int Not Null)")
cursor.execute("CREATE TABLE IF NOT EXISTS BookValue (ID Int Primary Key, AssetID Int Not Null, Name Varchar(50) Not Null, Month Int Not Null, Year Int Not Null, BookValue Decimal(12,2) Not Null,Depr Decimal(12,2) Not Null)")
db.commit()

month_conversions = {
    "jan" : "1",
    "feb" : "2",
    "mar" : "3",
    "apr" : "4",
    "may" : "5",
    "jun" : "6",
    "jul" : "7",
    "aug" : "8",
    "sep" : "9",
    "oct" : "10",
    "nov" : "11",
    "dec" : "12",
    "january" : "1",
    "february" : "2",
    "march" : "3",
    "april" : "4",
    "june" : "6",
    "july" : "7",
    "august" : "8",
    "september" : "9",
    "october" : "10",
    "november" : "11",
    "december" : "12"
}


def asset_input():
    cursor.execute("select count(ID) from startupfinancials.capex;")
    id_num = cursor.fetchone()[0] + 1
    print("Lets input your assets. Your starting asset # is: " + str(id_num))
    user_input = ""
    while user_input.lower() != "no":
        a_name = input("Asset name: ")
        a_cat = input("Asset category: ")
        a_cost = float(input("Purchase cost: "))
        a_month = month_conversions[input("Purchase month: ").lower()]
        a_year = int(input("Purchase year: "))
        a_life = int(input("Life of the asset in months: "))

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
                val = (depr_id_num, id_num, a_name, depr_month, depr_year, book_value,depr)
                cursor.execute(sql, val)
                db.commit()
                book_value = book_value - depr
                depr_month = depr_month + 1
                depr_id_num = depr_id_num + 1

        id_num = id_num + 1
        user_input = input("Do you have more assets to input (Yes/No): ")


def monthly_result():
    print("Your total monthly values are: ")
    print("Year, Month, Book Value, Depreciation Amount")
    cursor.execute("Select Year, Month, Cast(BookValue as Char) as BookValue, Cast(Depr as Char) as Depr from startupfinancials.bookvalue group by year, month")
    monthly_value = cursor.fetchall()
    for m_v in monthly_value:
        print(m_v)


def current_asset_view():
    print("Your current assets in CapEx table are: ")
    cursor.execute("select Name, Cast(Cost as Char) as Cost, Month, Year, Life from startupfinancials.capex;")
    print("Name, Cost, Purchase Month, Purchase Year, Depreciation Period")
    current_asset = cursor.fetchall()
    for c_a in current_asset:
        print(c_a)

def new_asset_input():
    new_input = input("Do you want to add new assets to your list: ").lower()
    if new_input == "yes":
        asset_input()
        monthly_results_request = input("Thank you for adding your new assets. Would you like to see your monthly book values and depreciation amounts: ")
        if monthly_results_request.lower() == 'yes':
            monthly_result()
            print("Thank you for your inputs!")
        else:
            print("Thank you for your inputs!")
    else:
        monthly_results_request = input("Would you like to see your monthly book values and depreciation amounts: ")
        if monthly_results_request.lower() == 'yes':
            monthly_result()
            print("Thank you!")
        else:
            print("Thank you!")


cursor.execute("Select count(*) from startupfinancials.capex")
monthly_value = cursor.fetchone()
a = monthly_value[0]
if a == 0:
    print("There isn't any asset in the CapEx table right now.")
elif a == 1:
    user_input_current = input("There is one asset in the CapEx table. Would you like to view the asset: ")
    if user_input_current.lower() == "yes":
        current_asset_view()
else:
    user_input_current = input("There are " + str(a) + " assets in CapEx table. Would you like to view them: ")
    if user_input_current.lower() == "yes":
        current_asset_view()

new_asset_input()

cursor.close()
db.close()
