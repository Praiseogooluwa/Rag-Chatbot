import requests, os

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

docs = [
    {
        "name": "IMF_Nigeria_Economic_Report.pdf",
        "url": "https://www.imf.org/en/Publications/CR/Issues/2023/02/16/Nigeria-2022-Article-IV-Consultation-Press-Release-and-Staff-Report-529234"
    },
    {
        "name": "World_Bank_Nigeria_Finance.pdf", 
        "url": "https://documents1.worldbank.org/curated/en/099060424102518559/pdf/P1801920fc82900e10a6500c1e3b5b21295.pdf"
    },
    {
        "name": "AfDB_Nigeria_Report.pdf",
        "url": "https://www.afdb.org/fileadmin/uploads/afdb/Documents/Project-and-Operations/Nigeria_-_2021-2025_-_Country_Strategy_Paper.pdf"
    },
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for doc in docs:
    path = os.path.join(OUTPUT_DIR, doc["name"])
    try:
        r = requests.get(doc["url"], headers=headers, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ {doc['name']} ({len(r.content)//1024} KB)")
    except Exception as e:
        print(f"❌ {doc['name']} — {e}")