import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def authenticate_google_sheets():
    creds = None
    token_file = os.getenv('TOKEN_FILE')

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('CREDENTIALS_FILE'), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            token.write(creds.to_json().encode())

    return build('sheets', 'v4', credentials=creds)


def read_sheet_data(spreadsheet_id, range_name):
    service = authenticate_google_sheets()

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)


def write_sheet_data(spreadsheet_id, range_name, values):
    service = authenticate_google_sheets()

    body = {
        'values': values
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

    print(f'{result.get("updatedCells")} cells updated.')


if __name__ == '__main__':
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    RANGE_NAME = os.getenv('RANGE_NAME')

    read_sheet_data(SPREADSHEET_ID, RANGE_NAME)

    new_values = [
        ['A', 'B', 'C'],
        ['1', '2', '3'],
        ['4', '5', '6']
    ]
    write_sheet_data(SPREADSHEET_ID, RANGE_NAME, new_values)
