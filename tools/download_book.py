"""
download_book.py — Download the primary source book from tamilvu.org.

Downloads all pages of தமிழ் நடைக் கையேடு (bookid=169, pp.36-101)
and saves them as local text files with Tamil content preserved.

Usage:
    python Tamil_Nadai/tools/download_book.py

Output:
    Tamil_Nadai/.tmp/book_pages/page_036.txt through page_101.txt
    Tamil_Nadai/.tmp/book_pages/page_036.html through page_101.html (raw)
"""

import sys
import time
import re
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install requests beautifulsoup4")
    sys.exit(1)

sys.stdout.reconfigure(encoding="utf-8")

BOOK_ID = 169
START_PAGE = 36
END_PAGE = 101
BASE_URL = "http://www.tamilvu.org/slet/lA100/lA100pd3.jsp"

# Output dirs
PROJECT_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = PROJECT_DIR / ".tmp" / "book_pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)


def extract_text(html: str) -> str:
    """Extract Tamil content from tamilvu.org HTML.

    The site uses malformed HTML (body inside head) with content in
    <td class="head|phead|disc|pno"> elements inside nested tables.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Content CSS classes used by tamilvu.org
    CONTENT_CLASSES = {"head", "phead", "disc", "pno"}

    sections = []
    for td in soup.find_all("td"):
        css_class = td.get("class", [])
        if not css_class:
            continue
        cls = css_class[0] if isinstance(css_class, list) else css_class
        if cls not in CONTENT_CLASSES:
            continue

        text = td.get_text(separator="\n", strip=False)
        # Clean up whitespace within the cell
        lines = []
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        cell_text = "\n".join(lines)

        if not cell_text:
            continue

        # Add formatting markers
        if cls == "pno":
            sections.append(f"[Page {cell_text}]")
        elif cls == "head":
            sections.append(f"\n{'=' * 50}\n{cell_text}\n{'=' * 50}")
        elif cls == "phead":
            sections.append(f"\n--- {cell_text} ---")
        else:  # disc
            sections.append(cell_text)

    return "\n\n".join(sections).strip()


def fetch_page(page_num: int) -> str:
    """Fetch a single page HTML from tamilvu.org."""
    url = f"{BASE_URL}?bookid={BOOK_ID}&pno={page_num}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TamilNadai-Research/1.0",
        "Accept-Charset": "utf-8",
    }

    resp = requests.get(url, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    return resp.text


def main():
    total = END_PAGE - START_PAGE + 1
    downloaded = 0
    extracted = 0
    failed = []

    print(f"Downloading {total} pages from tamilvu.org (bookid={BOOK_ID})")
    print(f"Pages {START_PAGE} to {END_PAGE}")
    print(f"Output: {PAGES_DIR}")
    print()

    for page_num in range(START_PAGE, END_PAGE + 1):
        txt_path = PAGES_DIR / f"page_{page_num:03d}.txt"
        html_path = PAGES_DIR / f"page_{page_num:03d}.html"

        # Step 1: Download HTML if not already present
        if not html_path.exists() or html_path.stat().st_size < 100:
            try:
                raw_html = fetch_page(page_num)
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(raw_html)
                downloaded += 1
                time.sleep(0.5)  # Be polite to the server
            except Exception as e:
                print(f"  Page {page_num}: DOWNLOAD FAILED — {e}")
                failed.append(page_num)
                continue

        # Step 2: Extract text from HTML (always re-extract)
        try:
            raw_html = html_path.read_text(encoding="utf-8")
            text = extract_text(raw_html)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"# Page {page_num} — தமிழ் நடைக் கையேடு (bookid={BOOK_ID})\n\n")
                f.write(text)
                f.write("\n")

            tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
            print(f"  Page {page_num}: {len(text):>5} chars, {tamil_chars:>4} Tamil — OK")
            extracted += 1

        except Exception as e:
            print(f"  Page {page_num}: EXTRACT FAILED — {e}")
            failed.append(page_num)

    print(f"\nDone: {extracted}/{total} pages extracted ({downloaded} newly downloaded)")
    if failed:
        print(f"Failed pages: {failed}")

    # Summary of what we got
    print(f"\nFiles saved to: {PAGES_DIR}")
    txt_files = sorted(PAGES_DIR.glob("page_*.txt"))
    total_chars = 0
    total_tamil = 0
    for f in txt_files:
        content = f.read_text(encoding="utf-8")
        total_chars += len(content)
        total_tamil += len(re.findall(r'[\u0B80-\u0BFF]', content))
    print(f"Total: {len(txt_files)} text files, {total_chars:,} chars, {total_tamil:,} Tamil chars")


if __name__ == "__main__":
    main()
