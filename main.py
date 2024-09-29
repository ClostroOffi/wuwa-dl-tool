import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

RESOURCE_URL = ""
CDN_BASE_URL = ""

# Use sessions to reuse TCP connections and improve speed
session = requests.Session()

def download_file(url, dest, size, session, max_retries=3, timeout=30, chunk_size=65536):
    attempt = 0
    while attempt < max_retries:
        try:
            with session.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                # Skip download if the file already exists and size matches
                if os.path.exists(dest) and os.path.getsize(dest) == size:
                    print(f"{dest} already exists, skipping...")
                    return
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):  # Larger chunk size
                        if chunk:
                            f.write(chunk)
            print(f"Downloaded {dest} ({size} bytes)")
            break
        except requests.RequestException as e:
            attempt += 1
            print(f"Attempt {attempt} failed for {url}. Error: {e}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                print(f"Failed to download {url} after {max_retries} attempts")

def download_resources(resource_url, cdn_base_url, output_folder, max_workers=16):
    response = session.get(resource_url)
    response.raise_for_status()
    resources = response.json().get('resource', [])

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for resource in resources:
            file_url = cdn_base_url + resource['dest'].lstrip('/')
            dest_path = os.path.join(output_folder, resource['dest'].lstrip('/'))
            futures.append(executor.submit(download_file, file_url, dest_path, resource['size'], session))

        for future in as_completed(futures):
            future.result()  # This will raise any exception caught during download

def main():
    output_folder = input("Enter the folder path to download files to: ").strip()
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    download_resources(RESOURCE_URL, CDN_BASE_URL, output_folder)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
