import argparse
from dune.loader import load
from dune.process import process_dune
from llm.writer import write_thread
from graphing.graph import Grapher
from pathlib import Path
import datetime
import time
import os
import pickle
from llm.blocks import BlockWriter

def main(start_date: datetime.datetime, end_date: datetime.datetime, sol_start_deposits: float, sol_end_deposits: float):
    start_time = time.time() # start timing
    print(f"start_date: {str(start_date)}")
    print(f"end_date: {str(end_date)}")
    # dune_loaded = load(str(start_date), str(end_date), sol_start_deposits, sol_end_deposits)
    dune_loaded = pickle.load(open('data/dune_data_2023-08-02_11-18.pkl', 'rb'))
    processed = process_dune(dune_loaded)

    writer = BlockWriter(str(end_date), str(start_date))
    thread = writer.compose_thread(processed)
    print(thread)
    
    print("Writing thread to file")
    Path(f'threads/{str(end_date)}').mkdir(parents=True, exist_ok=True)
    with open(f'threads/{str(end_date)}/thread.md', 'w') as f:
        f.write(thread)
    print(f"Wrote thread to file in threads/{end_date}/thread.md")

    print("Graphing")
    grapher = Grapher(str(end_date))
    print(dune_loaded['totalStEthInDeFi'])
    grapher.process_all(dune_loaded)
    print(f"Done Graphing. Graphs are saved in graphs/{end_date}folder")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    return


if __name__ == '__main__':

    if (os.environ.get('DUNE_API_KEY') == None):
        print("Please set DUNE_API_KEY environment variable")
        exit(1)

    if (os.environ.get('OPENAI_API_KEY') == None):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)

    parser = argparse.ArgumentParser(description="Lido Weekly Digest Helper")

    parser.add_argument('-ss', '--sol_start', type=float, required=True, help='Description for Solana Start Deposits argument')
    parser.add_argument('-se', '--sol_end', type=float, required=True, help='Description for Solana End Deposits argument')
    parser.add_argument('-sd', '--start_date', type=str, required=True, help='Description for start_date argument')
    parser.add_argument('-ed', '--end_date', type=str, required=True, help='Description for end_date argument')
    

    args = parser.parse_args()

    # convert start date and ed to datetime objects
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")

    main(start_date, end_date, args.sol_start, args.sol_end)
