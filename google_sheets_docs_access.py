import logging
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import pickle

# Setup logging
logging.basicConfig(level=logging.INFO)

# Function to authenticate and access Google Sheets API
def authenticate_google_sheets():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials are available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            logging.error("Credentials not found or invalid.")
            return None

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Return the service object to access Google Sheets API
    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error in authenticating Google Sheets API: {e}")
        return None

# Function to fetch data from the sheet
def fetch_sheet_data(spreadsheet_id, range_):
    service = authenticate_google_sheets()
    if not service:
        return None

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_).execute()
        values = result.get('values', [])
        if not values:
            logging.error('No data found in the specified range.')
        else:
            logging.info(f"Data fetched successfully: {values}")
        return values
    except Exception as e:
        logging.error(f"Error fetching data from Sheets: {e}")
        return None

if __name__ == '__main__':
    spreadsheet_id = '1IzXe7gYW-EckIx6wPIZJLZGAJA0f_T8El2PydHIotwg'  # Replace with your actual spreadsheet ID
    range_ = 'Sheet1!A1:C10'  # Ensure this range is correct
    sheet_data = fetch_sheet_data(spreadsheet_id, range_)
    
    if sheet_data:
        logging.info(f"Retrieved Sheet Data: {sheet_data}")
