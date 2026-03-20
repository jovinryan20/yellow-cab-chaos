import os
import requests
import zipfile

DATA_DIR = "data/external"
os.makedirs(DATA_DIR, exist_ok=True)

# Taxi Zone Lookup (small CSV)
lookup_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
lookup_path = os.path.join(DATA_DIR, "taxi_zone_lookup.csv")

if not os.path.exists(lookup_path):
    print("Downloading taxi_zone_lookup.csv...")
    r = requests.get(lookup_url)
    with open(lookup_path, 'wb') as f:
        f.write(r.content)
    print("Lookup table downloaded")
else:
    print("Lookup table already exists")

# Taxi Zones Shapefile (for maps later)
zones_zip_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
zones_zip_path = os.path.join(DATA_DIR, "taxi_zones.zip")
zones_dir = os.path.join(DATA_DIR, "taxi_zones")

if not os.path.exists(zones_dir):
    print("Downloading taxi_zones shapefile...")
    r = requests.get(zones_zip_url)
    with open(zones_zip_path, 'wb') as f:
        f.write(r.content)
    
    with zipfile.ZipFile(zones_zip_path, 'r') as zip_ref:
        zip_ref.extractall(zones_dir)
    print("Shapefile extracted")
    os.remove(zones_zip_path)  # clean up zip
else:
    print("Shapefile already exists")

print("Zone files ready in data/processed")