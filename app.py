import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import datetime
import random

# --- 1. CONFIGURAZIONE E TEMA ---
st.set_page_config(page_title="Executive SAP Academy", page_icon="🎓", layout="wide")

def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=72&display=swap');
        html, body, [class*="css"] { font-family: '72', Arial, sans-serif; }
        h1, h2, h3, h4 { color: #2B7CE9 !important; } 
        .stButton>button { background-color: #0A6ED1 !important; color: white !important; border-radius: 0.5rem; border: none; font-weight: bold; }
        .stButton>button:hover { background-color: #0854A0 !important; color: white !important;}
        .stAlert { border-left-color: #0A6ED1; }
        .dataframe { font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 2. CONNESSIONE AL DATABASE ---
@st.cache_resource
def init_connection():
    try:
        return create_engine(st.secrets["DATABASE_URL"])
    except Exception:
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        return create_engine(db_url)

engine = init_connection()

# --- FUNZIONI CORE ---
def get_table_schema(table_name):
    query = f"SELECT * FROM \"{table_name}\" LIMIT 3"
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)

def write_audit_log(username, modulo, query_eseguita, status):
    """Simula la transazione SM20 (Audit Log) di SAP"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS "Z_SM20_AUDIT" (
        "TIMESTAMP" TIMESTAMP,
        "USERNAME" VARCHAR(50),
        "MODULO" VARCHAR(50),
        "QUERY" TEXT,
        "STATUS" VARCHAR(20)
    );
    """
    insert_sql = f"""
    INSERT INTO "Z_SM20_AUDIT" ("TIMESTAMP", "USERNAME", "MODULO", "QUERY", "STATUS")
    VALUES ('{timestamp}', '{username}', '{modulo}', '{query_eseguita.replace("'", "''")}', '{status}');
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.execute(text(insert_sql))
            conn.commit()
    except:
        pass 

# Gestione ID Anonimo per evitare paura di registrazione
if 'username' not in st.session_state:
    st.session_state.username = f"GUEST_{random.randint(1000, 9999)}"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/SAP_2011_logo.svg/512px-SAP_2011_logo.svg.png", width=100)
    st.markdown(f"## 🎓 Executive SAP Academy")
    st.markdown(f"**Utente Attivo:** 🟢 `{st.session_state.username}`")
    
    modulo = st.radio("Seleziona Ambiente:", [
        "MM - Procure to Pay", 
        "FI/CO - Financials", 
        "SD - Order to Cash",
        "PM/PP - Plant & Production",
        "⚙️ Data Importer",
        "🛡️ Cyber Security (SM20)"
    ], key="menu_moduli")
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Lead Architect")
    st.markdown("**Dott. Francesco Pagliara**")
    st.caption("Ingegnere Gestionale | SAP Analyst")
    st.caption("Executive Master Cyber Security LUM")

# =========================================================================
# MODULO: MM PROCURE TO PAY
# =========================================================================
if modulo == "MM - Procure to Pay":
    st.title("📦 Modulo MM: Ciclo Passivo (Procure-to-Pay)")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Manuale MM: Integrazione Dati e Processi")
        st.markdown("#### 🟢 BEGINNER: Struttura Documentale")
        st.write("In SAP MM, ogni acquisto nasce da una Testata (`EKKO`) e si sviluppa in Posizioni (`EKPO`).")
        st.code('SELECT "EBELN", "LIFNR", "AEDAT" FROM "EKKO" LIMIT 10;', language="sql")
        st.markdown("""
        * **EBELN (Einkaufsbelegnummer):** Numero univoco dell'ordine.
        * **LIFNR (Lieferantennummer):** Codice del fornitore associato.
        * **AEDAT (Änderungsdatum):** Data di creazione/modifica.
        """)
        
        st.markdown("#### 🟡 INTERMEDIATE: Join Anagrafica e Spesa")
        st.code("""
        SELECT lfa1."NAME1" AS "Fornitore", SUM(ekpo."NETWR") AS "Totale"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"
        GROUP BY lfa1."NAME1";
        """, language="sql")
        st.markdown("""
        * **LFA1."NAME1":** Ragione sociale del fornitore. Senza questa JOIN, vedresti solo codici numerici.
        * **EKPO."NETWR":** Valore netto dell'acquisto. Usiamo `SUM` per aggregare i costi.
        """)

    with tab_dizionario:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**EKKO (Testata)**")
            st.dataframe(get_table_schema("EKKO"), hide_index=True)
        with col2:
            st.markdown("**EKPO (Posizioni)**")
            st.dataframe(get_table_schema("EKPO"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox MM:", "SELECT * FROM \"EKKO\" LIMIT 20;")
        if st.button("▶️ Esegui MM"):
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "MM", user_query, "SUCCESS")
                st.dataframe(df)
            except Exception as e:
                write_audit_log(st.session_state.username, "MM", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: FI/CO FINANCIALS
# =========================================================================
elif modulo == "FI/CO - Financials":
    st.title("💶 Modulo FI/CO: Financials & Controlling")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Manuale FI: Logiche Contabili in S/4HANA")
        st.markdown("#### 🟢 BEGINNER: La Partita Doppia")
        st.write("Le registrazioni contabili sono divise tra Testata (`BKPF`) e Posizioni (`BSEG`).")
        st.code('SELECT "BELNR", "BUZEI", "SHKZG", "WRBTR" FROM "BSEG" LIMIT 10;', language="sql")
        st.markdown("""
        * **BELNR (Belegnummer):** Numero del documento contabile.
        * **BUZEI (Buchungszeile):** Numero della riga (item) nel documento.
        * **SHKZG (Soll/Haben Kennzeichen):** Indicatore Dare/Avere. 'S' = Dare, 'H' = Avere.
        * **WRBTR (Währungsbetrag):** Importo in valuta del documento.
        """)
        
        st.markdown("#### 🔴 ADVANCED: Calcolo Saldo Algebrico")
        st.code("""
        SELECT "BELNR", 
               SUM(CASE WHEN "SHKZG" = 'S' THEN "WRBTR" ELSE -"WRBTR" END) AS "Saldo"
        FROM "BSEG" GROUP BY "BELNR";
        """, language="sql")
        st.write("Questa query trasforma la logica SAP in un saldo reale: se è Avere ('H'), l'importo diventa negativo.")

    with tab_dizionario:
        st.markdown("**BSEG (Document Segments)**")
        st.dataframe(get_table_schema("BSEG"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox FI:", "SELECT * FROM \"BSEG\" LIMIT 20;")
        if st.button("▶️ Esegui FI"):
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "FI", user_query, "SUCCESS")
                st.dataframe(df)
            except Exception as e:
                write_audit_log(st.session_state.username, "FI", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: SD ORDER TO CASH
# =========================================================================
elif modulo == "SD - Order to Cash":
    st.title("🚚 Modulo SD: Vendite e Distribuzione")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Manuale SD: Il Flusso delle Vendite")
        st.markdown("#### 🟢 BEGINNER: Anagrafica Clienti")
        st.write("I dati dei clienti risiedono nella tabella `KNA1`.")
        st.code('SELECT "KUNNR", "NAME1", "ORT01" FROM "KNA1" LIMIT 10;', language="sql")
        st.markdown("""
        * **KUNNR (Kundennummer):** Codice cliente.
        * **NAME1:** Nome/Ragione Sociale.
        * **ORT01:** Città.
        """)
        
        st.markdown("#### 🟡 INTERMEDIATE: Fatturato per Cliente")
        st.code("""
        SELECT k."NAME1", SUM(p."NETWR") AS "Fatturato"
        FROM "VBAK" v
        JOIN "VBAP" p ON v."VBELN" = p."VBELN"
        JOIN "KNA1" k ON v."KUNNR" = k."KUNNR"
        GROUP BY k."NAME1";
        """, language="sql")
        st.write("Colleghiamo l'ordine (`VBAK`) alle posizioni (`VBAP`) e all'anagrafica (`KNA1`) per calcolare i ricavi.")

    with tab_dizionario:
        st.markdown("**VBAK (Sales Header)**")
        st.dataframe(get_table_schema("VBAK"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox SD:", "SELECT * FROM \"VBAK\" LIMIT 20;")
        if st.button("▶️ Esegui SD"):
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "SD", user_query, "SUCCESS")
                st.dataframe(df)
            except Exception as e:
                write_audit_log(st.session_state.username, "SD", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: PM/PP PLANT & PRODUCTION
# =========================================================================
elif modulo == "PM/PP - Plant & Production":
    st.title("🏭 Moduli PM: Gestione Asset e Impianti")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Manuale PM: Manutenzione Impianti")
        st.markdown("#### 🟢 BEGINNER: Anagrafica Macchinari")
        st.write("Le attrezzature aziendali sono censite nella tabella `EQUI`.")
        st.code('SELECT "EQUNR", "EQKTX", "KOSTL" FROM "EQUI" LIMIT 10;', language="sql")
        st.markdown("""
        * **EQUNR (Equipmentnummer):** Codice univoco del macchinario.
        * **EQKTX:** Descrizione tecnica dell'asset.
        * **KOSTL (Kostenstelle):** Centro di costo responsabile del macchinario.
        """)
        
        st.markdown("#### 🔴 ADVANCED: Costi Manutenzione vs Macchinario")
        st.code("""
        SELECT e."EQKTX", SUM(v."COST_TOT") AS "Spesa_Riparazioni"
        FROM "EQUI" e
        JOIN "AFIH" a ON e."EQUNR" = a."EQUNR"
        JOIN "AFVC" v ON a."AUFNR" = v."AUFNR"
        GROUP BY e."EQKTX";
        """, language="sql")
        st.write("Analizziamo l'impatto economico degli ordini di manutenzione (`AFIH`) e dei costi operativi (`AFVC`).")

    with tab_dizionario:
        st.markdown("**EQUI (Equipment Master)**")
        st.dataframe(get_table_schema("EQUI"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox PM:", "SELECT * FROM \"EQUI\" LIMIT 20;")
        if st.button("▶️ Esegui PM"):
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "PM", user_query, "SUCCESS")
                st.dataframe(df)
            except Exception as e:
                write_audit_log(st.session_state.username, "PM", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: CYBER SECURITY (SM20)
# =========================================================================
elif modulo == "🛡️ Cyber Security (SM20)":
    st.title("🛡️ Cyber Security Dashboard: SAP Audit Log")
    st.info("ℹ️ Questa sezione simula la transazione SAP **SM20**. Ogni interazione con il database viene tracciata per garantire l'integrità del sistema e monitorare accessi non autorizzati.")
    
    st.markdown("#### Registro Operazioni (Real-time Database Logs)")
    try:
        query_logs = "SELECT * FROM \"Z_SM20_AUDIT\" ORDER BY \"TIMESTAMP\" DESC LIMIT 100;"
        with engine.connect() as conn:
            df_logs = pd.read_sql(text(query_logs), conn)
        
        def highlight_status(val):
            color = '#E74C3C' if val == 'ERROR' else '#2ECC71'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_logs.style.applymap(highlight_status, subset=['STATUS']), use_container_width=True, hide_index=True)
    except:
        st.info("Nessun log presente. Esegui una query in un modulo per generare i primi dati di audit!")

# =========================================================================
# MODULO: DATA IMPORTER
# =========================================================================
elif modulo == "⚙️ Data Importer":
    st.title("⚙️ Data Importer: Estendi il tuo S/4HANA")
    st.write("Carica file CSV per creare nuove tabelle custom (`Z-Tables`).")
    uploaded_file = st.file_uploader("Scegli un file CSV", type="csv")
    table_name = st.text_input("Nome tabella SAP (es. Z_TEST):", "Z_CUSTOM_DATA")
    
    if uploaded_file is not None and st.button("Importa nel Database"):
        df_up = pd.read_csv(uploaded_file)
        df_up.to_sql(table_name.upper(), engine, if_exists='replace', index=False)
        write_audit_log(st.session_state.username, "IMPORTER", f"CREATE TABLE {table_name}", "SUCCESS")
        st.success(f"Tabella {table_name.upper()} caricata!")