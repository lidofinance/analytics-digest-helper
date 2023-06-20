import os

examples = []
for filename in os.listdir("examples"):
    with open(f"examples/{filename}", "r") as f:
        examples.append(f.read())

prompt = """
Here are the analytics digests in the form of Twitter thread
{examples}

You need to make a new one for the next week on the same form
You should point up any change compared with the previous week
Current metric values are:
{metrics}
"""


metrics = """
TVL: $12.7b

Withdrawals:
- requested 54,971 ETH
- finalized 57,937 ETH
- claimed 53,876 ETH

stETH APR: 4.11%

LP: Curve reserves:
- ETH: 291,758
- stETH: 288,155

LP: Aave:
- V2 stETH pool: 955,021 stETH, 2 liquidations for 0.52 stETH total
- V3 wstETH pool: 272,962 wstETH, 1 liquidation for 0.61 wstETH

LP: Maker
- Maker wstETH-A: 343,462, 0 liquidations
- Maker wstETH-B: 521,582, 0 liquidations
- Maker steCRV: 72,894, 0 liquidations

LP: Lido on L2
- Arbitrum: 52,466 wstETH
- Optimism: 40,464 wstETH
- Polygon: 4,774 wstETH
"""

result = prompt.format(examples="\n".join(examples), metrics=metrics)
print(result)
