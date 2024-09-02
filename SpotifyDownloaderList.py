# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 18:51:36 2024

@author: Administrator
"""

import queue
import threading
import json
import requests

# from stem import Signal
# from stem.control import Controller

# def switch_proxy():
#     with Controller.from_port() as controller:
#         controller.authenticate()
#         controller.signal(Signal.NEWNYM)
        
def producer(headers_url,sharelist):
    for url in sharelist:       
        try:
            last_part = url.split('/')[-1]
            track_id = last_part.split('?')[0] if '?' in last_part else last_part
            download_url = f'https://api.spotifydown.com/download/{track_id}'

            # Fetch download link
            download_response = requests.get(url=download_url, headers=headers_url)
            download_data = json.loads(download_response.text)
            true_url = download_data['link']            
            thread_safe_queue.put((true_url, download_data))
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            # Do not put None here to avoid premature stopping of the consumer
            continue  # Skip to the next iteration without breaking
    thread_safe_queue.put(None)  # Signal to stop the consumer

def consumer(headers_download):
    while True:
        item = thread_safe_queue.get()
        if item is None:
            thread_safe_queue.task_done()
            break
        try:
            response = requests.get(url=item[0], headers=headers_download)
            filename = f"{item[1]['metadata']['title']}_{item[1]['metadata']['artists']}.mp3"
            
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    f.write(chunk)
            print(f"Download completed for: {filename}")
        except Exception as e:
            print(f"Failed to download {item[0]}: {e}")
        finally:
            thread_safe_queue.task_done()

if __name__=='__main__':
    headers_url = {
        'Host': 'api.spotifydown.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Accept': '*/*',
        'Origin': 'https://spotifydown.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://spotifydown.com/',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7'
    }

    headers_download = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
    }
    sharelist=['https://open.spotify.com/track/6ERiuMBkiTfDzZ2nkCkOdv?si=a244038354f14f21',
               'https://open.spotify.com/track/1R0M0RAj4iErXwuUhU6mmh?si=73724f7f468a49bf',
               'https://open.spotify.com/track/4kDpSClrF42AkJOTQwqxyI?si=cdb6ab0e5d9444af'
               ]
    
    
    thread_safe_queue = queue.Queue()
    producer_thread = threading.Thread(target=producer, args=(headers_url,sharelist))
    consumer_thread = threading.Thread(target=consumer, args=(headers_download,))

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    thread_safe_queue.join()  # Ensure all tasks are processed
    consumer_thread.join()

    print("All downloads are completed.")
