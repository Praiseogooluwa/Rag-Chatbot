"""
Document Downloader
===================
Downloads free financial/economic PDFs for demo purposes.
Run this once to populate your data/raw/ folder.

Usage:
    python scripts/scrape_cbn.py
"""

import os
import time
import requests
from pathlib import Path

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All direct PDF links verified to work
DOCUMENTS = [
    {
        "name": "BIS_AI_In_Finance.pdf",
        "url":  "https://www.bis.org/publ/work1176.pdf"
    },
    {
        "name": "BIS_Crypto_Assets_Report.pdf",
        "url":  "https://www.bis.org/publ/work1049.pdf"
    },
    {
        "name": "BIS_Central_Bank_Digital_Currency.pdf",
        "url":  "https://www.bis.org/publ/work1004.pdf"
    },
    {
        "name": "BIS_Financial_Stability_Risks.pdf",
        "url":  "https://www.bis.org/publ/work980.pdf"
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def download_pdf(url: str, filename: str) -> bool:
    output_path = OUTPUT_DIR / filename
    if output_path.exists():
        print(f"  Already exists, skipping: {filename}")
        return True
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "html" in content_type.lower():
            print(f"  Skipped (got HTML not PDF): {filename}")
            return False
        with open(output_path, "wb") as f:
            f.write(response.content)
        size_kb = len(response.content) / 1024
        print(f"  Downloaded: {filename} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  Failed: {filename} - {e}")
        return False


def main():
    print("\n=== Document Downloader ===")
    print(f"Saving to: {OUTPUT_DIR.absolute()}\n")

    success = 0
    for doc in DOCUMENTS:
        print(f"Downloading: {doc['name']}")
        if download_pdf(doc["url"], doc["name"]):
            success += 1
        time.sleep(1)

    print(f"\n=== Done: {success}/{len(DOCUMENTS)} documents saved ===")
    print("\nNext step:")
    print("  python scripts/ingest.py")


if __name__ == "__main__":
    main()