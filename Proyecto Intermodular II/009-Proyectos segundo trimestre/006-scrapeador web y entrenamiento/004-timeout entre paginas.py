import requests
import os
import hashlib
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin, urlunparse
from collections import deque

from bs4 import BeautifulSoup

# -------------------- CONFIGURATION --------------------
START_URL = "https://tameformacion.com/"
OUTPUT_FOLDER = "paginas_html"
MAX_PAGES = 200                     # Safety limit
REQUEST_DELAY_SECONDS = 1          # <<< Delay between pages
# -------------------------------------------------------


# ---------- Helpers for filenames ----------

def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if "." in path:
        return path

    if path:
        return path + ".html"

    return ""


def generate_hash_filename(url: str) -> str:
    sha1 = hashlib.sha1(url.encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{sha1}_{timestamp}.html"


def get_output_path_for_url(url: str) -> str:
    filename = get_filename_from_url(url)
    if not filename:
        filename = generate_hash_filename(url)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    return os.path.join(OUTPUT_FOLDER, filename)


# ---------- Helpers for normalization / filtering ----------

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    parsed = parsed._replace(fragment="")
    return urlunparse(parsed)


def same_domain(url1: str, url2: str) -> bool:
    n1 = urlparse(url1).netloc.lower()
    n2 = urlparse(url2).netloc.lower()

    if n1.startswith("www."):
        n1 = n1[4:]
    if n2.startswith("www."):
        n2 = n2[4:]

    return n1 == n2


def is_interesting_link(href: str) -> bool:
    if not href:
        return False
    href = href.strip()
    if href.startswith("#"):
        return False
    if href.startswith("mailto:"):
        return False
    if href.startswith("tel:"):
        return False
    if href.lower().startswith("javascript:"):
        return False
    return True


# ---------- Main crawler ----------

def crawl(start_url: str):
    visited = set()
    queue = deque([start_url])

    while queue and len(visited) < MAX_PAGES:
        current_url = queue.popleft()
        current_url = normalize_url(current_url)

        if current_url in visited:
            continue

        print(f"[{len(visited)+1}] Fetching: {current_url}")
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {current_url}: {e}")
            continue

        # Respect delay between requests
        print(f"  Waiting {REQUEST_DELAY_SECONDS} seconds...")
        time.sleep(REQUEST_DELAY_SECONDS)

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            print(f"  Skipping non-HTML content: {content_type}")
            continue

        html_content = response.text

        filepath = get_output_path_for_url(current_url)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"  Saved to: {filepath}")
        except OSError as e:
            print(f"  Error saving {filepath}: {e}")

        soup = BeautifulSoup(html_content, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not is_interesting_link(href):
                continue

            new_url = urljoin(current_url, href)
            new_url = normalize_url(new_url)

            if same_domain(start_url, new_url) and new_url not in visited:
                queue.append(new_url)


if __name__ == "__main__":
    crawl(START_URL)
    print("Crawl finished.")

