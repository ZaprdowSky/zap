import asyncio
import aiohttp
import random
import re

# --- YENİ HEDEF LİNK ---
REF_CODE = "pixerals" 
WORKER_SAYISI = 1000
TIK_HIZI = 0.2 

async def get_proxies():
    urls = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ]
    proxies = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=10) as r:
                    found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', await r.text())
                    proxies.extend(found)
            except: continue
    return list(set(proxies))

async def worker(worker_id, proxy_queue):
    while True:
        proxy = await proxy_queue.get()
        proxy_url = f"http://{proxy}"
        connector = aiohttp.TCPConnector(ssl=False, limit=0, force_close=True)
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(f"https://api.thenanobutton.com/api/session?ref={REF_CODE}", proxy=proxy_url) as r:
                    if r.status == 200:
                        data = await r.json()
                        token = data.get("token")
                        async with session.ws_connect(f"wss://api.thenanobutton.com/ws?token={token}", proxy=proxy_url) as ws:
                            if worker_id % 250 == 0:
                                print(f"🚀 Pixerals-Worker-{worker_id} | IP: {proxy[:10]}...")
                            for _ in range(300): 
                                await ws.send_str("c")
                                await asyncio.sleep(TIK_HIZI)
        except: pass
        finally:
            proxy_queue.task_done()
            await proxy_queue.put(proxy)

async def main():
    proxies = await get_proxies()
    if not proxies: return
    proxy_queue = asyncio.Queue()
    for p in proxies: await proxy_queue.put(p)
    tasks = [asyncio.create_task(worker(i+1, proxy_queue)) for i in range(WORKER_SAYISI)]
    await asyncio.sleep(21000) 

if __name__ == "__main__":
    asyncio.run(main())
