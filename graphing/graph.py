import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime


class Grapher:
    def __init__(self, end_date: str):
        self.end_date = end_date
        self.graphing_functions = {
            "netDepositGrowthLeaders": self.graph_netDepositGrowthLeaders,
            "stETHApr": self.graph_stETHApr,
            "stEthOnL2Bridges": self.graph_stEthOnL2Bridges,
        }

    def graph_stETHApr(self, df: pd.DataFrame):
        plt.clf()
        # Ensure that 'time' column is in datetime format
        df["time"] = pd.to_datetime(df["time"])

        # Start a new figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot 'stakingAPR' line
        sns.lineplot(x="time", y="stakingAPR", data=df, label="stakingAPR", ax=ax)

        # Plot 'stakingAPR_ma_7' line
        sns.lineplot(x="time", y="stakingAPR_ma_7", data=df, label="stakingAPR_ma_7", ax=ax)

        # Set plot title and labels
        ax.set_title("stakingAPR and stakingAPR_ma_7 over time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")

        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        # Display the legend
        ax.legend()

        # Show the plot
        plt.show()

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f"graphs/{self.end_date}").mkdir(parents=True, exist_ok=True)
        fig.savefig(f"graphs/{self.end_date}/stakingAPR.png")

    def graph_netDepositGrowthLeaders(self, df: pd.DataFrame):
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort the dataframe by eth_deposits_growth in descending order and slice the first 10 rows
        top_10 = df.sort_values(by="eth_deposits_growth", ascending=False).iloc[:10]

        sns.barplot(x="eth_deposits_growth", y="name", data=top_10, ax=ax)
        ax.set(xlabel="ETH Deposits Growth", ylabel="Protocol")
        ax.set_title("ETH Deposits Growth Leaders")
        plt.show()

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f"graphs/{self.end_date}").mkdir(parents=True, exist_ok=True)
        fig.savefig(f"graphs/{self.end_date}/eth_deposits_growth.png")

    def graph_stEthOnL2Bridges(self, df: pd.DataFrame):
        # Convert the 'day' column to datetime format
        df["day"] = pd.to_datetime(df["day"])

        # Filter out the data after July 16, 2023
        df = df[df["day"] <= datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")]

        # Set 'day' as the index
        df.set_index("day", inplace=True)

        # Pivot the dataframe so that each bridge has its own column
        df_pivot = df.pivot(columns="name", values="balance_cumu")

        # Define a function to format the date
        def format_date(x, pos=None):
            return mdates.num2date(x).strftime("%B %-d")

        # Reset default settings
        plt.rcdefaults()

        # Set up a new color palette for the plot
        palette = sns.color_palette("hls", df_pivot.columns.size)

        # Plotting the stacked area plot with formatted dates
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.set_palette(palette)

        # Create the stacked area plot
        ax.stackplot(df_pivot.index, df_pivot.T, labels=df_pivot.columns, alpha=0.8)

        # Set plot title and labels
        ax.set_title("Cumulative balances of each bridge over time", fontsize=16)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Cumulative Balance", fontsize=14)

        # Create the legend
        ax.legend(loc="upper left")

        # Set the date formatter for the x-axis
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))

        # Rotate date labels slightly
        plt.xticks(rotation=30)

        # Show the plot
        plt.show()

        Path(f"graphs/{self.end_date}").mkdir(parents=True, exist_ok=True)
        fig.savefig(f"graphs/{self.end_date}/stEthOnL2Bridges.png")

    def process_all(self, dune_dataframes: dict[str, pd.DataFrame]):
        # for k, v in dune_dataframes.items():
        #     if k in self.graphing_functions.keys() and self.graphing_functions[k] is not None:
        #         self.graphing_functions[k](v)
        for df_name, df in dune_dataframes.items():
            graph_func = self.graphing_functions.get(df_name)
            if graph_func is not None:
                print(df_name)
                graph_func(df)
