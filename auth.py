from database import insert_data, create_table
from google_sheets import read_sheet_data


def sync_google_sheets_with_db():
    create_table()

    sheet_data = read_sheet_data()

    if sheet_data:
        header = sheet_data[0]
        sheet_data = sheet_data[1:]

        print(f"Google Sheet Columns: {header}")

        insert_data(sheet_data)
        print("Data from Google Sheets inserted into PostgreSQL.")


if __name__ == '__main__':
    sync_google_sheets_with_db()
