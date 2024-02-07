import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load credentials from environment variables
SCOPES =['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

service_account_info = json.loads(json.dumps({
    "type": "service_account",
    "project_id": "cyberbmo",
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets-458%40cyberbmo.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}))

credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# Use credentials to create a service object
service = build('sheets', 'v4', credentials=credentials)

def appendRow(spreadsheetId, sheet, row):
    print(service.spreadsheets().values())
    print(spreadsheetId, sheet, row)
    request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId,
        range=sheet,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]}
    )
    response = request.execute()
