# scraper/cleaner.py

from bs4 import BeautifulSoup
import re

REMOVE_TAGS = ["script", "style", "nav", "footer", "header", "form"]


def dedupe_paragraphs(text: str) -> str:
    """Removes repeated paragraphs from a page."""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    seen = set()
    final = []

    for p in paras:
        key = re.sub(r"\s+", " ", p.lower())
        if key not in seen:
            seen.add(key)
            final.append(p)

    return "\n".join(final)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove useless tags (menus, footer, script)
    for tag in REMOVE_TAGS:
        for element in soup.find_all(tag):
            element.decompose()

    text = soup.get_text(separator="\n")

    # Remove "Skip to content"
    text = text.replace("Skip to content", "")

    # Remove multiple blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Dedupe paragraphs
    text = dedupe_paragraphs(text)

    # Remove trailing spaces
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])

    return text.strip()
