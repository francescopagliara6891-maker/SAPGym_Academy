import os
import pandas as pd
from faker import Faker
import random
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Configurazione Connessione S/4HANA CLOUD
load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

# Il generatore di nomi fittizi deve restare!
fake = Faker('it_IT')

print("🚀 Avvio Motore Dati SD (Order-to-Cash)...")

# 2. Generazione KNA1 (Anagrafica Clienti)
print("⏳ Generazione Anagrafica Clienti (KNA1)...")
customers = []
for i in range(40):
    customers.append({
        'KUNNR': f"C{str(i+1).zfill(5)}", # Es. C00001
        'NAME1': fake.company(),
        'LAND1': 'IT',
        'ORT01': fake.city()
    })
df_kna1 = pd.DataFrame(customers)
df_kna1.to_sql('KNA1', engine, if_exists='replace', index=False)

# --- L'INTEGRAZIONE TRA MODULI (Cazzimma pura) ---
# Leggiamo la tabella MARA (Materiali creati nel modulo MM) per venderli ai clienti.
print("⏳ Lettura Anagrafica Materiali (MARA) in corso...")
df_mara = pd.read_sql('SELECT "MATNR", "STPRS" FROM "MARA"', engine)
material_list = df_mara.to_dict('records')

# 3. Generazione VBAK (Testata Ordini di Vendita)
print("⏳ Generazione Testate Ordini di Vendita (VBAK)...")
num_sales_orders = 300
sales_orders = []
for i in range(num_sales_orders):
    sales_orders.append({
        'VBELN': f"10{str(i+1).zfill(8)}", # 1000000001 (Standard SAP per vendite)
        'VKORG': '1000', # Sales Organization
        'KUNNR': random.choice(customers)['KUNNR'],
        'AUDAT': fake.date_between(start_date='-1y', end_date='today')
    })
df_vbak = pd.DataFrame(sales_orders)
df_vbak.to_sql('VBAK', engine, if_exists='replace', index=False)

# 4. Generazione VBAP (Posizioni Ordini di Vendita)
print("⏳ Generazione Posizioni Ordini (VBAP)...")
sales_items = []
for index, order in df_vbak.iterrows():
    num_items = random.randint(1, 4)
    for j in range(num_items):
        mat = random.choice(material_list)
        qty = random.randint(1, 50)
        
        # LOGICA DI BUSINESS: Prezzo Vendita = Costo Standard (MARA) + Ricarico (30%-80%)
        net_price = round(mat['STPRS'] * random.uniform(1.30, 1.80), 2)
        
        sales_items.append({
            'VBELN': order['VBELN'],
            'POSNR': (j + 1) * 10, # 10, 20, 30...
            'MATNR': mat['MATNR'],
            'KWMENG': qty, # Quantità ordinata
            'NETPR': net_price, # Prezzo unitario di vendita
            'NETWR': round(qty * net_price, 2) # Valore totale riga
        })
df_vbap = pd.DataFrame(sales_items)
df_vbap.to_sql('VBAP', engine, if_exists='replace', index=False)

print(f"✅ Tabella KNA1 (Clienti): {len(df_kna1)} record.")
print(f"✅ Tabella VBAK (Ordini Vendita): {len(df_vbak)} record.")
print(f"✅ Tabella VBAP (Posizioni Vendita): {len(df_vbap)} record.")
print("🎯 Boom! Modulo SD alimentato con successo. Order-to-Cash attivo.")