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

print("🚀 Avvio Motore Dati MM - Livello Avanzato...")

# 1. Generazione LFA1 (Fornitori)
print("⏳ Generazione LFA1 (Fornitori)...")
vendors = [{'LIFNR': f"V{str(i+1).zfill(5)}", 'NAME1': fake.company(), 'LAND1': 'IT', 'ORT01': fake.city()} for i in range(50)]
df_lfa1 = pd.DataFrame(vendors)
df_lfa1.to_sql('LFA1', engine, if_exists='replace', index=False)

# 2. Generazione MARA (Materiali - NUOVO)
print("⏳ Generazione MARA (Materiali)...")
material_types = ['Cuscinetto a sfera', 'Motore Elettrico 50kW', 'Cavo di Rame 100m', 'Quadro Elettrico', 'Valvola di Pressione', 'Sensore Termico', 'Pompa Idraulica']
materials = []
for i in range(100):
    materials.append({
        'MATNR': f"MAT-{str(i+1).zfill(5)}", # Es. MAT-00001
        'MTART': 'ROH', # Materie prime (Standard SAP)
        'MAKTX': f"{random.choice(material_types)} - Mod. {fake.bothify(text='??-###')}",
        'STPRS': round(random.uniform(10.0, 5000.0), 2) # Prezzo Standard
    })
df_mara = pd.DataFrame(materials)
df_mara.to_sql('MARA', engine, if_exists='replace', index=False)

# 3. Generazione EKKO (Testate Ordini)
print("⏳ Generazione EKKO (Testate Ordini)...")
num_orders = 500 # Aumentiamo il volume!
orders = []
for i in range(num_orders):
    orders.append({
        'EBELN': f"45{str(i+1).zfill(8)}",
        'BUKRS': '1000',
        'LIFNR': random.choice(vendors)['LIFNR'],
        'AEDAT': fake.date_between(start_date='-2y', end_date='today') # Dati di 2 anni per fare analisi
    })
df_ekko = pd.DataFrame(orders)
df_ekko.to_sql('EKKO', engine, if_exists='replace', index=False)

# 4. Generazione EKPO (Posizioni Ordini - NUOVO)
print("⏳ Generazione EKPO (Posizioni Ordini)...")
items = []
for index, order in df_ekko.iterrows():
    num_items = random.randint(1, 5) # Da 1 a 5 righe per ogni ordine
    for j in range(num_items):
        mat = random.choice(materials)
        qty = random.randint(1, 100)
        # Il prezzo netto varia leggermente dal prezzo standard del materiale (sconti/rincari)
        net_price = round(mat['STPRS'] * random.uniform(0.90, 1.10), 2) 
        
        items.append({
            'EBELN': order['EBELN'],
            'EBELP': (j + 1) * 10, # 10, 20, 30... (Logica SAP pura)
            'MATNR': mat['MATNR'],
            'MENGE': qty, # Quantità
            'NETPR': net_price, # Prezzo Unitario Netto
            'NETWR': round(qty * net_price, 2) # Valore Totale Riga
        })
df_ekpo = pd.DataFrame(items)
df_ekpo.to_sql('EKPO', engine, if_exists='replace', index=False)

print(f"🎯 Boom! Database arricchito: {len(df_lfa1)} Fornitori, {len(df_mara)} Materiali, {len(df_ekko)} Ordini, {len(df_ekpo)} Posizioni.")