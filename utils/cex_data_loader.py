import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

class CEXDataLoader:

    def __init__(self, start_date: datetime, end_date: datetime):
        # all functions are inclusive of start_date and end_date
        self.start_date = start_date
        self.end_date = end_date
        self.period = (self.end_date - self.start_date).days + 1 # to be inclusive of both dates
        self.exchange_functions = {
            'hitbtc': self.fetch_hitbtc_daily_data,
            'mexc': self.fetch_mexc_daily_data,
            'coinsbit': self.fetch_coinsbit_daily_data,
            'gateio': self.fetch_gateio_daily_data,
            'okx': self.fetch_okx_daily_data,
            'bybit': self.fetch_bybit_daily_data,
            'huobi': self.fetch_huobi_daily_data,
            'bitrue': self.fetch_bitrue_daily_data,
            'dcoin': self.fetch_dcoin_daily_data,
            'azbit': self.fetch_azbit_daily_data,
            'cointr': self.fetch_cointr_daily_data,
            'bitget': self.fetch_bitget_daily_data,
        }
        # default pairs for all exchanges
        self.all_steth_pairs = [
            "STETH/USDT", "STETH/USDC", "STETH/LUSD", "STETH/USD", "STETH/DAI",
            "STETH/BUSD", "STETH/USDP", "STETH/TUSD", "STETH/WBTC", "STETH/BTC",
            "STETH/LDO", "STETH/BTC","STETH/EUR", "STETH/WETH", "STETH/ETH"
        ]
        # specific pairs for exchanges (to override the default list above)
        self.exchange_pairs = {
            'bybit': ["STETH/USDT"]
        }

    def get_data_formated(self, data: pd.DataFrame, pair: str) -> pd.DataFrame: 
        data['symbol'] = pair
        data = data.set_index('date')
        for col in ['open','close','high','low','volume','volume_quote','baseVol' ,'c','o','h','l','vol','v','currencyVol','volumetotal']:
            if col in data.columns:
                if type(data[col].values[0]) == str:
                    data[col] = data[col].str.replace(',','').astype(np.float64)
        return data

    # https://api.hitbtc.com/#candles
    def fetch_hitbtc_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '')
        url = f'https://api.hitbtc.com/api/3/public/candles/{symbol}?period=D1&from={self.start_date}&till={self.end_date}'
        response = requests.get(url)
        if response.status_code == 200:  
            data = pd.DataFrame(json.loads(response.text), columns=['timestamp', 'open', 'close', 'min', 'max', 'volume', 'volume_quote'])
            if data.empty:
                logging.info(f"Did not return any data from HitBTC for {pair}")
                return pd.DataFrame()
            data.rename(columns = {'min':'low', 'max':'high'}, inplace = True)
            data['date'] = pd.to_datetime(data['timestamp']).dt.tz_localize(None) 
            data = self.get_data_formated(data, pair)
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from HitBTC API for {pair}")
            return pd.DataFrame()

    # https://mxcdevelop.github.io/APIDoc/
    def fetch_mexc_daily_data(self, pair: str) -> pd.DataFrame:
        timestamp_from = int(datetime.timestamp(self.start_date))
        symbol = pair.replace('/', '_')
        url = f'https://www.mexc.com/open/api/v2/market/kline?interval=1d&symbol={symbol}&start_time={timestamp_from}&limit={self.period}'
        response = requests.get(url)
        if response.status_code == 200:  
            data = pd.DataFrame(json.loads(response.text)['data'], columns=['timestamp', 'open', 'close', 'high', 'low',  'volume', 'volume_quote'])
            if data.empty:
                logging.info(f"Did not return any data from MEXC for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['timestamp'], unit='s')
            data = self.get_data_formated(data, pair)
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from MEXC API for {pair}")  
            return pd.DataFrame()

    # https://www.notion.so/coinsbitwsapi/API-COINSBIT-WS-API-COINSBIT-cf1044cff30646d49a0bab0e28f27a87
    def fetch_coinsbit_daily_data(self, pair: str) -> pd.DataFrame:
        timestamp_from = int(datetime.timestamp(self.start_date))
        timestamp_to = int(datetime.timestamp(self.end_date))
        symbol = pair.replace('/', '_')
        params = {"market": symbol, "interval": 86400, "start": timestamp_from, "end": timestamp_to}
        url = 'https://coinsbit.io/api/v1/public/kline'
        response = requests.get(url, params=params)
        if response.status_code == 200 and json.loads(response.text)['success'] == True:
            data = pd.DataFrame(json.loads(response.text)['result']['kline'], columns=['time', 'close', 'open', 'highest', 'lowest', 'volume', 'amount', 'market' ])
            if data.empty:
                logging.info(f"Did not return any data from Coinsbit for {pair}")
                return pd.DataFrame()
            data.rename(columns = {'time':'timestamp', 'highest':'high', 'lowest':'low', 'amount':'volume_quote'}, inplace = True)
            data['date'] = pd.to_datetime(data['timestamp'], unit='s')
            data = self.get_data_formated(data, pair)
            return data[['volume']]
        else:
            logging.info("Did not receieve OK response from Coinsbit API for {pair}")  
            return pd.DataFrame()

    # https://www.gate.io/api2#kline
    def fetch_gateio_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '_')
        url = f'https://data.gateapi.io/api2/1/candlestick2/{symbol}?group_sec=86400&range_hour={(datetime.now() - self.start_date).days*24}'
        response = requests.get(url)
        if response.status_code == 200 and len(response.text)>100:  
            data = pd.DataFrame(json.loads(response.text)['data'], columns=["timestamp", "volume", "open", "high", "low", "close"])
            if data.empty:
                logging.info(f"Did not return any data from Gate.io for {pair}")
                return pd.DataFrame()
            data['timestamp'] = data['timestamp'].astype(int)
            data['date'] = pd.to_datetime(data['timestamp'], unit='ms')
            data = self.get_data_formated(data, pair).query('@self.start_date<=index<=@self.end_date')
            data['volume_quote'] = data['volume']*data['close']
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from Gate.io API for {pair}")  
            return pd.DataFrame()

    # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
    def fetch_okx_daily_data(self, pair: str) -> pd.DataFrame:
        # * 1000 to convert to ms, and we need to add 1 more day as the API results is exclusive of end_date
        timestamp_to = (int(datetime.timestamp(self.end_date))+86400) * 1000
        symbol = pair.replace('/', '-')
        url = f'https://www.okx.com/api/v5/market/candles?instId={symbol}&bar=1Dutc&after={timestamp_to}&limit={self.period}'
        response = requests.get(url)
        if response.status_code == 200:
            data = pd.DataFrame(
                json.loads(response.text)['data'],
                columns=['timestamp','open', 'high', 'low', 'close', 'volume', 'volume_currency', 'volume_quote', 'confirm']
            )
            if data.empty:
                logging.info(f"Did not return any data from OKX for {pair}")
                return pd.DataFrame()
            data['timestamp'] = data['timestamp'].astype(int)
            data['date'] = pd.to_datetime(data['timestamp'], unit='ms')
            data['date'] = data['date'].dt.date
            data = self.get_data_formated(data, pair)
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from OKX API for {pair}")  
            return pd.DataFrame()

    # https://www.bybit.com/en/trade/spot/STETH/USDT
    def fetch_bybit_daily_data(self, pair: str) -> pd.DataFrame:
        timestamp_from = int(datetime.timestamp(self.start_date)) * 1000 # as ms
        timestamp_to = int(datetime.timestamp(self.end_date)+86400) * 1000 # as ms
        symbol = pair.replace('/', '')
        params = {
            "symbol": symbol,
            "interval": "1d",
            "limit": (datetime.now() - self.start_date).days + 1,
            "r": round(datetime.now().timestamp() * 1000) # current timestamp in ms
        }
        url = 'https://api2.bybit.com/spot/api/quote/v2/klines'
        response = requests.get(url, params=params)
        if response.status_code == 200 and len(json.loads(response.text)['result']) > 0:
            data = pd.DataFrame(
                json.loads(response.text)['result'],
                columns=['t', 'o', 'h', 'l', 'c', 'v']
            )
            if data.empty:
                logging.info(f"Did not return any data from Bybit for {pair}")
                return pd.DataFrame()
            data['t'] = data['t'].astype(int)
            data['date'] = pd.to_datetime(data['t'], unit='ms')
            data['date'] = data['date'].dt.date
            
            data = self.get_data_formated(data, pair)
            return data[['v']]
        else:
            logging.info(f"Did not receieve OK response from Bybit API for {pair}")  
            return pd.DataFrame()

    # https://huobiapi.github.io/docs/spot/v1/en/#get-klines-candles
    def fetch_huobi_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '').lower()
        params = {"symbol": symbol, "period": "1day", "size": (datetime.now() - self.start_date).days + 1}
        response = requests.get('https://api.huobi.pro/market/history/kline', params=params)
        if response.status_code == 200 and json.loads(response.text)['status'] == 'ok':
            data = pd.DataFrame(json.loads(response.text)['data'])
            if data.empty:
                logging.info(f"Did not return any data from Huobi for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['id'], unit='s')
            data['date'] = data['date'].dt.date
            data.rename(columns = {'amount':'volume', 'vol':'volume_quote'}, inplace = True)
            data = self.get_data_formated(data, pair).query('@self.start_date.date()<=index<=@self.end_date.date()')
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from Huobi API for {pair}")  
            return pd.DataFrame()
        
    #https://github.com/Bitrue-exchange/Spot-official-api-docs#kline_endpoint    
    def fetch_bitrue_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '')
        url = f'https://openapi.bitrue.com/api/v1/market/kline?symbol={symbol}&scale=1D&limit={(datetime.now() - self.start_date).days + 1}'
        response=requests.get(url)
        if response.status_code == 200:
            data = pd.DataFrame(json.loads(response.text)['data'], columns=['is', 'o', 'h', 'l', 'c', 'v'])
            if data.empty:
                logging.info(f"Did not return any data from BiTrue for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['is'],unit='ms').dt.tz_localize(None).dt.date
            data = self.get_data_formated(data, pair) 
            data=data.sort_values(['date'],ascending=False)
            data['volume_quote'] = data['v']*data['c']
            return data[['v']]
        else:
            logging.info(f"Did not receieve OK response from BiTrue API for {pair}")
            return pd.DataFrame()    

    #https://github.com/dcoinapi/openapi/wiki/HttpApi#get-kline-records
    def fetch_dcoin_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '').lower()
        url = f'https://openapi.dcoin.com/open/api/get_records?symbol={symbol}&period=1day&size={(datetime.now() - self.start_date).days + 1}'
        response=requests.get(url)
        if response.status_code == 200:
            data = pd.DataFrame(json.loads(response.text)['data'], columns=['id', 'amount', 'vol', 'open', 'close', 'high', 'low'])
            if data.empty:
                logging.info(f"Did not return any data from DCoin for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['id']*1000,unit='ms').dt.tz_localize(None).dt.date  
            data = self.get_data_formated(data, pair) 
            data=data.sort_values(['date'],ascending=False)
            data['volume_quote_corr'] = 0.5*data['vol']*data['close']
            return data[['vol']]
        else:
            logging.info(f"Did not receieve OK response from DCoin API for {pair}")
            return pd.DataFrame()    

    #https://data.azbit.com/swagger/index.html            
    def fetch_azbit_daily_data(self, pair: str) -> pd.DataFrame:
        symbol = pair.replace('/', '_')
        params = {
            'interval': 'day',
            'currencyPairCode': symbol,
            'start': self.start_date,
            'end': self.end_date + timedelta(days=1) # the API is exclusive of end date, so we must add a day
            }
        url = 'https://data.azbit.com/api/ohlc'
        response=requests.get(url, params=params)
        if response.status_code == 200:
            data = pd.DataFrame(json.loads(response.text), columns=['date', 'open', 'max', 'min', 'close', 'volume', 'volumeBase'])
            if data.empty:
                logging.info(f"Did not return any data from Azbit for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['date']).dt.date
            
            data = self.get_data_formated(data, pair) 
            data=data.sort_values(['date'],ascending=False)
            data['volume_quote'] = data['volume']*data['close']
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from Azbit API for {pair}")
            return pd.DataFrame()             

    #https://cointr-ex.github.io/openapis/spot.html#market-specifications
    def fetch_cointr_daily_data(self, pair: str) -> pd.DataFrame:  
        timestamp_to = int(datetime.timestamp(self.end_date))
        symbol = pair.replace('/', '')
        params = {
            'instId': symbol,
            'bar': '1D',
            'endTs': timestamp_to,
            'limit': self.period 
        }
        url = 'https://api.cointr.pro/v1/spot/market/candlesticks'
        response=requests.get(url, params=params)
        if response.status_code == 200:
            data = pd.DataFrame(json.loads(response.text)['data'], columns=['time', 'open', 'high', 'low','close', 'volume','quotevolume']) 
            if data.empty:
                logging.info(f"Did not return any data from CoinTR for {pair}")
                return pd.DataFrame()
            data['date'] = pd.to_datetime(data['time'], unit='s').dt.tz_localize(None).dt.date  
            data['date'] = pd.to_datetime(data['date']).dt.date     
            
            data = self.get_data_formated(data, pair) 
            data=data.sort_values(['date'],ascending=False)
            data['volume_quote'] = data['volume']*data['close']
            return data[['volume']]
        else:
            logging.info(f"Did not receieve OK response from CoinTR API for {pair}")
            return pd.DataFrame()

    #https://bitgetlimited.github.io/apidoc/en/spot/#get-candle-data
    def fetch_bitget_daily_data(self, pair: str) -> pd.DataFrame:
        timestamp_from = int(datetime.timestamp(self.start_date)) * 1000
        timestamp_to = (int(datetime.timestamp(self.end_date))+86400) * 1000
        symbol = pair.replace('/', '') + '_SPBL'
        params = {
            'symbol': symbol,
            'period': '1day',
            'after': timestamp_from,
            'before': timestamp_to
        }
        url = 'https://api.bitget.com/api/spot/v1/market/candles'
        response=requests.get(url, params=params)
        if response.status_code == 200:
            data = pd.DataFrame(json.loads(response.text)['data'], columns=['open', 'high', 'low','close', 'quoteVol','baseVol', 'usdtVol', 'ts'])
            if data.empty:
                logging.info(f"Did not return any data from BitGet for {pair}")
                return pd.DataFrame()
            data['ts'] = data['ts'].astype(int)
            data['date'] = pd.to_datetime(data['ts'],unit='ms').dt.tz_localize(None).dt.date
            data = self.get_data_formated(data, pair) 
            data=data.sort_values(['date'],ascending=False)
            data['volume_quote'] = data['baseVol']*data['close']
            return data[['baseVol']]
        else:
            logging.info(f"Did not receieve OK response from BitGet API for {pair}")
            return pd.DataFrame()

    def get_klines_by_exchange_pair(self, exchange: str, pair: str) -> pd.DataFrame:
        fetch_func = self.exchange_functions.get(exchange)
        if fetch_func:
            result = fetch_func(pair)
            return result
        else:
            logging.info(f"No data for {exchange}")

    def get_klines(self) -> dict[tuple[str, str], pd.DataFrame]:
        klines_by_exchange = {}
        for exchange in self.exchange_functions.keys():
            if exchange in self.exchange_pairs:
                for pair in self.exchange_pairs[exchange]:
                    klines_by_exchange.update({(exchange, pair): self.get_klines_by_exchange_pair(exchange, pair)})
            else:
                for pair in self.all_steth_pairs:
                    klines_by_exchange.update({(exchange, pair): self.get_klines_by_exchange_pair(exchange, pair)})
        return klines_by_exchange

    def get_trading_volume(self, symbol: str) -> pd.DataFrame:
        timestamp_to = int(datetime.timestamp(self.end_date)) + 86400
        period_required = max(self.period, 91) # for this API endpoint, to return daily data, it requires minimum 90 day period
        timestamp_from = timestamp_to - period_required * 86400
        url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range?vs_currency=usd&from={timestamp_from}&to={timestamp_to}'
        response = requests.get(url)
        if response.status_code == 200: 
            data = pd.DataFrame(json.loads(response.text)['prices'], columns=['timestamp','price'])
            data['date'] = pd.to_datetime(data['timestamp'], unit='ms').dt.date
            data = data[['date', 'price']].set_index('date')
            data_ = pd.DataFrame(json.loads(response.text)['total_volumes'], columns=['timestamp','total_volume_usd'])
            data_['date'] = pd.to_datetime(data_['timestamp'], unit='ms').dt.date
            data_ = data_[['date', 'total_volume_usd']].set_index('date')
            data = pd.merge(data, data_, left_index = True, right_index = True)
            data['total_volume'] = data.total_volume_usd/data.price
            data = data.query('@self.start_date.date()<=index<=@self.end_date.date()')
        return data[['total_volume', 'price']]
    
    def get_offchain_df(self) -> pd.DataFrame:

        # get coingecko price
        steth_trading_volume = self.get_trading_volume('staked-ether')

        # get volume on exchanges 
        stethtot_klines = self.get_klines()
        stethtot_offchain_all = []
        for key in stethtot_klines.keys():
            if stethtot_klines[key].empty == False: 
                k = stethtot_klines[key].copy()
                key1 = (key[0], key[1].replace('STETH/USDT', 'Stablecoins').replace('STETH/USDC', 'Stablecoins').replace('STETH/ETH', '(W)ETH').replace('STETH/BTC', 'Others').replace('STETH/USD', 'Stablecoins'))
                k.columns = [key1]
                stethtot_offchain_all.append(k)

        df_stethtot_offchain = steth_trading_volume.copy()
        for kline in stethtot_offchain_all:
            df_stethtot_offchain = pd.merge(df_stethtot_offchain, kline, how = 'left', left_index = True, right_index = True).fillna(0)

        # remove first 2 columns 'total_volume' and 'price' from index
        cols = df_stethtot_offchain.columns
        cols = cols.delete(0)
        cols = cols.delete(0)
        # multiply other columns (individual exchange+pair volumes) with price
        df_stethtot_offchain[cols] = df_stethtot_offchain[cols].mul(df_stethtot_offchain.price, axis = 0)

        # drop total_volume and price from dataframe
        df_stethtot_offchain.drop(['total_volume', 'price'], axis=1, inplace=True)

        # calculate total volume by summing across row
        df_stethtot_offchain['total_volume'] = df_stethtot_offchain.loc[:,cols].sum(axis=1)

        df_stethtot_offchain = df_stethtot_offchain[['total_volume']]
        df_stethtot_offchain = df_stethtot_offchain.rename(columns = {'total_volume': 'volume'})

        # df_stethtot_offchain.to_csv('df_stethtot_offchain.csv')
        # df_stethtot_offchain = pd.read_csv('df_stethtot_offchain.csv', index_col='date')
        # df_stethtot_offchain.index = pd.to_datetime(df_stethtot_offchain.index)
        return df_stethtot_offchain
