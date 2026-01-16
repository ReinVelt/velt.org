#!/usr/bin/env python3
"""
Smarter fetcher - test ranges first to find where content exists
"""

import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from urllib.parse import urljoin
import time

BASE_URL = "https://mechanicape.nl/node/"
OUTPUT_DIR = "projects/theos-mechanische-aap"

def slugify(text):
    """Convert text to URL-safe slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]

def fetch_page(node_id):
    """Fetch a single page from mechanicape.nl"""
    try:
        url = f"{BASE_URL}{node_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if it's a valid article page
        title_elem = soup.find('h1')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        
        # Skip error pages, search pages, and navigation
        skip_words = ['Error', 'Zoeken', 'Zoekveld', 'Home', 'Projecten', 'Menu']
        if any(word in title for word in skip_words):
            return None
            
        # Get date - try multiple methods
        date_str = None
        
        # Method 1: Look for date pattern in text like "rein  ma, 11/10/2014 - 09:31"
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', response.text)
        if date_match:
            try:
                date_obj = datetime.strptime(date_match.group(1), '%m/%d/%Y')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                pass
        
        # Method 2: Look for date in different format
        if not date_str:
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', response.text)
            if date_match:
                date_str = date_match.group(0)
        
        if not date_str:
            date_str = '2015-01-01'  # Default fallback
        
        # Get content
        content_elems = soup.find_all(['p', 'div', 'li'])
        content_parts = []
        
        for elem in content_elems:
            text = elem.get_text(strip=True)
            # Skip navigation and metadata
            if len(text) > 20 and not any(skip in text for skip in ['Zoeken', 'Skip to', 'Home »', 'Deprecated']):
                content_parts.append(text)
        
        content = '\n\n'.join(content_parts)
        
        # Get images
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url and 'sites/default/files' in img_url:
                full_url = urljoin("https://mechanicape.nl", img_url)
                images.append(full_url)
        
        # Check if there's enough content
        if len(content) < 100:  # Minimum content length
            return None
        
        # Check if there are images
        if len(images) == 0:
            return None
            
        return {
            'title': title,
            'date': date_str,
            'content': content,
            'images': images,
            'node_id': node_id
        }
        
    except Exception as e:
        return None

def create_nrc_article(article):
    """Create an NRC-style HTML article"""
    
    title = article['title']
    date = article['date']
    content = article['content']
    images = article['images']
    
    # Create filename
    slug = slugify(title)
    filename = f"{date}-{slug}.html"
    
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 30]
    
    # Create HTML content
    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Theo's Mechanische Aap</title>
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.8;
            color: #1a1a1a;
            background: #f9f9f9;
        }}
        
        header {{
            border-bottom: 3px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 2.2em;
            font-weight: 700;
            margin: 0 0 10px 0;
            line-height: 1.2;
        }}
        
        .date {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        article {{
            background: white;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        p {{
            margin: 1.5em 0;
            text-align: justify;
            font-size: 1.1em;
        }}
        
        p:first-of-type::first-letter {{
            font-size: 3.5em;
            line-height: 0.8;
            float: left;
            margin: 0.1em 0.1em 0 0;
            font-weight: bold;
        }}
        
        .images {{
            margin: 30px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .images img {{
            width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 5px;
            background: white;
        }}
        
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}
        
        footer a {{
            color: #000;
            text-decoration: none;
            border-bottom: 1px solid #000;
        }}
        
        footer a:hover {{
            border-bottom: 2px solid #000;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p class="date">{date} - Theo's Mechanische Aap</p>
    </header>
    
    <article>
"""
    
    # Add paragraphs
    for i, para in enumerate(paragraphs[:10]):  # Limit to first 10 paragraphs
        html += f"        <p>{para}</p>\n\n"
    
    # Add images if available
    if images:
        html += '        <div class="images">\n'
        for img in images[:8]:  # Limit to 8 images
            html += f'            <img src="{img}" alt="Project afbeelding">\n'
        html += '        </div>\n\n'
    
    html += """    </article>
    
    <footer>
        <p><a href="../../sitemap.html">← Terug naar sitemap</a></p>
    </footer>
</body>
</html>
"""
    
    return filename, html

def main():
    """Main function to fetch all articles"""
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Starting smart scan of mechanicape.nl...")
    
    successful = 0
    
    # Strategy: Test in chunks to find where content exists
    # We know 2815, 2820, 2828, 2842, 2848 exist
    # Let's test broader ranges
    
    ranges_to_test = [
        (2800, 2900),   # Known good range
        (2700, 2800),
        (2600, 2700),
        (2500, 2600),
        (2400, 2500),
        (2300, 2400),
        (2200, 2300),
        (2100, 2200),
        (2000, 2100),
        (1, 100),       # Very early nodes
        (100, 500),
        (500, 1000),
        (1000, 2000),
    ]
    
    for start, end in ranges_to_test:
        print(f"\n=== Testing range {start}-{end} ===")
        range_found = 0
        
        for node_id in range(start, end + 1):
            article = fetch_page(node_id)
            
            if article:
                try:
                    filename, html = create_nrc_article(article)
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    
                    print(f"✓ Node {node_id}: {article['title']}")
                    successful += 1
                    range_found += 1
                    
                except Exception as e:
                    print(f"✗ Error creating article for node {node_id}: {e}")
            
            # Small delay to be nice to server
            time.sleep(0.05)
        
        print(f"Found {range_found} articles in range {start}-{end}")
        
        # If we found nothing in this range, skip similar ranges
        if range_found == 0 and end - start > 100:
            print(f"Skipping similar ranges...")
    
    print(f"\n=== Summary ===")
    print(f"Successfully created: {successful} articles")

if __name__ == '__main__':
    main()
