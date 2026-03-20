import os
import requests
from tqdm import tqdm
import pandas as pd
from datetime import datetime

# Official Cloudfront base URL (2025–2026 files)
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
YEARS = [2025, 2026]  # we'll grab all available months
DATA_DIR = "../data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

def download_file(url, filepath):
    if os.path.exists(filepath):
        print(f"Already downloaded: {filepath}")
        return
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    with open(filepath, 'wb') as f, tqdm(
        desc=filepath.split('/')[-1],
        total=total,
        unit='iB',
        unit_scale=True
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

print("Downloading latest official NYC Yellow Taxi Parquet files...")

for year in YEARS:
    for month in range(1, 13):
        filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
        url = BASE_URL + filename
        filepath = os.path.join(DATA_DIR, filename)
        try:
            download_file(url, filepath)
        except:
            print(f"File not yet available: {filename} (normal for future months)")

print("Data fetch complete! Files saved in data/raw")