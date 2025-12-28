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
MAX_PAGES = 200              # Safety limit
REQUEST_DELAY_SECONDS = 1    # Delay between requests
# -------------------------------------------------------


# ---------- Helpers for filenames ----------

def get_filename_from_url(url: str) -> str:
    """
    Try to extract a filename from the URL path.
    If the path contains a dot, we assume it has an extension (e.g. .html, .php, .pdf).
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")  # OJO: no strip(), solo lstrip para conservar subcarpetas

    if "." in os.path.basename(path):
        # Si la última parte tiene extensión, devolvemos toda la ruta relativa
        return path  # p.ej. wp-content/uploads/2023/12/GD_xxx.pdf

    if path:
        # No hay extensión explícita, asumimos HTML y mantenemos ruta
        return os.path.join(path, "index.html") if path.endswith("/") else path + ".html"

    # Raíz del sitio → nombre por defecto
    return ""


def generate_hash_filename(url: str, ext: str = ".html") -> str:
    """
    Generates filename using SHA-1 hash of the URL + datetime, with the given extension.
    """
    sha1 = hashlib.sha1(url.encode()).hexdigest()[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not ext.startswith("."):
        ext = "." + ext
    return f"{sha1}_{timestamp}{ext}"


def get_output_path_for_url(url: str, content_type: str | None = None) -> str:
    """
    Decide the filename based on the URL and content type.
    - If URL already has a filename/path, use it.
    - If not, use hash + datetime with appropriate extension.
    """
    filename = get_filename_from_url(url)

    if not filename:
        # Decide extension based on content-type
        ext = ".html"
        if content_type:
            ct = content_type.lower()
            if "pdf" in ct:
                ext = ".pdf"
        filename = generate_hash_filename(url, ext=ext)

    # Ruta absoluta final
    full_path = os.path.join(OUTPUT_FOLDER, filename)

    # Asegurar que existe el directorio padre (paginas_html + posibles subcarpetas)
    parent_dir = os.path.dirname(full_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    return full_path


# ---------- Helpers for normalization / filtering ----------

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # Remove fragment (#...)
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
        ct_lower = content_type.lower()

        # -------- Save PDF files --------
        if "application/pdf" in ct_lower or current_url.lower().endswith(".pdf"):
            filepath = get_output_path_for_url(current_url, content_type=content_type)
            try:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"  [PDF] Saved to: {filepath}")
            except OSError as e:
                print(f"  Error saving PDF {filepath}: {e}")
            # No parse links inside PDF
            continue

        # -------- Process HTML pages --------
        if "text/html" in ct_lower:
            html_content = response.text

            filepath = get_output_path_for_url(current_url, content_type=content_type)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"  [HTML] Saved to: {filepath}")
            except OSError as e:
                print(f"  Error saving HTML {filepath}: {e}")
                continue

            # Parse links and enqueue same-domain URLs
            soup = BeautifulSoup(html_content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if not is_interesting_link(href):
                    continue

                new_url = urljoin(current_url, href)
                new_url = normalize_url(new_url)

                if same_domain(start_url, new_url) and new_url not in visited:
                    queue.append(new_url)

        else:
            # Non-HTML, non-PDF content (images, css, etc.) → ignore
            print(f"  Skipping content type: {content_type}")

    print("Crawl finished.")


if __name__ == "__main__":
    crawl(START_URL)

