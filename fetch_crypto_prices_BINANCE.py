import requests
from datetime import datetime, timedelta
from googlesheets_function import write_to_google_sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration
BINANCE_API_KEY = "your_binance_api_key_here"  # Optional, replace if you have one
CREDENTIALS_FILE = "credentials.json"  # Path to your Google credentials file
SPREADSHEET_NAME = "Beta Scores First Test"  # Name of the Google Sheet
MAX_LIMIT = 1000  # Binance API limit per request

def get_binance_crypto_ohlc(symbol='ETH', api_key=None, days=6000):
    """
    Fetch OHLC data for multiple days from Binance API with pagination. 
    Writes to google sheets by calling the write_to_google_sheet() function

    Can fetch prices for all the historical dates from the begining of the
    time series. This is the currently used method for fetching prices for 
    a new coin until today.

    After using this script don't forget to activate the Google Apps Scripts
    to fetch daily OHLC everyday by trigering at a given time
    """
    try:
        # Ensure symbol ends with USDT
        if not symbol.upper().endswith('USDT'):
            symbol = symbol.upper() + 'USDT'
        
        # Calculate start and end times
        now_utc = datetime.utcnow()
        end_time = now_utc.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_time = end_time - timedelta(days=days)
        
        # Convert to milliseconds
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        
        # Calculate number of requests needed
        total_requests = (days + MAX_LIMIT - 1) // MAX_LIMIT  # Ceiling division
        all_klines = []
        
        for i in range(total_requests):
            # Calculate time range for this chunk
            chunk_start_ms = start_time_ms + (i * MAX_LIMIT * 86400 * 1000)  # 86400s = 1 day
            chunk_end_ms = min(chunk_start_ms + (MAX_LIMIT * 86400 * 1000) - 1, end_time_ms)
            
            # Binance API endpoint for this chunk
            klines_url = (
                f"https://data-api.binance.vision/api/v3/klines?"
                f"symbol={symbol}&interval=1d&limit={MAX_LIMIT}&"
                f"startTime={chunk_start_ms}&endTime={chunk_end_ms}"
            )
            
            # Headers with optional API key
            headers = {"X-MBX-APIKEY": api_key} if api_key else {}
            
            # Fetch klines data
            print(f"Fetching chunk {i + 1}/{total_requests} for {symbol}...")
            klines_response = requests.get(klines_url, headers=headers)
            klines_response.raise_for_status()
            klines_data = klines_response.json()
            
            if klines_data:
                all_klines.extend(klines_data)
        
        # Prepare data for Google Sheets
        sheet_data = [["Date", "Open", "High", "Low", "Close", "Volume (USDT)"]]  # Header
        for kline in all_klines:
            timestamp_ms = kline[0]  # Open time in milliseconds
            date = datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
            open_price = float(kline[1])
            high = float(kline[2])
            low = float(kline[3])
            close = float(kline[4])
            volume = float(kline[5]) * float(kline[4])  # Volume * Close price for USDT value
            
            row = [date, open_price, high, low, close, volume]
            sheet_data.append(row)
        
        # Write to Google Sheet
        write_to_google_sheet(
            spreadsheet_name=SPREADSHEET_NAME,
            data=sheet_data,
            target_sheet=symbol,  # Use symbol as worksheet name
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
            target_sheet=symbol
        )
        return error_row

def main():
    # Configuration
    SYMBOL = "SOL"  # Crypto symbol (will append USDT if needed)
    DAYS = 6000  # Number of days to fetch
    
    # Fetch and write OHLC data
    result = get_binance_crypto_ohlc(
        symbol=SYMBOL,
        api_key=BINANCE_API_KEY,
        days=DAYS
    )
    
    if result and len(result[0]) > 1:  # Check if data was successfully fetched
        print(f"Successfully fetched and wrote {DAYS} days of OHLC data for {SYMBOL}USDT")
    else:
        print(f"Failed to fetch OHLC data for {SYMBOL}USDT")
        print(result)

if __name__ == "__main__":
    main()