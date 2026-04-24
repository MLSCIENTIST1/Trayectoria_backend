import requests
import json
import csv

TOKEN = "eyJraWQiOiJyU2lwUHpNTStjVTA0ZXltYTl3YXFwRENOK1VYQVh5R214T3RNNlRMUTBrPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5NTU5ODcwZC1mZGJmLTRmY2YtOGQ0Ny1iM2E3NDZkMTY2ZmYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfRFprVGt4UU1FIiwiY29nbml0bzp1c2VybmFtZSI6Ijk1NTk4NzBkLWZkYmYtNGZjZi04ZDQ3LWIzYTc0NmQxNjZmZiIsIm9yaWdpbl9qdGkiOiI0ZThmN2JmZS0wM2Q4LTRkMTUtYTVjYS1mMGMwY2RjODVhNzQiLCJhdWQiOiIxZWZ0bHQ5ZWQ3NTNrZ2RhZDJvZmd2OWExMSIsImV2ZW50X2lkIjoiOGQ4MTMzMDEtODhiOS00NmM3LWJhNmEtNjdiNGIwNDkxNTdiIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NzY5NzQyMzksImN1c3RvbTppZFVzZXJNYXN0ZXJzaG9wIjoiMTI5ODc1IiwiZXhwIjoxNzc2OTkxMDE1LCJjdXN0b206cm9sZSI6ImN1c3RvbWVyIiwiaWF0IjoxNzc2OTg5MjE1LCJqdGkiOiI1OTllMDllNy1jYTk5LTRlODMtOTRlOC03NjRlYjdkZGVmMGMiLCJlbWFpbCI6ImNhcmxvcy01MTAwQGhvdG1haWwuY29tIn0.gcudQ067CWaBHII5N2esk9wcDmznHGwMX9zqmb-qNgai3Wxs9bE5_D_SbdrPGP7tn_SlRYos-hi2Ys4MVs03BIVzE6kiR4_LGwCyM5PF5q7fh3neLN4XhYWxJ0m1ZrJff1VlaCaeBc-G7y0dwPlrXzuL66GmonkhA-qdyq2OZEVMhiIe1OAqayDDKljWSrrivvVasJSKUgubSJJaR0qErdE2r36jKmJiyB_36EpxL5XZZDlSEIx45ah7XdBntfCDuci4JzhtVa9prtaUT1x5uN8actYssg6h-fnxPv52jALJ-SBRGcIKKnAR4_smVVOKTtX7bqPy4CWF62aJwNU_Gg"

HEADERS = {
    "x-auth-id": TOKEN,
    "x-idbusiness": "118488",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
URL = "https://api-m.mastershop.com/prod/api/b2c/afiliation/market"

HEADERS = {
    "x-auth-id": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Filtros: 31 = Vehículos (el que ya vimos)
# Puedes cambiar o quitar el filtro para traer todos los productos
PAYLOAD = {
    "offset": 0,
    "limit": 50,
    "prodFormatIds": [31]  # Solo vehículos — quita esta línea para traer todo
}

def fetch_all_products():
    todos = []
    offset = 0
    limit = 50

    while True:
        PAYLOAD["offset"] = offset
        print(f"📦 Jalando productos {offset} - {offset + limit}...")

        resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=30)

        if resp.status_code == 401:
            print("❌ Token expirado — saca uno nuevo de DevTools")
            break

        if resp.status_code != 200:
            print(f"❌ Error {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        productos = data.get("data", {}).get("products", [])

        if not productos:
            print("✅ Sin más productos")
            break

        todos.extend(productos)
        print(f"   → {len(productos)} productos obtenidos (total: {len(todos)})")

        if len(productos) < limit:
            break

        offset += limit

    return todos

def guardar_csv(productos, archivo="mastershop_vehiculos.csv"):
    if not productos:
        print("⚠️ No hay productos para guardar")
        return

    campos = ["idProduct", "productName", "description", "basePrice",
              "prodFormatName", "publicName", "stock", "urlImageProduct"]

    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for p in productos:
            writer.writerow({k: p.get(k, "") for k in campos})

    print(f"✅ CSV guardado: {archivo} ({len(productos)} productos)")

if __name__ == "__main__":
    productos = fetch_all_products()
    guardar_csv(productos)
    # También guarda JSON por si acaso
    with open("mastershop_vehiculos.json", "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)
    print("✅ JSON guardado: mastershop_vehiculos.json")