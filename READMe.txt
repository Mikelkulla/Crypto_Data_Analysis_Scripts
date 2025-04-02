Date 01-04-2025
Made some changes.
Added interaction with google sheets.
    - Fetches coin id's from the google sheet
    - 


In this project i will be creating scripts that i will integrate with the GOOGLE SHEETS API in the future

Structure
    - coin_chart_price.py -> This file contains funtions to:
        - get_beta -> 
                Fetches historical price data for Benchmark(default='bitcoin') and another token from CoinGecko,
                calculates daily returns, and computes the beta of the token compared to BTC.

                Parameters:
                    token_coin (str): The token symbol (e.g., "aave", "ethereum").
                    benchmark (str): Benchmark the token is compared to (default: 'bitcoin')
                    days (int): Number of past days to fetch data for (default: 365) which is the max of the Demo API.

                Returns:
                    tuple: (DataFrame with prices and returns, beta value)

    - main.py -> This file contains the main logic

    - secret.py -> This file contains sensitive information like API_TOKEN etc.

CoinGecko :
    Google Sheet Coins List
        - https://docs.google.com/spreadsheets/d/1y8s0dwDxLSoJR3GzyW2fvaV6GirnEu1jJUrJPrHXLao/edit?gid=0#gid=0
        - You should find the id of the token
    API Dashboar
        - https://www.coingecko.com/en/developers/dashboard
        - Account: mikelccai@gmail.com
        - https://grok.com/share/bGVnYWN5_6e419654-3061-4635-ad6b-bcc0dcb7d958