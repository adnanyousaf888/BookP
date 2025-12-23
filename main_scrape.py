# main_scrape.py

from scraper.crawler import crawl_website
from scraper.scraper import scrape_and_store
from database.mongo import clear_collection

if __name__ == "__main__":
  clear_collection()
  pages = crawl_website()
  scrape_and_store(pages)
