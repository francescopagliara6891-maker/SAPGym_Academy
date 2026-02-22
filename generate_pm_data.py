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

print("🚀 Avvio Motore Dati PM/PP (Plant Maintenance & Production)...")

# 2. Generazione CSKS (Centri di Costo - Integrazione CO)
print("⏳ Generazione Centri di Costo (CSKS)...")
cost_centers_names = ['Manutenzione Elettrica', 'Reparto Laminazione', 'Servizi Generali', 'Magazzino Ricambi', 'Produzione Acciaio']
cost_centers = []
for i, name in enumerate(cost_centers_names):
    cost_centers.append({
        'KOSTL': f"CC{str(i+1).zfill(3)}", # Es. CC001
        'KTEXT': name
    })
df_csks = pd.DataFrame(cost_centers)
df_csks.to_sql('CSKS', engine, if_exists='replace', index=False)

# 3. Generazione EQUI (Anagrafica Equipment / Macchinari)
print("⏳ Generazione Anagrafica Macchinari (EQUI)...")
equipment_types = [
    'Motore Laminatoio a Caldo', 'Quadro Elettrico di Commutazione', 
    'Trasformatore MT/BT', 'Pompa Idraulica Principale', 'Carroponte Elettrico 50t',
    'Sensore Termico Forno', 'Nastro Trasportatore'
]
equipments = []
for i in range(60):
    equipments.append({
        'EQUNR': f"EQ{str(i+1).zfill(5)}", # Es. EQ00001
        'EQKTX': f"{random.choice(equipment_types)} - Z{random.randint(1,99)}",
        'KOSTL': random.choice(cost_centers)['KOSTL'] # Il macchinario appartiene a un centro di costo
    })
df_equi = pd.DataFrame(equipments)
df_equi.to_sql('EQUI', engine, if_exists='replace', index=False)

# 4. Generazione AFIH (Testata Ordine di Manutenzione)
print("⏳ Generazione Ordini di Manutenzione (AFIH)...")
pm_orders = []
for i in range(250):
    pm_orders.append({
        'AUFNR': f"400{str(i+1).zfill(6)}", # Es. 400000001 (Standard SAP PM)
        'EQUNR': random.choice(equipments)['EQUNR'],
        'ILART': random.choice(['PM01', 'PM02']), # PM01 = A guasto, PM02 = Preventiva
        'ERDAT': fake.date_between(start_date='-1y', end_date='today')
    })
df_afih = pd.DataFrame(pm_orders)
df_afih.to_sql('AFIH', engine, if_exists='replace', index=False)

# 5. Generazione AFVC (Operazioni e Costi dell'Ordine)
print("⏳ Generazione Operazioni e Costi (AFVC)...")
operations = []
for index, order in df_afih.iterrows():
    # Da 1 a 3 interventi per ogni ordine di manutenzione
    num_ops = random.randint(1, 3)
    for j in range(num_ops):
        ore_lavoro = random.randint(2, 48) # Ore per risolvere il guasto
        costo_ricambi = round(random.uniform(100.0, 15000.0), 2) # Costo dei materiali usati
        
        operations.append({
            'AUFNR': order['AUFNR'],
            'VORNR': f"{(j + 1) * 10}", # Operazione 10, 20, 30...
            'ARBEI': ore_lavoro, # Lavoro (Ore)
            'COST_MAT': costo_ricambi, # Costo Materiali
            'COST_TOT': round((ore_lavoro * 45.0) + costo_ricambi, 2) # Costo Totale (Manodopera a 45€/h + Ricambi)
        })
df_afvc = pd.DataFrame(operations)
df_afvc.to_sql('AFVC', engine, if_exists='replace', index=False)

print(f"✅ Tabella EQUI (Macchinari): {len(df_equi)} record.")
print(f"✅ Tabella AFIH (Ordini PM): {len(df_afih)} record.")
print(f"✅ Tabella AFVC (Costi Intervento): {len(df_afvc)} record.")
print("🎯 Boom! Modulo PM alimentato con successo. Impianto siderurgico virtuale online.")