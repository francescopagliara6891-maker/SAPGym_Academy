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

print("🚀 Avvio Motore Finanziario (FI/CO) - Generazione MIRO...")

# 2. Estrazione dati da MM (Leggiamo EKKO ed EKPO)
print("⏳ Lettura Ordini di Acquisto in corso...")
df_ekko = pd.read_sql('SELECT "EBELN", "LIFNR", "AEDAT" FROM "EKKO"', engine)
df_ekpo = pd.read_sql('SELECT "EBELN", "EBELP", "NETWR" FROM "EKPO"', engine)

bkpf_records = []
bseg_records = []

doc_number = 1900000000 # Range tipico documenti fattura SAP

print("⏳ Generazione Documenti Contabili (BKPF/BSEG) con iniezione scostamenti...")
# 3. Creazione Documenti Contabili per ogni Ordine
for index, row in df_ekko.iterrows():
    ebeln = row['EBELN']
    lifnr = row['LIFNR']
    aedat = pd.to_datetime(row['AEDAT'])
    
    # La fattura arriva in media da 5 a 30 giorni dopo l'ordine
    budat = aedat + pd.Timedelta(days=random.randint(5, 30))
    gjahr = budat.year
    belnr = str(doc_number)
    doc_number += 1
    
    # Creazione BKPF (Testata)
    bkpf_records.append({
        'BUKRS': '1000',
        'BELNR': belnr,
        'GJAHR': gjahr,
        'BLART': 'RE', # Tipo documento: Fattura lorda
        'BLDAT': budat.date(), # Data documento
        'BUDAT': budat.date(), # Data di registrazione
        'AWKEY': ebeln # Riferimento (Lega la fattura all'ordine MM!)
    })
    
    # Creazione BSEG (Posizioni)
    po_items = df_ekpo[df_ekpo['EBELN'] == ebeln]
    buzei = 1
    tot_fattura = 0
    
    for _, item in po_items.iterrows():
        netwr = item['NETWR']
        
        # INIEZIONE CAZZIMMA: Il 20% delle fatture ha uno scostamento di prezzo rispetto all'ordine
        if random.random() < 0.20:
            varianza = random.uniform(0.90, 1.15) # Variazione dal -10% al +15%
            fatturato_riga = round(netwr * varianza, 2)
        else:
            fatturato_riga = netwr
            
        tot_fattura += fatturato_riga
        
        # Riga Dare (Costo/Magazzino)
        bseg_records.append({
            'BUKRS': '1000',
            'BELNR': belnr,
            'GJAHR': gjahr,
            'BUZEI': buzei + 1,
            'BSCHL': '86', # Chiave di registrazione Entrata Merci/Fattura
            'HKONT': '400000', # Conto CoGe Costi
            'SHKZG': 'S', # Dare (Debit)
            'WRBTR': fatturato_riga,
            'EBELN': ebeln,
            'EBELP': item['EBELP']
        })
        buzei += 1
        
    # Riga Avere (Debito verso Fornitore)
    bseg_records.insert(0, {
        'BUKRS': '1000',
        'BELNR': belnr,
        'GJAHR': gjahr,
        'BUZEI': 1,
        'BSCHL': '31', # Chiave di registrazione Fattura Fornitore
        'HKONT': lifnr, # Il partitario fornitore
        'SHKZG': 'H', # Avere (Credit)
        'WRBTR': round(tot_fattura, 2),
        'EBELN': None,
        'EBELP': None
    })

# 4. Scrittura massiva su PostgreSQL
df_bkpf = pd.DataFrame(bkpf_records)
df_bseg = pd.DataFrame(bseg_records)

df_bkpf.to_sql('BKPF', engine, if_exists='replace', index=False)
df_bseg.to_sql('BSEG', engine, if_exists='replace', index=False)

print(f"✅ Tabella BKPF (Testate Contabili): {len(df_bkpf)} record.")
print(f"✅ Tabella BSEG (Posizioni Contabili): {len(df_bseg)} record.")
print("🎯 Boom! Modulo FI/CO alimentato. Il 3-Way Match MM-FI è completo.")