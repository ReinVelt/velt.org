#!/usr/bin/env python3
"""
Generate a static sitemap.html from the data/ folder structure
"""
import os
from pathlib import Path
from datetime import datetime

def format_size(bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def get_file_icon(filename):
    """Get emoji icon based on file extension"""
    ext = Path(filename).suffix.lower()
    if ext in ['.html', '.htm']:
        return '🌐'
    elif ext in ['.md', '.markdown']:
        return '📃'
    else:
        return '📄'

def scan_directory(path, base_path, indent=0):
    """Recursively scan directory and generate HTML list"""
    html = []
    
    try:
        items = sorted(os.listdir(path))
        
        # Separate folders and files
        folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        
        # Process folders first
        for folder in folders:
            folder_path = os.path.join(path, folder)
            rel_path = os.path.relpath(folder_path, base_path)
            
            html.append(f'\n<LI><SPAN class="folder-toggle collapsed">▶</SPAN> <B class="folder-name">{folder}</B>')
            html.append('\n<UL class="folder-content" style="display:none;">')
            
            # Recursively process subfolder
            html.extend(scan_directory(folder_path, base_path, indent + 1))
            
            html.append('\n</UL>')
            html.append('\n</LI>')
        
        # Process files
        for file in files:
            file_path = os.path.join(path, file)
            rel_path = os.path.relpath(file_path, base_path)
            size = os.path.getsize(file_path)
            
            html.append(f'\n<LI><A HREF="{rel_path}">{file}</A> <SMALL>({format_size(size)})</SMALL></LI>')
    
    except PermissionError:
        html.append('\n<LI><I>Permission denied</I></LI>')
    
    return html

def generate_sitemap():
    """Generate complete sitemap.html"""
    base_path = Path(__file__).parent
    
    # Folders to scan
    folders_to_scan = ['blog', 'cv', 'projects']
    
    # Generate the file structure HTML
    structure_html = []
    
    for folder in folders_to_scan:
        folder_path = base_path / folder
        if folder_path.exists():
            structure_html.append(f'\n<LI><SPAN class="folder-toggle collapsed">▶</SPAN> <B class="folder-name">{folder}</B>')
            structure_html.append('\n<UL class="folder-content" style="display:none;">')
            structure_html.extend(scan_directory(folder_path, base_path, 0))
            structure_html.append('\n</UL>')
            structure_html.append('\n</LI>')
    
    # Get generation timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Complete HTML template with responsive CSS
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rein's Cyberspaceplace - Site Map</title>
<style>
    * {{
        box-sizing: border-box;
    }}
    
    /* Elite background iframe */
    #elite-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
        z-index: -1;
        pointer-events: auto;
    }}
    
    body {{
        font-family: 'Courier New', 'Courier', monospace;
        line-height: 1.4;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1.5rem;
        background-color: transparent;
        color: #00ff00;
        text-shadow: 0 0 2px #00ff00;
        position: relative;
        z-index: 10;
    }}
    
    /* CRT scanlines effect */
    body::after {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, 0.15),
            rgba(0, 0, 0, 0.15) 1px,
            transparent 1px,
            transparent 2px
        );
        pointer-events: none;
        z-index: 9999;
    }}
    
    /* CRT vignette and curvature */
    html {{
        background: radial-gradient(ellipse at center, #000000 0%, #0a0a0a 50%, #000000 100%);
    }}
    
    html::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at center, transparent 0%, rgba(0, 0, 0, 0.7) 100%);
        pointer-events: none;
        z-index: 9998;
    }}
    
    h1 {{
        color: #00ff00;
        position: relative;
        z-index: 100;
        border-bottom: 1px solid #00ff00;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-size: clamp(1.2rem, 4vw, 1.8rem);
        font-weight: bold;
        letter-spacing: 0.05em;
    }}
    
    h1::before {{
        content: '> ';
    }}
    
    hr {{
        border: none;
        border-top: 1px solid #00ff00;
        margin: 2rem 0;
    }}
    
    ul {{
        list-style-type: none;
        padding-left: 0;
        margin-left: 0;
        position: relative;
        z-index: 100;
    }}
    
    ul ul {{
        padding-left: 2ch;
        margin-left: 0;
        border-left: 1px solid #006600;
    }}
    
    li {{
        margin: 0.2rem 0;
        padding: 0.1rem;
    }}
    
    .folder-toggle {{
        cursor: pointer;
        user-select: none;
        display: inline-block;
        width: 2ch;
        text-align: left;
        transition: none;
        color: #00ff00;
    }}
    
    .folder-toggle.expanded {{
        transform: none;
    }}
    
    .folder-toggle:hover {{
        color: #00ff00;
        background-color: #003300;
    }}
    
    .folder-name {{
        cursor: pointer;
        user-select: none;
    }}
    
    .folder-name:hover {{
        background-color: #003300;
    }}
    
    b {{
        color: #00ff00;
        font-size: 1em;
        display: inline-block;
        font-weight: bold;
    }}
    
    .folder-content {{
        overflow: hidden;
    }}
    
    a {{
        color: #00cc00;
        text-decoration: none;
        word-break: break-word;
        display: inline-block;
    }}
    
    a:hover {{
        background-color: #003300;
        color: #00ff00;
    }}
    
    a:visited {{
        color: #009900;
    }}
    
    small {{
        color: #008800;
        font-size: 0.9em;
        white-space: nowrap;
    }}
    
    .footer {{
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #00ff00;
        color: #00ff00;
        font-size: 0.9em;
    }}
    
    .back-link {{
        display: inline-block;
        margin-top: 1rem;
        padding: 0.3rem 1rem;
        background-color: #003300;
        color: #00ff00 !important;
        border: 1px solid #00ff00;
        text-decoration: none;
    }}
    
    .back-link:hover {{
        background-color: #00ff00;
        color: #000 !important;
    }}
    
    /* Blinking cursor effect */
    h1::after {{
        content: '█';
        animation: blink 1s infinite;
        margin-left: 0.2em;
    }}
    
    @keyframes blink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
    }}
    
    .disclaimer {{
        background-color: #001100;
        border: 1px solid #00ff00;
        padding: 0.5rem 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.9em;
    }}
    
    .disclaimer p {{
        margin: 0.3rem 0;
    }}
    
    /* Mobile optimizations */
    @media (max-width: 768px) {{
        body {{
            padding: 1rem;
            font-size: 0.9rem;
        }}
        
        ul ul {{
            padding-left: 1.5ch;
        }}
        
        h1 {{
            font-size: 1.4rem;
        }}
        
        small {{
            display: block;
            margin-top: 0.2rem;
        }}
    }}
    
    @media (max-width: 480px) {{
        body {{
            padding: 0.5rem;
            font-size: 0.85rem;
        }}
        
        ul ul {{
            padding-left: 1ch;
        }}
        
        li {{
            margin: 0.3rem 0;
        }}
    }}
</style>
</head>
<body>
<iframe id="elite-bg" src="elite.html"></iframe>
<h1>Rein's Cyberspaceplace - Site Map</h1>
<div class="disclaimer">
<p>This is the personal website of Rein Velt. A space for experiments, ideas, and projects — shared freely, without expectation of response, liking, or sharing.</p>
</div>
<ul>{''.join(structure_html)}
</ul>
<div class="footer">
<p><small>Last sitemap update: {timestamp}</small></p>
<a href="index.html" class="back-link">Back to Intro</a>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const eliteIframe = document.getElementById('elite-bg');
    
    // Track if mouse is over interactive content
    let isOverContent = false;
    
    // Detect when mouse enters/leaves content areas
    document.addEventListener('mouseover', function(e) {{
        // Check if mouse is over text content, links, or interactive elements
        if (e.target.closest('h1, ul, li, a, p, .disclaimer, .footer')) {{
            isOverContent = true;
            // Fade out vizier when over content
            eliteIframe.contentWindow.postMessage({{
                type: 'vizierOpacity',
                opacity: 0.15
            }}, '*');
        }}
    }});
    
    document.addEventListener('mouseout', function(e) {{
        // Check if we're leaving content areas
        if (!e.relatedTarget || !e.relatedTarget.closest('h1, ul, li, a, p, .disclaimer, .footer')) {{
            isOverContent = false;
            // Restore vizier when leaving content
            eliteIframe.contentWindow.postMessage({{
                type: 'vizierOpacity',
                opacity: 1.0
            }}, '*');
        }}
    }});
    
    // Add click handlers to all folder toggles and names
    document.querySelectorAll('.folder-toggle, .folder-name').forEach(function(element) {{
        element.addEventListener('click', function(e) {{
            e.stopPropagation();
            
            // Find the parent LI element (case-insensitive)
            let li = this.parentElement;
            while (li && li.tagName.toUpperCase() !== 'LI') {{
                li = li.parentElement;
            }}
            
            if (!li) return;
            
            // Find the toggle and content elements
            const toggle = li.querySelector('.folder-toggle');
            const content = li.querySelector('.folder-content');
            
            if (content) {{
                // Toggle visibility
                if (content.style.display === 'none') {{
                    content.style.display = 'block';
                    toggle.classList.remove('collapsed');
                    toggle.classList.add('expanded');
                }} else {{
                    content.style.display = 'none';
                    toggle.classList.remove('expanded');
                    toggle.classList.add('collapsed');
                }}
            }}
        }});
    }});
}});
</script>
</body>
</html>
"""
    
    # Write to sitemap.html
    output_path = Path(__file__).parent / 'sitemap.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ Generated sitemap.html ({format_size(output_path.stat().st_size)})")
    print(f"  Timestamp: {timestamp}")

if __name__ == '__main__':
    generate_sitemap()
