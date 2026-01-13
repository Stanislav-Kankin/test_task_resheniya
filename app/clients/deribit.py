from dataclasses import dataclass

import aiohttp


@dataclass(frozen=True)
class DeribitClient:
    base_url: str  # https://www.deribit.com или https://test.deribit.com

    async def get_index_price(self, index_name: str) -> float:
        # Deribit: GET /api/v2/public/get_index_price?index_name=btc_usd|eth_usd
        url = f"{self.base_url}/api/v2/public/get_index_price"
        params = {"index_name": index_name}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                data = await resp.json()

        # ожидаем {"result": {"index_price": ...}}
        return float(data["result"]["index_price"])
