import os
import json
import requests
import time

RESOURCE_URL = ""
CDN_BASE_URL = ""

def download_resources(resource_url, cdn_base_url, output_folder):
    response = requests.get(resource_url)
    response.raise_for_status()
    resources = response.json().get('resource', [])

    for resource in resources:
        file_url = cdn_base_url + resource['dest'].lstrip('/')
        dest_path = os.path.join(output_folder, resource['dest'].lstrip('/'))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        print(f"Downloading {file_url} to {dest_path}")

        download_file(file_url, dest_path, resource['size'])

def download_file(url, dest, size, max_retries=3, timeout=30):
    attempt = 0
    while attempt < max_retries:
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"Downloaded {dest} ({size} bytes)")
            break
        except requests.RequestException as e:
            attempt += 1
            print(f"Attempt {attempt} failed for {url}. Error: {e}")
            if attempt < max_retries:
                print("Retrying...")
                time.sleep(5)  # Pause before trying again
            else:
                print(f"Failed to download {url} after {max_retries} attempts")

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