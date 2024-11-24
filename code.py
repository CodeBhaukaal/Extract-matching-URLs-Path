import os
import re
import json
import requests

def extract_specific_urls_from_file(file_path, base_url):
    urls = []
    # Regular expression to match URLs starting with the base_url
    url_pattern = re.compile(rf'{re.escape(base_url)}[^\s]*')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Extract matching URLs from each line
                urls.extend(url_pattern.findall(line))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return urls

def extract_urls_from_directory(directory_path, base_url):
    all_urls = {}
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.ejs'):
                file_path = os.path.join(root, file_name)
                urls = extract_specific_urls_from_file(file_path, base_url)
                if urls:
                    # Store URLs under the corresponding file name
                    relative_path = os.path.relpath(file_path, directory_path)
                    all_urls[relative_path] = urls
    return all_urls

def download_images(image_urls, download_folder):
    failed_urls = []
    os.makedirs(download_folder, exist_ok=True)
    
    for url in image_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Extract file name from URL
                file_name = os.path.join(download_folder, os.path.basename(url))
                with open(file_name, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {url}")
            else:
                print(f"Failed to download: {url}")
                failed_urls.append(url)
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            failed_urls.append(url)
    
    return failed_urls

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    # Directory containing .ejs files
    source_directory = r"G:\py\newbigmumbai_backup\src"
    # Base URL to match
    base_url = "https://bigmumbai4.com"
    # Output JSON files
    matched_urls_json = "matched_urls.json"
    image_download_folder = "downloaded_images"
    failed_urls_json = "failed_urls.json"
    
    # Extract all URLs from the directory
    matched_urls = extract_urls_from_directory(source_directory, base_url)
    save_to_json(matched_urls, matched_urls_json)
    
    # Separate image URLs and non-image URLs
    all_urls = sum(matched_urls.values(), [])  # Flatten the list of all URLs
    image_urls = [url for url in all_urls if url.endswith(('.png', '.jpg'))]
    other_urls = [url for url in all_urls if not url.endswith(('.png', '.jpg'))]
    
    # Download images and get failed URLs
    failed_urls = download_images(image_urls, image_download_folder)
    
    # Save non-image URLs and failed image URLs to JSON
    save_to_json({"failed_image_urls": failed_urls, "other_urls": other_urls}, failed_urls_json)
    print("Process completed.")
