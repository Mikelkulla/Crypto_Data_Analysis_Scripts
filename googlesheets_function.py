# google_sheets_writer.py
import pandas as pd
import gspread  # Library to interact with Google Sheets
from oauth2client.service_account import ServiceAccountCredentials  # Handles authentication with Google APIs

def get_coin_list_from_google_sheet(spreadsheet_name, credentials_file = 'credentials.json', coins_sheet='Coins' ):
    """Fetch coin IDs from a Google Sheet."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(coins_sheet)
    
    # Get all values in column A, starting from A2 (assuming A1 is a header)
    coins = sheet.col_values(1)[1:]  # Skip header row
    return [coin for coin in coins if coin]  # Filter out empty cells

def write_to_google_sheet(spreadsheet_name, data, target_sheet=None, range_name=None, credentials_file='credentials.json'):
    """
    Write data to a specific sheet and range in a Google Sheet document.
    
    Parameters:
    - spreadsheet_name (str): The name of the Google Sheet document (e.g., "Beta Scores First Test").
    - data (list of lists): The data to write, where each inner list is a row (e.g., [["Hello", "World", 4]]).
    - target_sheet (str or int, optional): The name (e.g., "Sheet2") or index (e.g., 1) of the specific sheet/tab.
                                          If None, defaults to the first sheet.
    - range_name (str, optional): The range to write to in A1 notation (e.g., "A1:C2"). 
                                  If None, data is appended as new rows.
    - credentials_file (str): Path to the JSON credentials file downloaded from Google Cloud (default: 'credentials.json').
    """
    # Define the scope of access for the Google Sheets and Drive APIs
    # These URLs specify what permissions the script needs (read/write sheets and access Drive)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load the service account credentials from the JSON file
    # The JSON file contains the private key and client email for authentication
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)

    # Authorize the client using the credentials
    # This creates an authenticated connection to Google APIs
    client = gspread.authorize(creds)

    # Open the Google Sheet document by its name
    # This returns a Spreadsheet object representing the entire document (all its sheets)
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        spreadsheet.share('jira.test.mikel@gmail.com', perm_type='user', role='writer')
        print(f"Created new spreadsheet: {spreadsheet_name}")

    # Determine which specific sheet (tab) within the document to write to
    if target_sheet is None:
        # If no specific sheet is provided, default to the first sheet in the document
        sheet = spreadsheet.sheet1
    elif isinstance(target_sheet, int):
        # If target_sheet is an integer, treat it as a 0-based index
        # get_worksheet(0) gets the first sheet, get_worksheet(1) gets the second, etc.
        sheet = spreadsheet.get_worksheet(target_sheet)
    else:
        try:
            sheet = spreadsheet.worksheet(target_sheet)
        except gspread.exceptions.WorksheetNotFound:
            # If the specified worksheet doesn't exist, create it
            sheet = spreadsheet.add_worksheet(title=target_sheet, rows=10000, cols=20)
            print(f"Created new worksheet: {target_sheet} in {spreadsheet_name}")

    # Check if a specific range is provided
    if range_name:
        # Write data to the specified range (e.g., "A1:C2")
        # The data must match the size of the range (rows and columns)
        # For example, "A1:C2" expects 2 rows and 3 columns of data
        sheet.update(range_name, data)
        sheet.format(f"A1:A{len(data)}", {"numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}})
        print(f"Data written successfully to '{sheet.title}' in {spreadsheet_name} at range {range_name}!")
    else:
        # If no range is specified, append the data as new rows
        # This adds the data starting at the first empty row in the sheet
        sheet.append_rows(data)
        sheet.format(f"A1:A{len(data)}", {"numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}})
        print(f"Data appended successfully to '{sheet.title}' in {spreadsheet_name}!")

def get_coin_historical_prices_from_google_sheets(spreadsheet_name, coin = 'BTC', credentials_file='credentials.json'):
    """
    Fetch historical price data for a specific coin from a Google Sheet named '{coin}USDT'.
    Reminder! The coin should exists in the google sheet coins list.
    
    Parameters:
    - coin (str): The coin symbol (e.g., "BTC" for Bitcoin)
    - sheet_name (str): The name of the Google Sheet document containing the coin sheets
    - credentials_file (str): Path to the JSON credentials file (default: 'credentials.json')
    
    Returns:
    - pandas.DataFrame: Historical price data with columns:
                        ['Date', 'Open', 'High', 'Low', 'Close', 'Volume (USDT)']
    """
    # Define the scope for Google Sheets and Drive APIs
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load and authorize credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    
    # Open the main spreadsheet
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Spreadsheet '{spreadsheet_name}' not found!")
        return pd.DataFrame()  # Return empty DataFrame
    
    # Construct the coin-specific sheet name
    coin_sheet_name = f"{coin}USDT"
    
    # Try to access the coin-specific sheet
    try:
        sheet = spreadsheet.worksheet(coin_sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{coin_sheet_name}' not found in '{spreadsheet_name}'!")
        return pd.DataFrame()  # Return empty DataFrame
    
    # Get all data from the sheet
    data = sheet.get("A:F")
    
    # Check if there's any data
    if not data or len(data) < 2:  # Less than 2 rows means no data beyond header
        print(f"No data found in '{coin_sheet_name}'!")
        return pd.DataFrame()  # Return empty DataFrame
    
    # Create DataFrame directly from data
    df = pd.DataFrame(data[1:], columns=data[0])    

    # Verify expected headers
    expected_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume (USDT)']
    if list(df.columns) != expected_columns:
        print(f"Warning: Columns in '{coin_sheet_name}' do not match expected format: {expected_columns}")

    # Convert numeric columns to float
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume (USDT)']
    try:
        df[numeric_columns] = df[numeric_columns].astype(float)
    except ValueError as e:
        print(f"Error converting numeric columns to float: {e}")
        # # Optionally, you could drop rows with invalid data here
        # df = df[pd.to_numeric(df['Open'], errors='coerce').notna()]
        # df[numeric_columns] = df[numeric_columns].astype(float)
    
    print(f"Successfully retrieved {len(df)} price entries for {coin}")
    return df


# This block allows the file to be run directly for testing, but won’t execute when imported as a module
if __name__ == "__main__":
    # # Sample data for testing: two rows with three columns each
    # test_data = [["Hello", "World", 4], ["Hi", "There", 5]]
    
    # # Test writing to a specific range ("A1:C2") in "Sheet2"
    # write_to_google_sheet("Beta Scores First Test", test_data, target_sheet="Sheet2", range_name="A1:C2")
    
    # # Test appending data (no range specified)
    # # write_to_google_sheet("Beta Scores First Test", test_data, target_sheet="Sheet2")
    
    
    # ========================================================================================
    # Test get_coin_historical_prices_from_google_sheets with a sample coin
    coin = "BTC"
    spreadsheet_name = "Beta Scores First Test"
    prices_df = get_coin_historical_prices_from_google_sheets(spreadsheet_name, coin)
    
    # Print the first few entries if data exists
    if not prices_df.empty:
        print(f"First 3 price entries for {coin}:")
        print(prices_df)
