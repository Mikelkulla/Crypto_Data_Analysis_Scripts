# beta_compared_to_benchmark.py

import pandas as pd
import requests
from datetime import datetime
from scipy.stats import linregress  # For beta calculation
from secret import CIONGECKO_API_TOKEN
import time

def get_coin_historical_prices(days, coin, retries = 5):
        """Fetches historical prices for a given coin from CoinGecko API."""
        api_url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
        params = {
            "days": days,
            "vs_currency": "usd",
            "interval": "daily"
        }
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": CIONGECKO_API_TOKEN
        }

        for attempt in range(retries):
            try:
                response = requests.get(api_url, params=params, headers=headers)
                response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
                data = response.json()
                print(data)
                # Check if "prices" key exists and has data
                if "prices" not in data or not data["prices"]:
                    raise ValueError(f"No price data returned for {coin}")

                # Convert timestamp to date and store prices
                prices = {datetime.utcfromtimestamp(p[0] / 1000).strftime('%Y-%m-%d'): p[1] for p in data["prices"]}
                return prices

            except (requests.RequestException, ValueError) as e:
                print(f"Error fetching prices for {coin} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:  # If not the last attempt
                    delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Max retries reached for {coin}. Skipping.")
                    return None

def get_beta(token_coin, benchmark = "bitcoin", days=365, max_retries=5):
    """
    Fetches historical price data for Bitcoin and another token from CoinGecko,
    calculates daily returns, and computes the beta of the token compared to BTC.

    Parameters:
        token_coin (str): The token symbol (e.g., "aave", "ethereum").
        benchmark (str): Benchmark the token is compared to (default: 'bitcoin').
        days (int): Number of past days to fetch data for (default: 365).
        max_retries (int): Maximum number of retries for failed API calls (default: 3).

    Returns:
        tuple: (DataFrame with prices and returns, beta value) or (None, None) on failure.
    """
    print(f'Getting beta for {token_coin}...')

    # Fetch prices for benchmark (BTC) and token with error handling
    btc_prices = get_coin_historical_prices(days, benchmark, retries=max_retries)
    if btc_prices is None:
        print(f"Failed to fetch {benchmark} prices. Aborting beta calculation for {token_coin}.")
        return token_coin, None

    token_prices = get_coin_historical_prices(days, token_coin, retries=max_retries)
    if token_prices is None:
        print(f"Failed to fetch {token_coin} prices. Aborting beta calculation.")
        return token_coin, None

    # Ensure both coins have the same dates
    common_dates = set(btc_prices.keys()) & set(token_prices.keys())
    if not common_dates:
        print(f"No common dates found between {benchmark} and {token_coin}. Aborting.")
        return None, None
    common_dates = sorted(common_dates)  # Sort dates in ascending order
    # Create a DataFrame
    df = pd.DataFrame({
        "Time": common_dates,
        "BTC_Price": [btc_prices[date] for date in common_dates],
        "Coin_Price": [token_prices[date] for date in common_dates]
    })

    # Convert Time column to datetime
    df["Time"] = pd.to_datetime(df["Time"])

    # Calculate daily returns
    df["BTC_Return"] = df["BTC_Price"].pct_change()
    df["Coin_Return"] = df["Coin_Price"].pct_change()

    # Drop NaN values (first row will be NaN due to pct_change)
    df.dropna(inplace=True)

    # Compute beta using linear regression (Slope = Beta)
    slope, _, _, _, _ = linregress(df["BTC_Return"], df["Coin_Return"])
    beta = slope
    print(f'Beta calculated for {token_coin}...')
    return df, beta

if __name__ == "__main__":
    # Test with one coin
    df, beta = get_beta("dogecoin")
    if df is not None:
        print(df.head())
        print(f"Beta: {beta}")
