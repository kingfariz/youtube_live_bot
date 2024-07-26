import json
import requests
import socks
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from threading import Thread
import time

# Path to the proxy JSON file
proxy_file_path = 'proxies/proxy.json'

# Load proxies from JSON file
def load_proxies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            proxy_data = json.load(file)
            if isinstance(proxy_data, list):
                return proxy_data
            else:
                print("Error: JSON data should be a list of proxies.")
                return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Convert JSON data to proxy format
def convert_proxies_to_format(proxies):
    formatted_proxies = []
    for proxy in proxies:
        if 'protocols' in proxy and 'socks4' in proxy['protocols']:
            formatted_proxies.append(f"socks4://{proxy['ip']}:{proxy['port']}")
    return formatted_proxies

# Load and format proxies
proxies_data = load_proxies(proxy_file_path)
proxies_list = convert_proxies_to_format(proxies_data)

# Define the YouTube live stream URL
youtube_live_url = "https://www.youtube.com/watch?v=[VIDEO_ID_HERE]"

def view_live_stream(proxy):
    session = requests.Session()
    session.proxies = {
        'http': proxy,
        'https': proxy,
    }
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    while True:
        try:
            response = session.get(youtube_live_url, timeout=10)
            if response.status_code == 200:
                print(f"Viewing with proxy {proxy} - Status code: {response.status_code}")
                # Keep the connection open by continuing the loop
                time.sleep(60)  # Sleep for 60 seconds before next request
            else:
                print(f"Received unexpected status code {response.status_code} with proxy {proxy}")
        except requests.exceptions.ProxyError as e:
            print(f"Proxy error with {proxy}: {e}")
            break  # Exit loop and try the next proxy
        except requests.exceptions.RequestException as e:
            print(f"Request error with {proxy}: {e}")
            break  # Exit loop and try the next proxy

# Start viewing the live stream using multiple proxies
threads = []
for proxy in proxies_list:
    thread = Thread(target=view_live_stream, args=(proxy,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()
