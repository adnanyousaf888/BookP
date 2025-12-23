# scraper/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from settings import ROOT_URL

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def is_internal(href: str) -> bool:
  if not href:
    return False
  if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
    return False

  root = urlparse(ROOT_URL)
  full = urljoin(ROOT_URL, href)
  parsed = urlparse(full)

  return parsed.netloc == root.netloc


def normalize(url: str) -> str:
  parsed = urlparse(url)
  return parsed._replace(fragment="", query="").geturl()


def get_links(url: str):
  try:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
  except Exception as e:
    print(f"❌ Failed to load {url}: {e}")
    return []

  soup = BeautifulSoup(response.text, "html.parser")
  links = set()

  for a in soup.find_all("a", href=True):
    href = a["href"]
    if is_internal(href):
      absolute = normalize(urljoin(ROOT_URL, href))
      links.add(absolute)

  return list(links)


def crawl_website():
  visited = set()
  to_visit = {normalize(ROOT_URL)}
  all_pages = []

  print(f"🌐 Starting crawl: {ROOT_URL}")

  while to_visit:
    url = to_visit.pop()
    if url in visited:
      continue

    visited.add(url)
    all_pages.append(url)
    print(f"📄 Crawling: {url}")

    new_links = get_links(url)
    for link in new_links:
      if link not in visited:
        to_visit.add(link)

  print(f"\n✅ Total pages found: {len(all_pages)}")
  return all_pages
