#!/usr/bin/env python3
"""
Download all images and files from mechanicape.nl and update HTML files to use local copies
"""

import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
import hashlib
import time

ARCHIEF_DIR = "projects/theos-mechanische-aap-archief"
IMAGES_DIR = os.path.join(ARCHIEF_DIR, "images")

def get_filename_from_url(url):
    """Extract and sanitize filename from URL"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    
    # Remove query parameters for the actual filename
    if '?' in filename:
        filename = filename.split('?')[0]
    
    # Create a hash suffix to ensure uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    name, ext = os.path.splitext(filename)
    
    # Sanitize filename
    name = re.sub(r'[^\w\-.]', '_', name)
    
    return f"{name}_{url_hash}{ext}"

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {e}")
        return False

def process_html_file(filepath):
    """Process a single HTML file to download and localize media"""
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    downloads = []
    
    # Find all mechanicape.nl URLs (images and files)
    urls = set()
    
    # Find image URLs
    img_pattern = r'src="(https://mechanicape\.nl/[^"]+)"'
    urls.update(re.findall(img_pattern, content))
    
    # Find attachment/link URLs
    link_pattern = r'href="(https://mechanicape\.nl/[^"]+)"'
    urls.update(re.findall(link_pattern, content))
    
    if not urls:
        print("  No mechanicape.nl URLs found")
        return False
    
    print(f"  Found {len(urls)} unique URLs")
    
    # Download each file and update content
    for url in urls:
        filename = get_filename_from_url(url)
        local_path = os.path.join(IMAGES_DIR, filename)
        relative_path = f"images/{filename}"
        
        # Check if file already exists
        if not os.path.exists(local_path):
            print(f"  ↓ Downloading: {filename}")
            if download_file(url, local_path):
                downloads.append(filename)
                time.sleep(0.1)  # Be nice to the server
            else:
                continue
        else:
            print(f"  ✓ Already exists: {filename}")
        
        # Update content to use local path
        content = content.replace(url, relative_path)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {len(downloads)} references")
        return True
    
    return False

def main():
    """Main function"""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    print("="*60)
    print("Downloading and localizing media files")
    print("="*60)
    
    # Find all HTML files (except index.html)
    html_files = []
    for filename in os.listdir(ARCHIEF_DIR):
        if filename.endswith('.html') and filename != 'index.html':
            html_files.append(os.path.join(ARCHIEF_DIR, filename))
    
    print(f"\nFound {len(html_files)} HTML files to process")
    
    updated_count = 0
    for filepath in sorted(html_files):
        if process_html_file(filepath):
            updated_count += 1
    
    # Count downloaded files
    image_count = len([f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))])
    
    print("\n" + "="*60)
    print(f"✓ Complete!")
    print(f"  Updated files: {updated_count}")
    print(f"  Total media files: {image_count}")
    print(f"  Location: {IMAGES_DIR}")
    print("="*60)

if __name__ == '__main__':
    main()
