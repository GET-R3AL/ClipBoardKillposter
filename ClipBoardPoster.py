import requests
import pyperclip
import time
import threading
import queue

zkill = 'https://zkillboard.com/post/'
killmail_esi = 'https://esi.evetech.net/v1/killmails/'

post_queue = queue.Queue()

def monitor_clipboard():
    recent_value = pyperclip.paste()
    while True:
        clipboard = pyperclip.paste()
        if clipboard != recent_value:
            recent_value = clipboard
            if clipboard.startswith(killmail_esi):
                print(f'New killmail Detected: {clipboard}')
                post_queue.put(clipboard)
        time.sleep(0.1)

def process_queue():
    while True:
        clipboard = post_queue.get()
        try:
            print(f'POST: {clipboard}')
            response = requests.post(zkill, data={'killmailurl': clipboard})
            if response.status_code == 200:
                print('POST succeeded: DONE')
            else:
                print(f'POST failed with status {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Error posting killmail: {e}')
        finally:
            post_queue.task_done()

def main():
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()
    processing_thread = threading.Thread(target=process_queue, daemon=True)
    processing_thread.start()
    clipboard_thread.join()
    processing_thread.join()

if __name__ == '__main__':
    main()
