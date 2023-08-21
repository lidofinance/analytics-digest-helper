from dune_client.client import DuneClient
from .queries import get_queries
import os
import pickle
import datetime


def get_query_result(queries, query_name, cluster="medium"):
    query = queries[query_name]

    dune = DuneClient(os.environ["DUNE_API_KEY"])
    pd = dune.refresh_into_dataframe(query, performance=cluster)
    return pd


def load(start_date: str, end_date: str, sol_start_deposits: float, sol_end_deposits: float):
    queries = get_queries(start_date, end_date, sol_start_deposits, sol_end_deposits)
    dfs = {}
    for query_name in queries.keys():
        dfs[query_name] = get_query_result(queries, query_name, cluster="large")

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"data/dune_data_{now}.pkl"
    with open(file_name, "wb") as f:
        pickle.dump(dfs, f)

    return dfs
