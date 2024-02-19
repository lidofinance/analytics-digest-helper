import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
from matplotlib.dates import DateFormatter
import numpy as np
import os


class Grapher:
    def __init__(self, end_date: str):
        self.end_date = end_date
        self.graphing_functions = {
            "netDepositGrowthLeaders": self.graph_netDepositGrowthLeaders,
            "stETHApr": self.graph_stETHApr,
            "stEthOnL2Bridges": self.graph_stEthOnL2Bridges,
            "stEthToEth": self.graph_stEthToEth,
            "tvl": self.graph_tvl,
            "totalStEthInDeFi": self.graph_totalStEthInDeFi,
            # "dexLiquidityReserves": self.graph_dexLiquidityReserves,
        }
        self.graph_location = f"/tmp/digest/{end_date}/graphs"
        Path(self.graph_location).mkdir(parents=True, exist_ok=True)

    def graph_dexLiquidityReserves(self, df: pd.DataFrame,):
        df = df.reset_index(drop=True)

        # Format the values in the table
        for col in df.columns:
            if "change" in col.lower():
                df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: "" if pd.isnull(x) else "{:.2f}%".format(x * 100))
            elif col != "token":
                df[col] = df[col].apply(lambda x: "${:,.0f}".format(x))

        # Calculate the figure height based on the number of rows and columns. Added extra space for the column headers.
        fig_height = 2
        fig_width = 6  # Adjust this value as needed

        # Create a figure and a subplot
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Hide axes
        ax.axis("off")

        # Create the table and scale it to the subplot
        # Format column labels to replace underscores with spaces and capitalize each word
        formatted_columns = [col.replace('_', ' ').title() for col in df.columns]
        table = plt.table(cellText=df.values, cellLoc="center", loc="center", colLabels=formatted_columns)
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        # Make the column labels bold and set the background color
        table.auto_set_column_width(col=list(range(len(df.columns))))
        for key, cell in table.get_celld().items():
            if key[0] == 0:
                cell.set_fontsize(14)
                cell.set_facecolor('gray')

        
        self.save_figure(fig, "dexLiquidityReserves")

    def graph_totalStEthInDeFi(self, df: pd.DataFrame):

        original_df = df.copy()
        # Convert time column to datetime format and set it as the index
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)

        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(10, 7))

        # Create the line plot
        sns.lineplot(data=df, x=df.index, y="stETH_DeFi_share", ax=ax, color="blue")

        # Set the x-axis formatter to display date in "Month Day" format
        ax.xaxis.set_major_formatter(DateFormatter("%B %d"))

        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45)

        # Set plot title and labels
        ax.set_title("Total (w)stETH in DeFi")
        ax.set_xlabel("")
        ax.set_ylabel("")

        self.save_figure(fig, "totalStEthInDeFi")

        def extract_relevant_data(df):
            """
            Takes in a DataFrame and returns a table with specific columns for the latest data point 
            and the data point 7 days before that.
            """
            # Convert 'time' to datetime format for easier manipulation
            df['time'] = pd.to_datetime(df['time'])
            
            # Sort the DataFrame by 'time' in ascending order
            df.sort_values('time', inplace=True)
            
            # Get the latest data point and the data point 7 days before that
            latest_data = df.iloc[-1]
            seven_days_before = df[df['time'] <= (latest_data['time'] - pd.Timedelta(days=7))].iloc[-1]
            
            # Create a new DataFrame to store these two rows
            result_df = pd.DataFrame([latest_data, seven_days_before])
            
            # Keep only the relevant columns
            result_df = result_df[['time', 'liquidity_pools', 'lending_pools', 'stETH_in_DeFi', 'stETH_DeFi_share']]
            
            return result_df
        
        def format_and_save_table(df):
            """
            Formats and saves a DataFrame as a table image.
            """
            # Replace NaN and other null-like values with an empty string
            df.replace(["<nill>", "nil", "undefined", "null", np.nan], "", inplace=True)
            
            # Format the values in the table
            for col in df.columns:
                if col == "liquidity_pools" or col == "lending_pools" or col == "stETH_in_DeFi":
                    df[col] = df[col].apply(lambda x: "{:,.0f}".format(x))  # Express in whole numbers with comma separators
                elif col == "stETH_DeFi_share":
                    df[col] = df[col].apply(lambda x: "{:.2f}%".format(x))  # Express as percentage
                elif col == "time":
                    df[col] = df[col].dt.strftime('%Y-%m-%d')  # Format datetime to string
                
            # Create a figure and a subplot
            fig, ax = plt.subplots(figsize=(12, 2))
            
            # Hide axes
            ax.axis("off")
            
            # Create the table and scale it to the subplot
            table = plt.table(cellText=df.values, cellLoc="center", loc="center", colLabels=[col.replace('_', ' ').title() for col in df.columns])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            
            # Make the column labels bold and set the background color
            table.auto_set_column_width(col=list(range(len(df.columns))))
            for key, cell in table.get_celld().items():
                if key[0] == 0:
                    cell.set_fontsize(14)
                    cell.set_facecolor('gray')
            
            self.save_figure(fig, "totalStEthInDeFi_table")

        extracted_data = extract_relevant_data(original_df.copy())

        format_and_save_table(extracted_data.copy())

            

    def graph_tvl(self, df: pd.DataFrame):
        df = df.reset_index(drop=True)

        # Replace NaN values and other null-like values with an empty string
        df.replace(["<nill>", "nil", "undefined", "null", np.nan], "", inplace=True)

        # Remove Solana until we prepare a query to extract the data
        df = df[df['chain'] != 'Solana']

        # Format the values in the table
        for col in df.columns:
            if "change" in col.lower():
                df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: "" if pd.isnull(x) else "{:.0f}%".format(x * 100))  # Rounded to no decimals
            elif col == "Tokens deposited":
                df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: "" if pd.isnull(x) else "{:,.0f}".format(x))  # Express in whole numbers with comma separators, rounded to no decimals
            elif col == "TVL":
                df[col] = df[col].apply(lambda x: "${:,.0f}".format(x))  # Express as currency, rounded to no decimals
            elif col != "chain":
                df[col] = df[col].apply(lambda x: "{:,.0f}".format(x))  # Rounded to no decimals

        # Calculate the figure height based on the number of rows and columns. Added extra space for the column headers.
        fig_height = 2
        fig_width = 12  # Adjust this value as needed

        # Create a figure and a subplot
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Hide axes
        ax.axis("off")

        # Create the table and scale it to the subplot
        table = plt.table(cellText=df.values, cellLoc="center", loc="center", colLabels=["chain", "TVL", "Tokens deposited", "TVL change %", "Deposits Change %", "Token Price Change %"])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        # Make the column labels bold and set the background color
        table.auto_set_column_width(col=list(range(len(df.columns))))
        for key, cell in table.get_celld().items():
            if key[0] == 0:
                cell.set_fontsize(14)
                cell.set_facecolor('gray')

        self.save_figure(fig, "tvl")

    def graph_stETHApr(self, df: pd.DataFrame):
        plt.clf()
        # Ensure that 'time' column is in datetime format
        df["time"] = pd.to_datetime(df["time"])

        df = df.sort_values("time")

        # Start a new figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot 'stakingAPR' line
        sns.lineplot(x="time", y="stakingAPR", data=df, label="stakingAPR", ax=ax)

        # Plot 'stakingAPR_ma_7' line
        ma_plot = sns.lineplot(x="time", y="stakingAPR_ma_7", data=df, label="stakingAPR_ma_7", ax=ax)

        # Set plot title
        ax.set_title("Staking APR")

        # Remove axis labels
        ax.set_xlabel("")
        ax.set_ylabel("")

        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        # Display the legend
        ax.legend()

        # Add percentage label at the very last point of stakingAPR_MA_7 line
        last_point = df.iloc[-1]
        ax.annotate(f'{last_point["stakingAPR_ma_7"]:.2%}', 
                    (last_point["time"], last_point["stakingAPR_ma_7"]), 
                    textcoords='offset points', 
                    xytext=(0,10), 
                    ha='right', 
                    va='bottom',
                    color='black',
                    zorder=10)
        self.save_figure(fig, "stakingAPR")

    def graph_stEthToEth(self, df: pd.DataFrame):
        # Convert 'time' column to datetime if it's not already
        if df["time"].dtype == "O":
            df["time"] = pd.to_datetime(df["time"])

        # Correct anomalies in weight_avg_price
        def correct_anomalies(y_values):
            corrected = np.copy(y_values)
            for i in range(1, len(y_values) - 1):
                prev_val = y_values[i - 1]
                curr_val = y_values[i]
                next_val = y_values[i + 1]

                if curr_val < 0.7 * prev_val and curr_val < 0.7 * next_val:
                    corrected[i] = (prev_val + next_val) / 2.0

            return corrected

        df["weight_avg_price"] = correct_anomalies(df["weight_avg_price"])

        # Create a plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Use Seaborn to create the line plot
        sns.lineplot(x="time", y="weight_avg_price", data=df, ax=ax)

        # Set plot title and labels
        plt.title("stETH:ETH Price")
        plt.xlabel("")
        plt.ylabel("")

        # Set x-axis date format without year and time
        date_format = mdates.DateFormatter("%b %d")
        plt.gca().xaxis.set_major_formatter(date_format)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        self.save_figure(fig, "stEthToEth")

    def graph_netDepositGrowthLeaders(self, df: pd.DataFrame):
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort the dataframe by eth_deposits_growth in descending order and slice the first 5 rows
        top_5 = df.sort_values(by="eth_deposits_growth", ascending=False).iloc[:5]

        bars = sns.barplot(x="eth_deposits_growth", y="name", data=top_5, ax=ax)
        ax.set_title("ETH Deposits Growth Leaders")

        # Define a function to format the numbers
        def format_number(number):
            if number >= 1e9:  # Billion
                return "{:.0f}B".format(number / 1e9)
            elif number >= 1e6:  # Million
                return "{:.0f}M".format(number / 1e6)
            elif number >= 1e3:  # Thousand
                return "{:.0f}K".format(number / 1e3)
            else:
                return str(number)
            
        ax.set_xlabel("")
        ax.set_ylabel("")

        # Add a label at the end of each bar with the formatted value
        for bar in bars.patches:
            bars.annotate(format_number(bar.get_width()), 
                          (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                          ha = 'center', va = 'center',
                          size=15, xytext = (20, 0),
                          textcoords = 'offset points')

        self.save_figure(fig, "eth_deposits_growth")

    def graph_stEthOnL2Bridges(self, df: pd.DataFrame):
        # Convert the 'day' column to datetime format
        df["day"] = pd.to_datetime(df["day"])

        # Filter out the data after July 16, 2023
        df = df[df["day"] <= datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")]

        # Set 'day' as the index
        df.set_index("day", inplace=True)

        # Pivot the dataframe so that each bridge has its own column
        df_pivot = df.pivot(columns="bridge", values="amount")

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

        # Set plot title
        ax.set_title("Cumulative balances of each bridge over time", fontsize=16)

        # Remove axis labels
        ax.set_xlabel("")
        ax.set_ylabel("")

        # Create the legend
        ax.legend(loc="upper left")

        # Set the date formatter for the x-axis
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(format_date))

        # Rotate date labels slightly
        plt.xticks(rotation=30)

        self.save_figure(fig, "stEthOnL2Bridges")

    def process_all(self, dune_dataframes: dict[str, pd.DataFrame]):
        for df_name, df in dune_dataframes.items():
            graph_func = self.graphing_functions.get(df_name)
            if graph_func is None:
                print(f"No graphing function for {df_name}")
            else:
                print("Graphing " + df_name)
                graph_func(df)

    def save_figure(self, fig, name):
        fig.savefig(f"{self.graph_location}/{name}.png")
        if os.path.exists(f"{self.graph_location}/{name}.png"):
            print(f"Graph {name} saved successfully.")
        else:
            print(f"Failed to save the graph {name}")