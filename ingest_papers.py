#!/usr/bin/env python3
"""
Ingest robotics papers into the research-ingest repository.
Creates markdown files for each paper and commits to git.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
REPO_DIR = Path.home() / '.openclaw' / 'workspace' / 'research-ingest'
PAPERS_DIR = REPO_DIR / 'papers'
PAPERS_FILE = Path.home() / '.openclaw' / 'workspace' / 'papers' / f'today_papers_{datetime.now().strftime("%Y-%m-%d")}.json'

def ensure_dirs():
    """Create necessary directories."""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    # Create year directory
    year = datetime.now().strftime('%Y')
    (PAPERS_DIR / year).mkdir(exist_ok=True)

def paper_to_markdown(paper):
    """Convert paper data to markdown format."""
    title = paper.get('title', 'No title')
    arxiv_id = paper.get('id', '')
    summary = paper.get('summary', 'No abstract')
    url = paper.get('url', '')
    published = paper.get('published', 'unknown')
    authors = paper.get('authors', [])

    # Extract date from arxiv_id or use published date
    # Format: YYMM.version (e.g., 2603.12263v1)
    if '.' in arxiv_id:
        yymm = arxiv_id.split('.')[0][:4]
        date = f"20{yymm[:2]}-{yymm[2:4]}-01"
    else:
        date = published

    # Format date string for filename
    try:
        date_obj = datetime.strptime(published, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y-%m-%d')
    except:
        date_str = published

    filename = f"{date_str}-{arxiv_id.replace('/', '_')}.md"
    year_dir = date_str[:4]
    filepath = PAPERS_DIR / year_dir / filename

    # Clean title for markdown (remove LaTeX)
    title_clean = title.replace('$', '').replace('\\', '')

    # Format authors
    if len(authors) > 5:
        authors_str = ', '.join(authors[:5]) + f' +{len(authors)-5}'
    else:
        authors_str = ', '.join(authors)

    # Build markdown content
    md_content = f"""# {title_clean}

**arXiv ID:** {arxiv_id}  
**Published:** {published}  
**Authors:** {authors_str}  
**Link:** [{url}]({url})

## Abstract

{summary}

## Metadata

- **Source:** arXiv Robotics (cs.RO)
- **Ingested:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tags:** robotics, arXiv

---
*Ingested by quack quack*
"""

    return md_content, filepath

def ingest_papers():
    """Read papers from JSON and create markdown files."""
    ensure_dirs()

    if not PAPERS_FILE.exists():
        print(f"No papers file found: {PAPERS_FILE}", file=sys.stderr)
        return 0

    with open(PAPERS_FILE) as f:
        papers_data = json.load(f)

    papers = papers_data.get('papers', [])
    count = 0

    for paper in papers:
        md_content, filepath = paper_to_markdown(paper)

        # Skip if already exists
        if filepath.exists():
            print(f"Already exists: {filepath.name}", file=sys.stderr)
            continue

        # Write markdown file
        filepath.write_text(md_content)
        print(f"Created: {filepath.name}", file=sys.stderr)
        count += 1

    return count

def main():
    print("Ingesting papers...", file=sys.stderr)
    count = ingest_papers()
    print(f"Ingested {count} papers", file=sys.stderr)

    if count > 0:
        # Commit changes
        os.chdir(REPO_DIR)
        os.system(f'git add papers/ && git commit -m "ingest: add {count} new papers"')
        os.system('git push')

    return count

if __name__ == '__main__':
    sys.exit(main())
