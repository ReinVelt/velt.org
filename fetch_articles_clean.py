#!/usr/bin/env python3
"""
Fetch articles from mechanicape.nl with clean content extraction
Only creates files with substantial content for NRC-style articles
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

def extract_clean_content(soup):
    """Extract clean article content, filtering out navigation and metadata"""
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Remove error messages and navigation
    for element in soup.find_all(string=re.compile(r'Deprecated function|Skip to|Zoekveld|Zoeken|Home »|Error message|session_set_save_handler')):
        if element.parent:
            element.parent.decompose()
    
    # Find main content area - try multiple selectors
    content_area = (
        soup.find('div', class_='field-item') or
        soup.find('section', id='main-content') or 
        soup.find('main') or 
        soup.find('article') or 
        soup.find('div', class_='content')
    )
    
    if not content_area:
        return "", []
    
    # Extract paragraphs
    paragraphs = []
    seen_paragraphs = set()
    
    for elem in content_area.find_all(['p', 'div', 'li', 'h2', 'h3', 'h4']):
        text = elem.get_text(strip=True)
        
        # Skip if too short or is navigation
        if len(text) < 30:
            continue
        
        # Skip navigation patterns
        skip_patterns = [
            'Zoeken', 'Skip to', 'Home »', 'Blogs »', 'Projecten',
            'Deprecated', 'session_set_save', 'blog van rein',
            'Error message', 'ma,', 'di,', 'wo,', 'do,', 'vr,', 'za,', 'zo,'
        ]
        
        if any(pattern in text for pattern in skip_patterns):
            continue
        
        # Remove date prefix patterns like "rein  ma, 11/10/2014 - 09:31"
        text = re.sub(r'^.*?\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2}', '', text).strip()
        text = re.sub(r'^(rein|theo|admin)\s+', '', text, flags=re.IGNORECASE).strip()
        
        # Avoid duplicates
        text_key = text[:100].lower()
        if text_key in seen_paragraphs:
            continue
        
        if len(text) >= 30:
            seen_paragraphs.add(text_key)
            paragraphs.append(text)
    
    content = '\n\n'.join(paragraphs)
    
    # Extract links
    links = []
    for link in content_area.find_all('a', href=True):
        href = link['href']
        link_text = link.get_text(strip=True)
        if href and link_text and len(link_text) > 3:
            if not any(skip in href for skip in ['javascript:', '#', 'mailto:']):
                links.append({'text': link_text, 'url': href})
    
    return content, links

def fetch_page(node_id):
    """Fetch a single page from mechanicape.nl"""
    try:
        url = f"{BASE_URL}{node_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title
        title_elem = soup.find('h1')
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        
        # Skip error pages and navigation
        skip_words = ['Error', 'Zoeken', 'Zoekveld', 'Home', 'Projecten', 'Menu', 'Page not found']
        if any(word in title for word in skip_words):
            return None
        
        # Extract clean content and links
        content, links = extract_clean_content(soup)
        
        # Must have substantial content (at least 150 chars for NRC column)
        if len(content) < 150:
            return None
        
        # Get date
        date_str = None
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', response.text)
        if date_match:
            try:
                date_obj = datetime.strptime(date_match.group(1), '%m/%d/%Y')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                pass
        
        if not date_str:
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', response.text)
            if date_match:
                date_str = date_match.group(0)
        
        if not date_str:
            date_str = '2015-01-01'
        
        # Get images
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url and 'sites/default/files' in img_url:
                # Skip logo images
                if 'apekoplogo' in img_url or 'logo' in img_url.lower():
                    continue
                full_url = urljoin("https://mechanicape.nl", img_url)
                images.append(full_url)
        
        # Get file attachments
        attachments = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(ext in href.lower() for ext in ['.pdf', '.zip', '.tar', '.gz', '.doc', '.xls']):
                full_url = urljoin("https://mechanicape.nl", href)
                link_text = link.get_text(strip=True) or os.path.basename(href)
                attachments.append({'url': full_url, 'text': link_text})
        
        return {
            'title': title,
            'date': date_str,
            'content': content,
            'images': images,
            'links': links,
            'attachments': attachments,
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
    links = article['links']
    attachments = article['attachments']
    
    # Create filename
    slug = slugify(title)
    filename = f"{date}-{slug}.html"
    
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 30]
    
    # Limit to reasonable article length
    paragraphs = paragraphs[:15]
    
    # Create HTML
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
        
        .links, .attachments {{
            margin: 20px 0;
            padding: 20px;
            background: #f5f5f5;
            border-left: 3px solid #333;
        }}
        
        .links h3, .attachments h3 {{
            margin: 0 0 10px 0;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .links ul, .attachments ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .links li, .attachments li {{
            margin: 5px 0;
        }}
        
        .links a, .attachments a {{
            color: #000;
            text-decoration: none;
            border-bottom: 1px solid #666;
        }}
        
        .links a:hover, .attachments a:hover {{
            border-bottom: 2px solid #000;
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
    for para in paragraphs:
        # Escape HTML characters
        para_escaped = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html += f"        <p>{para_escaped}</p>\n\n"
    
    # Add images
    if images:
        html += '        <div class="images">\n'
        for img in images[:8]:
            html += f'            <img src="{img}" alt="Project afbeelding" loading="lazy">\n'
        html += '        </div>\n\n'
    
    # Add links
    if links:
        html += '        <div class="links">\n'
        html += '            <h3>Gerelateerde links</h3>\n'
        html += '            <ul>\n'
        for link in links[:10]:
            html += f'                <li><a href="{link["url"]}" target="_blank">{link["text"]}</a></li>\n'
        html += '            </ul>\n'
        html += '        </div>\n\n'
    
    # Add attachments
    if attachments:
        html += '        <div class="attachments">\n'
        html += '            <h3>Bestanden</h3>\n'
        html += '            <ul>\n'
        for att in attachments:
            html += f'                <li><a href="{att["url"]}" target="_blank">{att["text"]}</a></li>\n'
        html += '            </ul>\n'
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
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Starting clean article extraction from mechanicape.nl...")
    print("Filtering for substantial content (NRC-style columns)...\n")
    
    successful = 0
    
    # Test ranges where content exists
    ranges_to_test = [
        (2800, 2900),
        (2700, 2800),
        (2600, 2700),
        (2500, 2600),
        (2400, 2500),
        (2300, 2400),
        (2200, 2300),
        (2100, 2200),
        (2000, 2100),
        (1900, 2000),
        (1800, 1900),
        (1, 500),
        (500, 1000),
        (1000, 1500),
        (1500, 2000),
    ]
    
    for start, end in ranges_to_test:
        print(f"\n=== Scanning range {start}-{end} ===")
        range_found = 0
        
        for node_id in range(start, end + 1):
            article = fetch_page(node_id)
            
            if article:
                try:
                    filename, html = create_nrc_article(article)
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    
                    img_count = len(article['images'])
                    link_count = len(article['links'])
                    att_count = len(article['attachments'])
                    
                    print(f"✓ {node_id}: {article['title'][:60]}")
                    print(f"  → {filename}")
                    print(f"  → {len(article['content'])} chars, {img_count} imgs, {link_count} links, {att_count} files")
                    
                    successful += 1
                    range_found += 1
                    
                except Exception as e:
                    print(f"✗ Error creating article for node {node_id}: {e}")
            
            time.sleep(0.05)
        
        if range_found > 0:
            print(f"✓ Found {range_found} articles in this range")
        else:
            print(f"  (No articles found)")
    
    print(f"\n{'='*60}")
    print(f"Successfully created {successful} NRC-style articles")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
