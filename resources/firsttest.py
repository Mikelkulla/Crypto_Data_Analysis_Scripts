import pandas as pd
import numpy as np
import requests
import xlsxwriter
import math
from scipy import stats
from secret import CIONGECKO_API_TOKEN
from datetime import datetime

date = datetime.now().strftime('%d-%m-%Y')
symbol = 'bitcoin'
api_url = f'https://api.coingecko.com/api/v3/coins/{symbol}/history?date={date}&localization=false'
api_url_multi_tokens = f'https://api.coingecko.com/api/v3/coins/markets?'
params = {
    "date": date,
    "vs_currency": "usd",
    "ids": "bitcoin-cash,near,algorand,axie-infinity,the-graph,aave,floki,project-galaxy,immutable-x,filecoin,blockstack,injective-protocol,lido-dao,gala,curve-dao-token,raydium,conflux-token,thorchain,havven,harmony,woo-network,yield-guild-games"
    }

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": CIONGECKO_API_TOKEN
}

data = requests.get(api_url_multi_tokens, params=params, headers=headers).json()

print(data)
# print(data['market_data']['current_price']['usd'])
# print(data['market_data']['market_cap']['usd'])
# print(data['market_data']['total_volume']['usd'])