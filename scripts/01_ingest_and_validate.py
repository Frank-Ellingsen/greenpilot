import os
import sys
import pandas as pd

# ==============================================================================
# GENERALISERT STEG 1: DATA INGESTION & SCHEMA VALIDATION
# ==============================================================================

BASE_DIR = os.getcwd() if os.path.exists(os.path.join(os.getcwd(), "data")) else os.path.dirname(os.getcwd())
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
STAGING_DIR = os.path.join(BASE_DIR, "data", "staging")
os.makedirs(STAGING_DIR, exist_ok=True)

dict_file = os.path.join(RAW_DIR, "20_data_dictionary.csv")

print("=" * 75)
print("=== STEG 1: GENERELL DATA INGESTION & SCHEMA VALIDATION ===")
print("=" * 75)

# Les data dictionary for obligatoriske kolonner dersom den finnes
schema_map = {}
if os.path.exists(dict_file):
    df_dict = pd.read_csv(dict_file, sep=";", encoding="utf-8-sig")
    df_dict.columns = [c.strip().lstrip('\ufeff') for c in df_dict.columns]
    for _, row in df_dict.iterrows():
        fname = str(row["file_name"]).strip()
        col = str(row["column_name"]).strip()
        schema_map.setdefault(fname, []).append(col)

csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv") and f != "21_manifest.csv"]

print(f"{'Filnavn':<35} | {'Rader':<8} | {'Kolonner':<10} | {'Status'}")
print("-" * 75)

for fname in sorted(csv_files):
    file_path = os.path.join(RAW_DIR, fname)
    
    # 1. Sjekk om filen er tom
    if os.path.getsize(file_path) == 0:
        print(f"{fname:<35} | {'0':<8} | {'0':<10} | [FEIL: Tom fil]")
        continue
        
    try:
        # 2. Detekter skilletegn
        with open(file_path, "r", encoding="utf-8-sig") as f:
            first_line = f.readline()
            delimiter = ";" if ";" in first_line else ","
            
        df = pd.read_csv(file_path, encoding="utf-8-sig", sep=delimiter)
        df.columns = [c.strip().strip('"').strip("'").lstrip('\ufeff') for c in df.columns]
        
        # 3. Schema-sjekk mot forventede kolonner
        expected_cols = schema_map.get(fname, [])
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            status_str = f"FEIL: Mangler kolonner {missing_cols}"
        else:
            status_str = "OK (Validert)"
            
        print(f"{fname:<35} | {len(df):<8d} | {len(df.columns):<10d} | {status_str}")
        
        # 4. Skriv til staging
        staging_path = os.path.join(STAGING_DIR, fname)
        df.to_csv(staging_path, index=False, sep=";")
        
    except Exception as e:
        print(f"{fname:<35} | {'-':<8} | {'-':<10} | [FEIL: {e}]")

print("=" * 75)
print(f"[OK] Innlesing fullført. Generiske staging-data lagret i: {STAGING_DIR}")
print("=" * 75)