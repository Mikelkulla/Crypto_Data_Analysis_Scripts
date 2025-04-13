import requests
from datetime import datetime, timedelta
from googlesheets_function import write_to_google_sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration
CREDENTIALS_FILE = "credentials.json"  # Path to your Google credentials file
SPREADSHEET_NAME = "historical_prices_daily"  # Name of the Google Sheet
MAX_LIMIT = 300  # Coinbase API limit per request (max 300 candles)

def get_coinbase_crypto_ohlc(symbol='ETH', days=6000):
    """
    Fetch OHLC data for multiple days from Coinbase API with pagination.
    Writes to Google Sheets by calling the write_to_google_sheet() function.

    Can fetch prices for all historical dates from the beginning of the
    time series. This is the currently used method for fetching prices for
    a new coin until today.

    After using this script, consider setting up automation (e.g., Google Apps Script)
    to fetch daily OHLC every day by triggering at a given time.
    """
    try:
        # Ensure symbol ends with USD (Coinbase uses ETH-USD, SOL-USD, etc.)
        
        if not symbol.upper().endswith('USD'):
            symbol = symbol.upper() + '-USD'
        
        # Calculate start and end times
        now_utc = datetime.utcnow()
        end_time = now_utc.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_time = end_time - timedelta(days=days)
        
        # Coinbase API requires ISO 8601 format for timestamps
        start_time_iso = start_time.isoformat()
        end_time_iso = end_time.isoformat()
        
        # Calculate number of requests needed
        total_requests = (days + MAX_LIMIT - 1) // MAX_LIMIT  # Ceiling division
        all_candles = []
        
        for i in range(total_requests):
            # Calculate time range for this chunk
            chunk_start = start_time + timedelta(days=i * MAX_LIMIT)
            chunk_end = min(chunk_start + timedelta(days=MAX_LIMIT - 1), end_time)
            
            # Convert to ISO 8601
            chunk_start_iso = chunk_start.isoformat()
            chunk_end_iso = chunk_end.isoformat()
            
            # Coinbase API endpoint for this chunk
            candles_url = (
                f"https://api.exchange.coinbase.com/products/{symbol}/candles?"
                f"granularity=86400&"  # 86400 seconds = 1 day
                f"start={chunk_start_iso}&end={chunk_end_iso}"
            )
            
            # Fetch candles data
            print(f"Fetching chunk {i + 1}/{total_requests} for {symbol}...")
            candles_response = requests.get(candles_url)
            candles_response.raise_for_status()
            candles_data = candles_response.json()
            
            if candles_data:  # Only extend if data is returned
                all_candles.extend(candles_data)
        
        # Sort candles by timestamp (Coinbase returns in descending order)
        all_candles.sort(key=lambda x: x[0])  # Sort by timestamp (ascending)
        
        # Prepare data for Google Sheets
        sheet_data = [["Date", "Open", "High", "Low", "Close", "Volume (USDT)"]]  # Header
        for candle in all_candles:
            timestamp = candle[0]  # Unix timestamp in seconds
            date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
            low = float(candle[1])      # Low
            high = float(candle[2])     # High
            open_price = float(candle[3])  # Open
            close = float(candle[4])    # Close
            volume = float(candle[5])   # Volume * Close price for USD value
            
            row = [date, open_price, high, low, close, volume]
            sheet_data.append(row)
        
        # Write to Google Sheet
        write_to_google_sheet(
            spreadsheet_name=SPREADSHEET_NAME,
            data=sheet_data,
            target_sheet=symbol.replace('-USD', 'USDT'),  # Use base symbol (e.g., ETH) as worksheet name
            range_name=f"A1:F{len(sheet_data)}"
        )
        
        return sheet_data[1:]  # Return data without header
    
    except Exception as e:
        print(f"Error fetching OHLC for {symbol}: {e}")
        error_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        error_row = [[error_date, f"Error: {e}", "", "", "", ""]]
        write_to_google_sheet(
            spreadsheet_name=SPREADSHEET_NAME,
            data=error_row,
            target_sheet=symbol.replace('-USD', '')
        )
        return error_row

def main():
    # Configuration
    # SYMBOL = "GAL"  # Crypto symbol (will append USD if needed)
    DAYS = 6000  # Number of days to fetch
    symbols_list = ['GAL']
    for symbol in symbols_list:
        # Fetch and write OHLC data
        result = get_coinbase_crypto_ohlc(
            symbol=symbol,
            days=DAYS
        )
        
        if result and len(result[0]) > 1:  # Check if data was successfully fetched
            print(f"Successfully fetched and wrote {DAYS} days of OHLC data for {symbol}-USD")
        else:
            print(f"Failed to fetch OHLC data for {symbol}-USD")
            print(result)

if __name__ == "__main__":
    main()