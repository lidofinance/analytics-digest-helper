import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from pathlib import Path

class Grapher:
    def __init__(self, end_date: str):
        self.end_date = end_date
        self.graphing_functions = {
            "tvl": None,
            "netDepositGrowthLeaders": self.graph_netDepositGrowthLeaders,
            "stETHApr": self.graph_stETHApr,
            "stEthToEth": None,
            "dexLiquidityReserves": None,
            "stEthOnL2": None
        }
        

    def graph_stETHApr(self, df: pd.DataFrame):
        plt.clf()
        # Ensure that 'time' column is in datetime format
        df['time'] = pd.to_datetime(df['time'])

        # Start a new figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot 'stakingAPR' line
        sns.lineplot(x='time', y='stakingAPR', data=df, label='stakingAPR', ax=ax)

        # Plot 'stakingAPR_ma_7' line
        sns.lineplot(x='time', y='stakingAPR_ma_7', data=df, label='stakingAPR_ma_7', ax=ax)

        # Set plot title and labels
        ax.set_title('stakingAPR and stakingAPR_ma_7 over time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')

        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        # Display the legend
        ax.legend()

        # Show the plot
        plt.show()

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/stakingAPR.png')

    def graph_netDepositGrowthLeaders(self, df: pd.DataFrame):
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="eth_deposits_growth", y="name", data=df, ax=ax)
        ax.set(xlabel='ETH Deposits Growth', ylabel='Protocol')
        ax.set_title('ETH Deposits Growth Leaders')
        plt.show()
        
        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/eth_deposits_growth.png')

    def process_all(self, dune_dataframes: dict[str, pd.DataFrame]):
        for k, v in dune_dataframes.items():
            if self.graphing_functions[k] is not None:
                self.graphing_functions[k](v)