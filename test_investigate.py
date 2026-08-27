import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000') as client:
        for exc_id in [1, 2, 3, 4]:
            resp = await client.post(f'/exceptions/{exc_id}/investigate')
            print(f'Exception {exc_id}: {resp.status_code}')
            if resp.status_code == 200:
                data = resp.json()
                print(f'  Status: {data.get("status")}')
                print(f'  Classification: {data.get("classification")}')
                print(f'  Confidence: {data.get("confidence")}')
                print(f'  Explanation: {data.get("explanation")[:100]}...')
            else:
                print(f'  Error: {resp.text}')
            print()

asyncio.run(test())