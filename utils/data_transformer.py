import pandas as pd
from datetime import datetime, timedelta
from utils.cex_data_loader import CEXDataLoader
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

class DataTransformer:

    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        # the enrich functions enrich dune data with additional off-chain data where applicable
        self.enrich_functions = {
            "stethVolumes": DataTransformer.enrich_stethVolumes
        }
        # the processing functions is after enrichment
        # it takes in the enriched dataframe and produces a string, to be used in the prompt
        self.process_functions = {
            "tvl": DataTransformer.process_tvl,
            "netDepositGrowthLeaders": DataTransformer.process_netDepositGrowthLeaders,
            "stETHApr": DataTransformer.process_stETHApr,
            "stEthToEth": DataTransformer.process_stEthToEth,
            # "dexLiquidityReserves": DataTransformer.process_dexLiquidityReserves,
            "bridgeChange": DataTransformer.process_bridgeChange,
            "totalStEthInDeFi": DataTransformer.process_totalStEthInDeFi,
            "bridgedToCosmos": DataTransformer.process_bridgedToCosmos,
            "stethVolumes": DataTransformer.process_stethVolumes
        }


    def enrich_stethVolumes(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        # on-chain section (dune)
        df['date'] = pd.to_datetime(df['day']).dt.date
        df = df[['date','chain','volume']].groupby(['date','chain']).agg({'volume': ['sum']}).reset_index()
        df.columns = ['date', 'chain', 'volume']
        chainlist = []
        for d in df['chain']:
            if d not in chainlist:
                chainlist.append(d)
        tv_by_chain = {}
        for chain in chainlist:
            tv_by_chain.update({(chain): df.query('chain==@chain')[['date','volume']].set_index('date')})
        
        stethtot_klines_chain = []
        for key in tv_by_chain.keys():
            if tv_by_chain[key].empty == False: 
                k = tv_by_chain[key].copy()
                k.columns = [key]
                stethtot_klines_chain.append(k)
    
        # off-chain section (exchange APIs)

        # first we need to extend the start date to include 1 more period before
        # e.g. if start_date = 2024-04-29 and end_date = 2024-05-05, we want to have extended_start_date = 2024-04-22
        # we need this to calculate the values for 1 week before, so we can say, the values rose / drop by X%
        period = (end_date - start_date).days + 1
        extended_start_date = end_date - timedelta(days = 2 * period - 1)
        logging.info(f"Loading offchain CEX data with start date as {extended_start_date} and end date as {end_date}...")
        cex_data_loader = CEXDataLoader(extended_start_date, end_date)
        df_stethtot_offchain = cex_data_loader.get_offchain_df()

        # merge on-chain with off-chain
        df_stethtot_chain = df_stethtot_offchain
        for kline in stethtot_klines_chain:
            df_stethtot_chain = pd.merge(df_stethtot_chain, kline, how = 'left', left_index = True, right_index = True).fillna(0)
        df_stethtot_chain.rename(columns = {'volume': 'off_chain'}, inplace = True)
        df_stethtot_chain.to_csv('df_stethtot_chain.csv')
        # df_stethtot_chain = pd.read_csv('df_stethtot_chain.csv', index_col='date')
        return df_stethtot_chain


    def enrich_dune(self, dune_results: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        res = {}

        for df_name, df in dune_results.items():
            enrich_func = self.enrich_functions.get(df_name)
            if enrich_func is not None:
                res[df_name] = enrich_func(df, self.start_date, self.end_date)
            else:
                res[df_name] = df
        return res

    def process_tvl(df: pd.DataFrame) -> str:
        # Select the row corresponding to 'Total'
        total_row = df[df["chain"] == "Total"]

        # Extract the 'TVL' and 'TVL change, %' from the total row
        total_tvl = total_row["TVL"].values[0]
        total_tvl_change = total_row["TVL change, %"].values[0] * 100

        # Format the total TVL and total TVL change into strings
        total_tvl_str = f"${total_tvl / 1e9:.2f}b"
        total_tvl_change_str = f"{total_tvl_change:.2f}%"

        # Select the rows corresponding to 'Ethereum' and 'Polygon'
        eth_row = df[df["chain"] == "Ethereum"]
        polygon_row = df[df["chain"] == "Polygon"]

        # Extract the 'Token price change, %' from the Ethereum and Polygon rows
        eth_price_change = float(eth_row["Token price change, %"].values[0]) * 100
        polygon_price_change = float(polygon_row["Token price change, %"].values[0]) * 100

        # Format the Ethereum and Polygon price changes into strings
        eth_price_change_str = f"{eth_price_change:.2f}%"
        polygon_price_change_str = f"{polygon_price_change:.2f}%"

        # Combine everything into a result string
        result_string = (
            f"TVL: {total_tvl_str}\n"
            f"TVL Percentage Change: {total_tvl_change_str}\n"
            f"Ethereum Token Price Change: {eth_price_change_str}\n"
            f"Polygon Token Price Change: {polygon_price_change_str}"
        )

        return result_string


    def process_netDepositGrowthLeaders(df: pd.DataFrame) -> str:

        # Find Lido's stats
        lido_stats = df[df["name"] == "Lido"]

        # If Lido is not in the list, return None for both values
        if lido_stats.empty:
            return ""

        lido_net_deposit_growth = round(lido_stats.iloc[0]["eth_deposits_growth"], 0)

        # If net deposit is positive (i.e. more deposits than withdrawals)
        if lido_net_deposit_growth >= 0:
            lido_rank = lido_stats.iloc[0]["eth_deposits_rank"]
            return f"Lido had net deposit growth of {lido_net_deposit_growth} ETH. ETH deposits rank: {lido_rank}"
        # If net deposit is negative
        else:
            lido_rank = lido_stats.iloc[0]["eth_withdrawals_rank"]
            return f"Lido had net unstake of {lido_net_deposit_growth} ETH. ETH unstaking rank: {lido_rank}"

    def process_stETHApr(df: pd.DataFrame) -> str:
        # Sort DataFrame by time in descending order
        df = df.sort_values("time", ascending=False)
        
        # Get the most recent 7d moving average
        recent_7d_ma = df["stakingAPR_ma_7"].values[0]
        week_ago_7d_ma = df["stakingAPR_ma_7"].values[7]

        difference_in_bps = (recent_7d_ma - week_ago_7d_ma) * 10000
        # Format the result into a string
        result_string = f"7d MA: {recent_7d_ma:.2%}, change from 7d ago: {difference_in_bps:.0f}bps"

        return result_string

    def process_stEthToEth(df: pd.DataFrame) -> str:
        # Convert 'time' column to datetime
        df["time"] = pd.to_datetime(df["time"])

        # Sort DataFrame by time in descending order
        df = df.sort_values("time", ascending=False)

        # Get the most recent 'weight_avg_price'
        recent_price = df["weight_avg_price"].iloc[0]

        # Calculate the volatility of the 'weight_avg_price'
        volatility = df["weight_avg_price"].std()

        # Return results as a string
        return f"The week ended with a ratio of {recent_price}. The ratio over the week had a standard deviation of {volatility}"


    def process_dexLiquidityReserves(df: pd.DataFrame) -> str:
        # Select the row corresponding to 'total'
        total_row = df[df["token"] == "total"]

        # Extract the 'end value' and 'period_change' from this row
        end_value = total_row["end value"].values[0]
        period_change = total_row["period_change"].values[0]

        # Format the end value into a string in billions with 2 decimal places
        end_value_str = f"${end_value / 1e9:.0f}b"

        # Format the period change into a string as a percentage with 2 decimal places
        period_change_str = f"{period_change * 100:.2f}%"

        # Combine these into a result string
        result_string = f"Total End Value: {end_value_str}\nPeriod Change: {period_change_str}"

        return result_string


    def process_totalStEthInDeFi(df: pd.DataFrame) -> str:

        # Order the dataframe from oldest to latest
        df = df.sort_values("time")

        # Get the latest row, that is the data at the end_date
        latest_row = df.iloc[-1]

        # Format the changes into a string
        result = (
            f"Liquidity Pools Balance: {latest_row['liquidity_pools_balance']:.0f}\n"
            f"Liquidity Pools Percentage Change: {float(latest_row['liquidity_pct_change']):.2f}%\n"
            f"Lending Pools Balance: {latest_row['lending_pools_balance']:.0f}\n"
            f"Lending Pools Percentage Change: {float(latest_row['lending_pct_change']):.2f}%"
        )

        return result


    def process_stEthOnL2(df: pd.DataFrame) -> str:
        # Select the row corresponding to 'total'
        total_row = df[df["bridge"] == "total"]

        # Extract the 'end_amount' and 'period_change' from the total row
        total_end_amount = total_row["end_amount"].values[0]
        total_period_change = total_row["period_change"].values[0]

        # Format the total end amount and total period change into strings
        total_end_amount_str = f"{round(total_end_amount, 0)} wstETH"
        total_period_change_str = f"{total_period_change:.2f}%"

        # Initialize an empty string to store the individual bridge data
        bridge_data_str = ""

        # Loop over the rows of the DataFrame
        for i, row in df.iterrows():
            # Skip the total row
            if row["bridge"] == "total":
                continue

            # Extract the 'bridge', 'end_amount' and 'period_change' for each row
            bridge = row["bridge"]
            end_amount = row["end_amount"]
            period_change = row["period_change"]

            # Format the end amount and period change into strings
            end_amount_str = f"{end_amount:.0f} wstETH"
            period_change_str = f"{period_change:.2f}%"

            # Append this bridge's data to the bridge data string
            bridge_data_str += f"{bridge}: {end_amount_str} (7d: {period_change_str})\n"

        # Combine the total and bridge data into a result string
        result_string = f"The amount of wstETH on L2 changed by {total_period_change_str}, hitting {total_end_amount_str}:\n\n{bridge_data_str}"

        return result_string


    def process_bridgeChange(df: pd.DataFrame) -> str:
        # Apply rounding logic to the 'period_change' column
        df['period_change'] = df['period_change'].apply(lambda x: round(x, 2))
        df['end_amount'] = df['end_amount'].apply(lambda x: int(round(x, 0)))
        df['start_amount'] = df['start_amount'].apply(lambda x: int(round(x, 0)))

        # Convert the DataFrame to a string
        df_string = df.to_string(index=False)

        return df_string

    def process_bridgedToCosmos(df: pd.DataFrame) -> str:
        # Sort by day
        df = df.sort_values("day")

        # Get values 
        balance = df.iloc[-1]['balance_cumu']
        balance_7d_ago = df.iloc[-8]['balance_cumu']
        pct_change = (balance/balance_7d_ago - 1) * 100

        result_string = f"The balance of wstETH on Cosmos is {balance:.0f}, with a 7d change of {pct_change:.2f}%."

        return result_string
    
    def process_stethVolumes(df: pd.DataFrame) -> str:

        dates = pd.to_datetime(df.index)
        # the df here contains 2 periods. so we need to split into current period and previous period
        min_date = dates.min()
        max_date = dates.max()
        
        period_length = (max_date - min_date + timedelta(days = 1)) / 2
        # this is start_date of current period
        start_date = min_date + period_length
        previous_sum = df[pd.to_datetime(df.index) < start_date].sum().sum()
        current_sum = df[pd.to_datetime(df.index) >= start_date].sum().sum()
        pct_change = (current_sum/previous_sum - 1) * 100

        result_string = (
            f"{period_length.days}d trading volume: ${current_sum}\n"
            f"Previous trading volume: ${previous_sum}\n"
            f"Percentage change: {pct_change}"
        )
        return result_string

    def process_dune(self, dune_results: dict[str, pd.DataFrame]) -> dict[str, str]:
        res = {}

        for df_name, df in dune_results.items():
            process_func = self.process_functions.get(df_name)
            if process_func is not None:
                s = process_func(df)
                res[df_name] = s

        return res