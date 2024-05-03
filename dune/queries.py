from dune_client.query import QueryBase
from dune_client.types import QueryParameter


def get_queries(start_date: str, end_date: str, sol_start_deposits: float, sol_end_deposits: float):
    queries = {
        "tvl": QueryBase(
            name="tvl",
            query_id=2497839,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
                QueryParameter.number_type("solana_start_deposits", sol_start_deposits),
                QueryParameter.number_type("solana_end_deposits", sol_end_deposits),
            ],
        ),
        "netDepositGrowthLeaders": QueryBase(
            name="netDepositGrowthLeaders",
            query_id=2393989,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
        "stETHApr": QueryBase(
            name="stETHApr",
            query_id=2404762,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
        "stEthToEth": QueryBase(
            name="stEthToEth",
            query_id=2198571,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
            ],
        ),
        # "dexLiquidityReserves": QueryBase(
        #     name="dexLiquidityReserves",
        #     query_id=2706963,
        #     params=[
        #         QueryParameter.date_type("digest_start_date", start_date),
        #         QueryParameter.date_type("digest_end_date", end_date),
        #     ],
        # ),
        "stEthOnL2Bridges": QueryBase(
            name="stEthOnL2Bridges",
            query_id=2709440,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
        "bridgeChange": QueryBase(
            name="bridgeChange",
            query_id=2709470,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
        "totalStEthInDeFi": QueryBase(
            name="totalStEthInDeFi",
            query_id=2740000,
            params=[
                QueryParameter.date_type("digest_start_date", start_date),
                QueryParameter.date_type("digest_end_date", end_date),
            ],
        ),
    }
    return queries
