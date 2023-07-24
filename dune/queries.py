from dune_client.query import Query
from dune_client.types import QueryParameter

def get_queries(start_date: str, end_date: str):
    queries = {
        "tvl": Query(
            name="tvl",
            query_id=2497839,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),

            ]
        ),
        "netDepositGrowthLeaders": Query(
            name="netDepositGrowthLeaders",
            query_id=2393989,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ]
        ),
        "stETHApr": Query(
            name="stETHApr",
            query_id=2404762,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
            ],
        ),
        "stEthToEth": Query(
            name="stEthToEth",
            query_id=2198571,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
            ],
        ),
        "dexLiquidityReserves": Query(
            name="dexLiquidityReserves",
            query_id=2706963,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
        "stEthOnL2": Query(
            name="stEthOnL2",
            query_id=2709470,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ]
        ),
    }
    return queries