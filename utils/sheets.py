import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials from environment variables
SCOPES =['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

service_account_info = {
    "type": "service_account",
    "project_id": "cyberbmo",
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your_client_x509_cert_url"
}

credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# Use credentials to create a service object
service = build('sheets', 'v4', credentials=credentials)

async def appendRow(spreadsheetId, sheet, row):
    print(service)
    print(spreadsheetId, sheet, row)
    try:
        request = service.spreadsheets().values().append(
            spreadsheetId=spreadsheetId,
            range=sheet,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [].push(row)}
        )
        print(request)
        response = await request.execute()
        print('re',response)
    except e:
        print(e)
