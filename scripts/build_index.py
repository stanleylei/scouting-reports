import os
import re
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scouting Reports Dashboard</title>
    <meta name="description" content="Baseball Scout Helper - Advanced Analytics & Team Reports">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover-border: rgba(94, 234, 212, 0.4);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-glow: rgba(94, 234, 212, 0.15);
            --accent-text: #5eead4;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(94, 234, 212, 0.04) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.04) 0%, transparent 50%);
            background-attachment: fixed;
        }}

        header {{
            padding: 4rem 2rem 2rem;
            text-align: center;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        p.subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 300;
        }}

        main {{
            flex: 1;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-text), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-4px);
            border-color: var(--card-hover-border);
            box-shadow: 0 10px 30px -10px var(--accent-glow);
        }}

        .card:hover::before {{
            opacity: 1;
        }}

        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1.4;
        }}

        .card-date {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .card-icon {{
            width: 20px;
            height: 20px;
            color: var(--accent-text);
            opacity: 0.8;
            transition: transform 0.3s ease;
        }}

        .card:hover .card-icon {{
            transform: translateX(4px);
            opacity: 1;
        }}

        footer {{
            padding: 2rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.875rem;
            border-top: 1px solid var(--card-border);
            margin-top: auto;
        }}

        @media (max-width: 600px) {{
            header {{
                padding: 3rem 1.5rem 1.5rem;
            }}
            h1 {{
                font-size: 2.25rem;
            }}
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Scouting Intelligence</h1>
        <p class="subtitle">Advanced Analytics & Team Reports</p>
    </header>
    
    <main>
        <div class="grid">
            {cards_html}
        </div>
    </main>

    <footer>
        &copy; {year} Baseball Scout Helper. Automatically generated.
    </footer>
</body>
</html>
"""

CARD_TEMPLATE = """
            <a href="{file_path}" class="card">
                <div class="card-header">
                    <h2 class="card-title">{team_name}</h2>
                    <svg class="card-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                </div>
                <div class="card-date">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    {date_str}
                </div>
            </a>
"""

def parse_filename(filepath):
    basename = os.path.basename(filepath)
    # Example: Combat_Baseball_Academy_8U_-_Allen_8U_20260503_103036.html
    match = re.search(r'^(.*?)_(\d{8}_\d{6})\.html$', basename)
    
    if match:
        team_part = match.group(1)
        date_part = match.group(2)
        
        # Clean up team name
        team_name = team_part.replace('_-_', ' - ').replace('_', ' ')
        
        # Parse date
        try:
            dt = datetime.strptime(date_part, "%Y%m%d_%H%M%S")
            # Format: May 03, 2026 &bull; 10:30 AM
            date_str = dt.strftime("%b %d, %Y &bull; %I:%M %p")
            sort_key = dt
        except ValueError:
            date_str = date_part
            sort_key = datetime.min
    else:
        # Fallback if pattern doesn't match
        team_name = basename.replace('.html', '').replace('_', ' ')
        date_str = "Unknown Date"
        sort_key = datetime.min
        
    # Ensure forward slashes for URLs even on Windows
    url_path = filepath.replace('\\', '/')
        
    return {
        "file_path": url_path,
        "team_name": team_name,
        "date_str": date_str,
        "sort_key": sort_key
    }

def main():
    # When running in GitHub Actions, the script will run from the root of the repository.
    root_dir = "."
    reports_dir = os.path.join(root_dir, "reports")
    
    files = []
    if os.path.exists(reports_dir):
        for root, _, filenames in os.walk(reports_dir):
            for f in filenames:
                if f.endswith('.html'):
                    # Path relative to root_dir
                    files.append(os.path.relpath(os.path.join(root, f), root_dir))
    
    reports = []
    for f in files:
        reports.append(parse_filename(f))
        
    # Sort by date, newest first
    reports.sort(key=lambda x: x["sort_key"], reverse=True)
    
    cards_html = ""
    for r in reports:
        cards_html += CARD_TEMPLATE.format(
            file_path=r["file_path"],
            team_name=r["team_name"],
            date_str=r["date_str"]
        )
        
    # Handle empty state
    if not reports:
        cards_html = "<div class='card' style='grid-column: 1 / -1; text-align: center; padding: 3rem;'><p style='color: var(--text-secondary);'>No scouting reports available yet.</p></div>"
        
    final_html = HTML_TEMPLATE.format(
        cards_html=cards_html,
        year=datetime.now().year
    )
    
    with open(os.path.join(root_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"Successfully generated index.html with {len(reports)} reports.")

if __name__ == "__main__":
    main()
