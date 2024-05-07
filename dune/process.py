import pandas as pd


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
    # Get the most recent 7d moving average
    recent_7d_ma = df["stakingAPR_ma_7"].values[0]

    # Format the result into a string
    result_string = f"7d MA: {recent_7d_ma:.2%}"

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


def process_bridgeChange(df):
    # Apply rounding logic to the 'period_change' column
    df['period_change'] = df['period_change'].apply(lambda x: round(x, 2))
    df['end_amount'] = df['end_amount'].apply(lambda x: int(round(x, 0)))
    df['start_amount'] = df['start_amount'].apply(lambda x: int(round(x, 0)))

    # Convert the DataFrame to a string
    df_string = df.to_string(index=False)

    return df_string

def process_bridgedToCosmos(df):
    # Sort by day
    df = df.sort_values("day")

    # Get values 
    balance = df.iloc[-1]['balance_cumu']
    balance_7d_ago = df.iloc[-8]['balance_cumu']
    pct_change = (balance/balance_7d_ago - 1) * 100

    result_string = f"The balance of wstETH on Cosmos is {balance:.0f}, with a 7d change of {pct_change:.2f}%."

    return result_string

# Define a dictionary mapping the DataFrame names to their respective processing functions
process_functions = {
    "tvl": process_tvl,
    "netDepositGrowthLeaders": process_netDepositGrowthLeaders,
    "stETHApr": process_stETHApr,
    "stEthToEth": process_stEthToEth,
    # "dexLiquidityReserves": process_dexLiquidityReserves,
    "bridgeChange": process_bridgeChange,
    "totalStEthInDeFi": process_totalStEthInDeFi,
    "bridgedToCosmos": process_bridgedToCosmos,
}


def process_dune(dune_results: dict[str, pd.DataFrame]) -> dict[str, str]:
    res = {}

    for df_name, df in dune_results.items():
        process_func = process_functions.get(df_name)
        if process_func is not None:
            s = process_func(df)
            res[df_name] = s

    return res
