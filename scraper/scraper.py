# scraper/scraper.py

import requests
from scraper.cleaner import clean_html   # you already have this file
from database.mongo import insert_document
from scraper.crawler import HEADERS
from embeddings.embedder import embed_text


def scrape_and_store(urls):

  seen_pages = set()

  for url in urls:
    print(f"\n🔎 Processing page: {url}")

    try:
      response = requests.get(url, headers=HEADERS, timeout=25)
      response.raise_for_status()
    except Exception as e:
      print(f"❌ Could not fetch {url}: {e}")
      continue

    cleaned_text = clean_html(response.text)

    if len(cleaned_text) < 80:
      print("⚠️ Skipped (too little content)")
      continue

    normalized = " ".join(cleaned_text.split()).lower()
    if normalized in seen_pages:
      print("⚠️ Skipped (duplicate page)")
      continue

    seen_pages.add(normalized)

    try:
      page_embedding = embed_text(cleaned_text)
    except Exception as e:
      print(f"⚠️ Failed to embed page {url}: {e}")
      continue

    document = {
      "url": url,
      "text": cleaned_text,
      "embedding": page_embedding,
    }

    insert_document(document)
    print(f"✅ Stored page with embedding: {url}")

  print("\n🎉 COMPLETED: All pages scraped & saved with semantic embeddings.")
