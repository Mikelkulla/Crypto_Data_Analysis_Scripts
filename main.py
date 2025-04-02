from beta_compared_to_benchmark import get_beta, get_coin_historical_prices
from googlesheets_function import write_to_google_sheet, get_coin_list_from_google_sheet
import time
from datetime import datetime  # Import datetime for current timestamp
# List of coins to analyze
# coins_list = [
#     "dogecoin", "cardano", "render-token", "avalanche-2", "chainlink",
#     "bitcoin-cash", "near", "algorand", "axie-infinity", "the-graph",
#     "aave", "floki", "project-galaxy", "immutable-x", "filecoin",
#     "blockstack", "injective-protocol", "lido-dao", "gala",
#     "curve-dao-token", "raydium", "conflux-token", "thorchain",
#     "havven", "harmony", "woo-network", "yield-guild-games"
# ]


SPREADSHEET_NAME = 'Beta Scores First Test'
COINS_SHEET_NAME = 'Coins'
TARGET_SHEET_NAME = 'Beta Table'
RANGE_NAME = 'F4:G'
CREDENTIALS_FILE = "credentials.json"
BENCHMARK = ['bitcoin', 'BTC']

def fetch_beta_scores_to_google_sheet(SPREADSHEET_NAME = 'Beta Scores First Test', COINS_SHEET_NAME = 'Coins', TARGET_SHEET_NAME = 'Beta Table', RANGE_NAME = 'F4:G', CREDENTIALS_FILE = "credentials.json", BENCHMARK = ['bitcoin', 'BTC']):
    """
    This function fetches Coins from google sheets lists in a sheet, use each coin ID to fetch price
    from CoinGecko API for max 365 days
    
    Parameters:
    - SPREADSHEET_NAME = 'Beta Scores First Test'
    - COINS_SHEET_NAME = 'Coins'
    - TARGET_SHEET_NAME = 'Beta Table'
    - RANGE_NAME = 'F4:G'
    - CREDENTIALS_FILE = "credentials.json"
    - BENCHMARK = ['bitcoin', 'BTC']
    
    - get_coin_list_from_google_sheet()
    - get_beta() -> For each coin
    - write_to_google_sheet() -> Write the beta calculated for each coin to a google sheet
    """

    # Fetch coin IDs from Google Sheet
    coins_list = get_coin_list_from_google_sheet(SPREADSHEET_NAME, CREDENTIALS_FILE, COINS_SHEET_NAME)
    print(f"Fetched coins: {coins_list}")

    # Fetch beta values for each coin with rounding to 4 decimal places
    coins_beta = [(coin, round(float(get_beta(coin,BENCHMARK[0])[1]), 4)) for coin in coins_list]
    print(f"Beta values (raw): {coins_beta}")

    # Get current datetime as a string
    current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Prepare data with headers
    beta_data = [
        ["Updated", current_datetime],  # Header row with timestamp
        ["Coin", f"Beta/{BENCHMARK[1]} "]               # Column headers for data
    ] + [[coin, beta] for coin, beta in coins_beta]  # Data rows

    print(f"Beta data with headers: {beta_data}")

    # Write beta values to Google Sheet starting at A1 (to include headers)
    print('Trying to write to google sheets...')
    write_to_google_sheet(
        spreadsheet_name = SPREADSHEET_NAME,
        data = beta_data,
        target_sheet = TARGET_SHEET_NAME,
        range_name= RANGE_NAME  # Adjust range to include headers
    )
    print('Successfully writen to google sheets.')

def fetch_token_historical_prices_to_googlesheets(): # Deprecated as it uses CoinGecko API
    """
    Fetch coin historical data for max 365 days from CoinGecko API and writes them to a google sheet. 
    This function is deprecated since we started using Binance API that can fetch all historical prices.
    """
    # Configuration
    DAYS = 365  # Number of days of historical data
    COIN = ["ethereum",  "ETH"]  # Coin to fetch prices for (use CoinGecko ID)
    CREDENTIALS_FILE = "credentials.json"  # Path to your Google credentials file
    
    # Use the coin name as the sheet name
    TARGET_SHEET_NAME = f"{COIN[1]}USDT"
    
    # Fetch historical prices
    prices = get_coin_historical_prices(DAYS, COIN[0])
    
    if prices:
        # Prepare data for Google Sheets
        sheet_data = [["Date", "Price"]]  # Header row
        for date, price in sorted(prices.items()):
            sheet_data.append([date, price])
        
        try:
            # Write data to Google Sheet, create if it doesn't exist
            write_to_google_sheet(
                sheet_name=SPREADSHEET_NAME,
                data=sheet_data,
                target_sheet=TARGET_SHEET_NAME,  # Default first sheet
                range_name="A1:B" + str(len(sheet_data)),
                credentials_file=CREDENTIALS_FILE
            )
        except Exception as e:
            print(f"Error writing to Google Sheet: {e}")
    else:
        print("Failed to fetch price data. Check coin ID and API token.")

if __name__ == "__main__":
    fetch_beta_scores_to_google_sheet('Beta Scores First Test', 'Coins', 'Beta Table', 'F4:G', "credentials.json", ['bitcoin', 'BTC'])
    # fetch_token_historical_prices_to_googlesheets()
    pass
"""
Until now i have just fetched the prices of the coins from the API and calculated the beta for each of them compared to the benchmark
To do:
    - Fetch the Coins IDs from a GOOGLE SHEETS sheet
    - Paste the beta calculated values to a GOOGLE SHEETS sheet through the googlesheets api.
    - Try to use FLASK to triger scripts from the GOOGLE APPS SCRIPT
    - Automating the process of calcuating beta scores for trash tokens

Project Path:
    - f"C:\\Users\\MikelKulla\\OneDrive - CData Software\\Documents\\Crypto\\Quantitative Momentum Strategy"
    - Don't forget to activate the VENV before executing scripts
"""