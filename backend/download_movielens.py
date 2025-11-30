import urllib.request
import zipfile
import os

def download_movielens_1m():
    url = "http://files.grouplens.org/datasets/movielens/ml-1m.zip"
    os.makedirs("data", exist_ok=True)
    
    print("Descargando MovieLens 1M...")
    urllib.request.urlretrieve(url, "data/ml-1m.zip")
    
    print("Extrayendo archivos...")
    with zipfile.ZipFile("data/ml-1m.zip", 'r') as zip_ref:
        zip_ref.extractall("data")
    
    # Copiar movies.dat al directorio data/
    os.rename("data/ml-1m/movies.dat", "data/movies.dat")
    print("✓ movies.dat listo en data/")

if __name__ == "__main__":
    download_movielens_1m()