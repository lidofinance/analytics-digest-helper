import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
from textwrap import wrap
from matplotlib.dates import DateFormatter

class Grapher:
    def __init__(self, end_date: str):
        self.end_date = end_date
        self.graphing_functions = {
            "netDepositGrowthLeaders": self.graph_netDepositGrowthLeaders,
            "stETHApr": self.graph_stETHApr,
            "stEthOnL2Bridges": self.graph_stEthOnL2Bridges,
            "stEthToEth": self.graph_stEthToEth,
            "tvl": self.graph_tvl,
            "totalStEthInDeFiPools": self.graph_totalStEthInDeFi,
            "dexLiquidityReserves": self.graph_dexLiquidityReserves,
        }

    def graph_dexLiquidityReserves(self, df: pd.DataFrame):
        # Set the seaborn style
        sns.set_theme()

        # Create a subplot without a frame
        fig, ax = plt.subplots(1, 1, figsize=(10, 2))

        # Remove the axes of the subplot
        ax.axis('off')

        # Format the values in the table with commas for each thousand like 123,456,789.99
        cell_text = df.values.copy()
        for i in range(cell_text.shape[0]):
            for j in range(cell_text.shape[1]):
                if isinstance(cell_text[i, j], float):
                    # Express 'period_change' as a percentage
                    if df.columns[j] == 'period_change':
                        cell_text[i, j] = '{:.2f}%'.format(cell_text[i, j] * 100)
                    else:
                        cell_text[i, j] = '{:,.2f}'.format(cell_text[i, j])
        
        # Create a table and add it to the subplot
        table = plt.table(cellText=cell_text, 
                        colLabels=df.columns, 
                        cellLoc='center', 
                        loc='center',
                        bbox=[0, 0, 1, 1])

        # Apply style to the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/dexLiquidityReserves.png')
    

    def graph_totalStEthInDeFi(self, df: pd.DataFrame):
        # Convert time column to datetime format and set it as the index
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)

        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create the line plot
        sns.lineplot(data=df, x=df.index, y='stETH_DeFi_share', ax=ax, color='blue')

        # Set the x-axis formatter to display date in "Month Day" format
        ax.xaxis.set_major_formatter(DateFormatter('%B %d'))

        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45)

        # Set plot title and labels
        ax.set_title('stETH DeFi Share Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('stETH DeFi Share')

        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        plt.savefig(f'graphs/{self.end_date}/totalStEthInDeFi.png')


    def graph_tvl(self, df: pd.DataFrame):
        df = df.reset_index(drop=True)

        # Replace NaN values with an empty string
        df.fillna("", inplace=True)

        # Calculate the figure height based on the number of rows and columns. Added extra space for the column headers.
        fig_height = df.shape[0]*0.4 + len(max(df.columns, key=len))/1.5

        # Create a figure and a subplot
        fig, ax = plt.subplots(figsize=(10, fig_height))

        # Hide axes
        ax.axis('off')

        # Adjust column headers to fit within the column width
        col_labels = [ '\n'.join(wrap(l, 15)) for l in df.columns ]

        # Create the table and scale it to the subplot
        table = plt.table(cellText=df.values, colLabels=col_labels, cellLoc = 'center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/tvl.png')

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

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/stakingAPR.png')

    def graph_stEthToEth(self, df: pd.DataFrame):
        # Convert 'time' column to datetime if it's not already
        if df['time'].dtype == 'O':
            df['time'] = pd.to_datetime(df['time'])

        # Create a plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use Seaborn to create the line plot
        sns.lineplot(x='time', y='weight_avg_price', data=df, ax=ax)
        
        # Set plot title and labels
        plt.title('Weighted Average Price Over Time')
        plt.xlabel('Time')
        plt.ylabel('Weighted Average Price')
        
        # Set x-axis date format without year and time
        date_format = mdates.DateFormatter('%b %d')
        plt.gca().xaxis.set_major_formatter(date_format)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/stEthToEth.png')

    def graph_netDepositGrowthLeaders(self, df: pd.DataFrame):
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sort the dataframe by eth_deposits_growth in descending order and slice the first 10 rows
        top_10 = df.sort_values(by='eth_deposits_growth', ascending=False).iloc[:10]
        
        sns.barplot(x="eth_deposits_growth", y="name", data=top_10, ax=ax)
        ax.set(xlabel='ETH Deposits Growth', ylabel='Protocol')
        ax.set_title('ETH Deposits Growth Leaders')

        # Save the plot to a file in graphs/<end_date> folder. make the folder if it doesn't exist.
        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/eth_deposits_growth.png')

    def graph_stEthOnL2Bridges(self, df: pd.DataFrame):
        # Convert the 'day' column to datetime format
        df['day'] = pd.to_datetime(df['day'])

        # Filter out the data after July 16, 2023
        df = df[df['day'] <= datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S")]

        # Set 'day' as the index
        df.set_index('day', inplace=True)

        # Pivot the dataframe so that each bridge has its own column
        df_pivot = df.pivot(columns='name', values='balance_cumu')

        # Define a function to format the date
        def format_date(x, pos=None):
            return mdates.num2date(x).strftime('%B %-d')

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
        ax.legend(loc='upper left')

        # Set the date formatter for the x-axis
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))

        # Rotate date labels slightly
        plt.xticks(rotation=30)

        Path(f'graphs/{self.end_date}').mkdir(parents=True, exist_ok=True)
        fig.savefig(f'graphs/{self.end_date}/stEthOnL2Bridges.png')

    def process_all(self, dune_dataframes: dict[str, pd.DataFrame]):
        # for k, v in dune_dataframes.items():
        #     if k in self.graphing_functions.keys() and self.graphing_functions[k] is not None:
        #         self.graphing_functions[k](v)
        for df_name, df in dune_dataframes.items():
            graph_func = self.graphing_functions.get(df_name)
            if graph_func is not None:
                print(df_name)
                graph_func(df)