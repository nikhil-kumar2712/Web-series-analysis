import pandas as pd
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from tqdm import tqdm
import re
import time

# -------------------------
# Config
# -------------------------
INPUT_CSV = "webseries_cleaned.csv"
OUTPUT_CSV = "webseries_with_genre.csv"
SLEEP_BETWEEN_QUERIES = 1.5  # delay to avoid rate-limiting
SAVE_EVERY = 500  # save progress after every 500 updates

# -------------------------
# Parsers
# -------------------------
def parse_wikipedia_genre(url):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        infobox = soup.find("table", class_=lambda x: x and "infobox" in x)
        if infobox:
            for tr in infobox.find_all("tr"):
                th = tr.find("th")
                td = tr.find("td")
                if th and td and "genre" in th.get_text(" ", strip=True).lower():
                    return td.get_text(" ", strip=True)
    except Exception:
        return None
    return None

def parse_imdb_genre(url):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        genres = soup.find_all("a", href=re.compile("/search/title\\?genres="))
        if genres:
            return ", ".join([g.get_text(strip=True) for g in genres])
    except Exception:
        return None
    return None

# -------------------------
# Fetch genre using ddgs
# -------------------------
def fetch_genre(title):
    ddgs = DDGS()
    query = f"{title} web series genre"
    try:
        results = ddgs.text(query, max_results=5)
        for r in results:
            url = r["href"].lower()
            if "wikipedia.org" in url:
                genre = parse_wikipedia_genre(r["href"])
                if genre:
                    return genre
            if "imdb.com" in url:
                genre = parse_imdb_genre(r["href"])
                if genre:
                    return genre
    except Exception:
        return None
    return None

# -------------------------
# Main
# -------------------------
df = pd.read_csv(INPUT_CSV)

mask_missing = df["genre"].isna() | (df["genre"].astype(str).str.strip() == "") | (df["genre"].astype(str).str.lower() == "unknown")
missing_df = df[mask_missing].copy()

print(f"Found {missing_df.shape[0]} missing genres...")

for count, (idx, row) in enumerate(tqdm(missing_df.iterrows(), total=missing_df.shape[0], desc="Fetching missing genres"), start=1):
    title = row["series_name"]
    genre = fetch_genre(title)
    if genre:
        df.at[idx, "genre"] = genre
    else:
        df.at[idx, "genre"] = "Unknown"

    # save progress every 500 updates
    if count % SAVE_EVERY == 0:
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"💾 Progress saved after {count} updates...")

    time.sleep(SLEEP_BETWEEN_QUERIES)

# Final save
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Done! Final file saved to {OUTPUT_CSV}")



