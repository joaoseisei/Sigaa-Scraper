import threading
import queue
import requests

fila = queue.Queue()
proxies = []
funcionais = []
lock = threading.Lock()

with open('proxy_list.txt', 'r') as f:
    proxies = f.read().split("\n")
    for proxy in proxies:
        if proxy.startswith('http://'):
            proxy = proxy.replace('http://', '')
        fila.put(proxy)

def check_proxies():
    global fila
    while not fila.empty():
        proxy = fila.get()
        try:
            res = requests.get('https://www.meuip.com.br/', proxies={'http': proxy, 'https': proxy}, timeout=5)
            if res.status_code == 200:
                print(f"\033[92mProxy válido: {proxy}\033[0m")
                with lock:
                    funcionais.append(proxy)
        except requests.exceptions.RequestException as e:
            print(f"\033[91mFalha com o proxy {proxy}: {e}\033[0m")
        finally:
            fila.task_done()

for _ in range(50):
    threading.Thread(target=check_proxies).start()

fila.join()

print(f'\033[92m\nPROXIES FUNCIONAIS:\n\033[0m')
for proxy in funcionais:
    print(f'\033[92m{proxy}\033[0m')

