#!/usr/bin/env python3
"""
Generate index.html with embedded article metadata for the archief folder
"""

import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

ARCHIEF_DIR = "projects/theos-mechanische-aap-archief"

def extract_article_metadata(filepath):
    """Extract metadata from an article HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        title = soup.find('h1')
        title = title.get_text(strip=True) if title else 'Untitled'
        
        date = soup.find(class_='date')
        date = date.get_text(strip=True) if date else ''
        
        # Get first paragraph
        first_p = soup.select_one('article p')
        excerpt = first_p.get_text(strip=True)[:200] if first_p else ''
        
        # Get first image
        first_img = soup.select_one('article img')
        image = first_img['src'] if first_img and first_img.get('src') else ''
        
        # Count media
        images = len(soup.select('article img'))
        links = len(soup.select('.links a'))
        attachments = len(soup.select('.attachments a'))
        
        # Extract date for sorting
        filename = os.path.basename(filepath)
        sort_date = filename[:10] if filename[:4].isdigit() else '1900-01-01'
        
        return {
            'href': filename,
            'title': title,
            'date': date,
            'excerpt': excerpt,
            'image': image,
            'images': images,
            'links': links,
            'attachments': attachments,
            'sortDate': sort_date
        }
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def generate_index():
    """Generate index.html with embedded article data"""
    
    # Find all article HTML files
    articles = []
    for filename in os.listdir(ARCHIEF_DIR):
        if filename.endswith('.html') and filename != 'index.html':
            filepath = os.path.join(ARCHIEF_DIR, filename)
            metadata = extract_article_metadata(filepath)
            if metadata:
                articles.append(metadata)
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x['sortDate'], reverse=True)
    
    # Convert to JSON
    articles_json = json.dumps(articles, ensure_ascii=False, indent=2)
    
    # Create HTML
    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Theo's Mechanische Aap - Archief</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            background: #f5f5f5;
            color: #1a1a1a;
        }}
        
        header {{
            background: #000;
            color: #fff;
            padding: 40px 20px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.8;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .article-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        
        .article-image {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            background: #e0e0e0;
            display: block;
        }}
        
        .article-content {{
            padding: 25px;
        }}
        
        .article-date {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .article-title {{
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 15px;
            line-height: 1.3;
            color: #000;
        }}
        
        .article-excerpt {{
            font-size: 1em;
            line-height: 1.6;
            color: #444;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .article-meta {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            font-size: 0.85em;
            color: #999;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #666;
        }}
        
        footer {{
            text-align: center;
            padding: 40px 20px;
            background: #000;
            color: #fff;
            margin-top: 60px;
        }}
        
        footer a {{
            color: #fff;
            text-decoration: none;
            border-bottom: 1px solid #fff;
            padding-bottom: 2px;
        }}
        
        footer a:hover {{
            border-bottom: 2px solid #fff;
        }}
        
        @media (max-width: 768px) {{
            .articles-grid {{
                grid-template-columns: 1fr;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Theo's Mechanische Aap</h1>
        <p>Archief 2009-2020 • {len(articles)} Artikelen</p>
    </header>
    
    <div class="container">
        <div class="articles-grid" id="articlesGrid"></div>
        <div class="loading" id="loading" style="display: none;">Meer artikelen laden...</div>
    </div>
    
    <footer>
        <p><a href="../../sitemap.html">← Terug naar sitemap</a></p>
    </footer>
    
    <script>
        // Article data embedded directly
        const allArticles = {articles_json};
        
        let displayedArticles = 0;
        const articlesPerLoad = 12;
        
        function createArticleCard(article) {{
            const card = document.createElement('div');
            card.className = 'article-card';
            card.onclick = () => window.location.href = article.href;
            
            const imageHtml = article.image 
                ? `<img src="${{article.image}}" alt="${{article.title}}" class="article-image" loading="lazy">`
                : `<div class="article-image" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></div>`;
            
            const metaParts = [];
            if (article.images > 0) metaParts.push(`${{article.images}} foto's`);
            if (article.links > 0) metaParts.push(`${{article.links}} links`);
            if (article.attachments > 0) metaParts.push(`${{article.attachments}} bestanden`);
            
            card.innerHTML = `
                ${{imageHtml}}
                <div class="article-content">
                    <div class="article-date">${{article.date}}</div>
                    <h2 class="article-title">${{article.title}}</h2>
                    <p class="article-excerpt">${{article.excerpt}}</p>
                    ${{metaParts.length > 0 ? `<div class="article-meta">${{metaParts.join(' • ')}}</div>` : ''}}
                </div>
            `;
            
            return card;
        }}
        
        function displayMoreArticles() {{
            const grid = document.getElementById('articlesGrid');
            const toDisplay = allArticles.slice(displayedArticles, displayedArticles + articlesPerLoad);
            
            toDisplay.forEach(article => {{
                grid.appendChild(createArticleCard(article));
            }});
            
            displayedArticles += toDisplay.length;
            
            // Hide loading indicator if all articles are displayed
            if (displayedArticles >= allArticles.length) {{
                document.getElementById('loading').style.display = 'none';
            }}
        }}
        
        // Infinite scroll
        function checkScroll() {{
            if (displayedArticles >= allArticles.length) return;
            
            const loading = document.getElementById('loading');
            const rect = loading.getBoundingClientRect();
            
            if (rect.top < window.innerHeight + 200) {{
                displayMoreArticles();
            }}
        }}
        
        // Initialize
        function init() {{
            document.getElementById('loading').style.display = 'block';
            displayMoreArticles();
            
            window.addEventListener('scroll', checkScroll);
            window.addEventListener('resize', checkScroll);
        }}
        
        init();
    </script>
</body>
</html>
"""
    
    # Write index.html
    index_path = os.path.join(ARCHIEF_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated index.html with {len(articles)} articles")
    print(f"  Location: {index_path}")

if __name__ == '__main__':
    generate_index()
