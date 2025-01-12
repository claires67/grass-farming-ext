import asyncio
import random
import ssl
import json
import time
import uuid
import base64
import aiohttp
from datetime import datetime
from colorama import init, Fore, Style
from websockets_proxy import Proxy, proxy_connect

init(autoreset=True)

BANNER = """
_________ ____________________                            
__  ____/______  /__  ____/____________ _______________
_  / __ _  _ \  __/  / __ __  ___/  __ `/_  ___/_  ___/
/ /_/ / /  __/ /_ / /_/ / _  /   / /_/ /_(__  )_(__  ) 
\____/  \___/\__/ \____/  /_/    \__,_/ /____/ /____/  
"""

EDGE_USERAGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.57",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.52",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.46",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.128",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.112",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.98",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.133",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.121",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91"
]

HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created", 
    202: "Accepted",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden", 
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout"
}

def colorful_log(proxy, device_id, message_type, message_content, is_sent=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (
        f"{Fore.WHITE}[{timestamp}] "
        f"{Fore.MAGENTA}[Proxy: {proxy}] "
        f"{Fore.CYAN}[Device ID: {device_id}] "
        f"{Fore.YELLOW}[{message_type}] "
        f"{Fore.GREEN if is_sent else Fore.BLUE}{message_content}"
    )
    print(log_message)

async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, socks5_proxy))
    random_user_agent = random.choice(EDGE_USERAGENTS)
    
    colorful_log(proxy=socks5_proxy, device_id=device_id, message_type="INITIALIZATION", message_content=f"User Agent: {random_user_agent}")

    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": random_user_agent,
                "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"
            }
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            urilist = [
                "wss://proxy2.wynd.network:4444/",
                "wss://proxy2.wynd.network:4650/"
            ]
            uri = random.choice(urilist)
            proxy = Proxy.from_url(socks5_proxy)

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname="proxy.wynd.network", extra_headers=custom_headers) as websocket:

                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid5(uuid.NAMESPACE_DNS, socks5_proxy)), 
                             "version": "1.0.0", 
                             "action": "PING", 
                             "data": {}})

                        colorful_log(
                            proxy=socks5_proxy,  
                            device_id=device_id, 
                            message_type="SENDING PING", 
                            message_content=send_message,
                            is_sent=True
                        )

                        await websocket.send(send_message)
                        await asyncio.sleep(5)

                ping_task = asyncio.create_task(send_ping())
                
                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    colorful_log(proxy=socks5_proxy, device_id=device_id, message_type="RECEIVED", message_content=json.dumps(message))

        except Exception:
            print("Working...")
            await asyncio.sleep(5)

async def main():
    print(f"{Fore.CYAN}{BANNER}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}IM-Hanzou | GetGrass Crooter V2{Style.RESET_ALL}")

    try:
        with open("id.txt", "r") as id_file:
            user_id = id_file.read().strip()
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] id.txt not found. Please create the file and add your User ID.{Style.RESET_ALL}")
        return

    with open('proxy_list.txt', 'r') as file:
        local_proxies = file.read().splitlines()

    print(f"{Fore.YELLOW}Total Proxies: {len(local_proxies)}{Style.RESET_ALL}")

    tasks = [asyncio.ensure_future(connect_to_wss(proxy, user_id)) for proxy in local_proxies]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
