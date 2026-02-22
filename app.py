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
        .stButton>button { 
            background-color: #0A6ED1 !important; 
            color: white !important; 
            border-radius: 0.5rem; 
            border: none; 
            padding: 0.5rem 1rem; 
            font-weight: bold; 
        }
        .stButton>button:hover { background-color: #0854A0 !important; border-color: #0854A0 !important; color: white !important;}
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

# --- 3. FUNZIONI CORE (AUDIT & SCHEMA) ---
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

# Gestione Sessione per Guest ID Anonimo
if 'username' not in st.session_state:
    st.session_state.username = f"GUEST_{random.randint(1000, 9999)}"

# --- 4. STRUTTURA SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/SAP_2011_logo.svg/512px-SAP_2011_logo.svg.png", width=100)
    st.markdown("## 🎓 Executive SAP Academy")
    st.markdown(f"**Utente Attivo:** 🟢 `{st.session_state.username}`")
    
    modulo = st.radio("Seleziona Ambiente:", [
        "MM - Procure to Pay", 
        "FI/CO - Financials", 
        "SD - Order to Cash",
        "PM/PP - Plant & Production",
        "⚙️ Data Importer (CSV/Gemini)",
        "🛡️ Cyber Security (SM20)"
    ], key="menu_moduli")
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Lead Architect")
    st.markdown("**Dott. Francesco Pagliara**")
    st.caption("Ingegnere Gestionale")
    st.caption("SAP Functional Analyst")
    st.caption("Master Cyber Security Candidate @ LUM")

# =========================================================================
# MODULO: MM PROCURE TO PAY
# =========================================================================
if modulo == "MM - Procure to Pay":
    st.title("📦 Modulo MM: Ciclo Passivo (Procure-to-Pay)")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Procurement")
        st.markdown("#### 🟢 BEGINNER LEVEL: Fondamentali Logistici")
        st.write("In SAP, l'ordine di acquisto è diviso in **EKKO** (Testata: chi compra) e **EKPO** (Posizioni: cosa compriamo).")
        st.code('SELECT "EBELN", "LIFNR", "AEDAT" FROM "EKKO" LIMIT 10;', language="sql")
        st.markdown("""
        * **EBELN (Einkaufsbeleg):** Numero univoco dell'ordine.
        * **LIFNR (Lieferant):** Codice fornitore.
        * **AEDAT:** Data di creazione.
        """)
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Integrazione Fornitori")
        st.code("""
        SELECT lfa1."NAME1" AS "Fornitore", SUM(ekpo."NETWR") AS "Spesa Totale"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"
        GROUP BY lfa1."NAME1";
        """, language="sql")
        st.markdown("**Anatomia:** Uniamo la spesa (`NETWR` di `EKPO`) al nome reale del fornitore (`NAME1` di `LFA1`).")

        st.markdown("#### 🔴 ADVANCED LEVEL: KPI Direzionali")
        st.write("Analisi dell'impatto percentuale di ogni fornitore sul totale speso tramite Window Functions.")

    with tab_dizionario:
        st.subheader("Tracciato Record (S/4HANA Schema)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**EKKO (Testata Ordini)**")
            st.dataframe(get_table_schema("EKKO"), hide_index=True)
            st.markdown("**LFA1 (Fornitori)**")
            st.dataframe(get_table_schema("LFA1"), hide_index=True)
        with col2:
            st.markdown("**EKPO (Posizioni Ordini)**")
            st.dataframe(get_table_schema("EKPO"), hide_index=True)

    with tab_pratica:
        st.markdown("### 💻 SQL Sandbox & Analytics Dashboard")
        user_query = st.text_area("SQL Sandbox MM:", height=150, key="sandbox_mm", value="SELECT * FROM \"EKKO\" LIMIT 50;")
        if st.button("▶️ Esegui (Run MM)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "MM", user_query, "SUCCESS")
                col_tab, col_chart = st.columns(2)
                with col_tab: st.dataframe(result_df, use_container_width=True)
                with col_chart:
                    if len(result_df.columns) >= 2 and pd.api.types.is_numeric_dtype(result_df[result_df.columns[1]]):
                        st.bar_chart(result_df.set_index(result_df.columns[0])[result_df.columns[1]])
            except Exception as e:
                write_audit_log(st.session_state.username, "MM", user_query, "ERROR")
                st.error(f"❌ Errore SQL: {e}")

# =========================================================================
# MODULO: FI/CO FINANCIALS
# =========================================================================
elif modulo == "FI/CO - Financials":
    st.title("💶 Modulo FI/CO: Financials & Controlling")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Financials")
        st.markdown("#### 🟢 BEGINNER LEVEL: La Partita Doppia")
        st.write("In SAP FI, il campo **SHKZG** determina il segno: 'S' (Soll/Dare) e 'H' (Haben/Avere).")
        st.code('SELECT "BELNR", "SHKZG", "WRBTR" FROM "BSEG" LIMIT 10;', language="sql")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Controllo Varianze")
        st.write("Confronto tra quanto ordinato in MM (`EKPO`) e quanto registrato in contabilità (`BSEG`).")

        st.markdown("#### 🔴 ADVANCED LEVEL: Saldo Algebrico Real-Time")
        st.code("""
        SELECT "BELNR" AS "Documento",
               SUM(CASE WHEN "SHKZG" = 'S' THEN "WRBTR" ELSE -"WRBTR" END) AS "Saldo"
        FROM "BSEG" GROUP BY "BELNR";
        """, language="sql")
        st.markdown("**Analatomia:** Trasformiamo l'Avere in valore negativo per calcolare se il documento è in pareggio.")

    with tab_dizionario:
        st.markdown("**BKPF (Testata Contabile)**")
        st.dataframe(get_table_schema("BKPF"), hide_index=True)
        st.markdown("**BSEG (Libro Giornale)**")
        st.dataframe(get_table_schema("BSEG"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox FI:", height=150, key="sandbox_fi", value="SELECT * FROM \"BSEG\" LIMIT 50;")
        if st.button("▶️ Esegui (Run FI)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "FI", user_query, "SUCCESS")
                st.dataframe(result_df)
            except Exception as e:
                write_audit_log(st.session_state.username, "FI", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: SD ORDER TO CASH
# =========================================================================
elif modulo == "SD - Order to Cash":
    st.title("🚚 Modulo SD: Order to Cash")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Sales")
        st.markdown("#### 🟢 BEGINNER LEVEL: Anagrafica Clienti")
        st.write("Tutti i dati dei clienti sono in **KNA1**. Chiave primaria: `KUNNR`.")
        st.code('SELECT "KUNNR", "NAME1", "ORT01" FROM "KNA1" LIMIT 10;', language="sql")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Analisi Fatturato")
        st.write("Colleghiamo l'ordine (`VBAK`) alle righe (`VBAP`) per vedere il venduto per cliente.")

        st.markdown("#### 🔴 ADVANCED LEVEL: Margine di Profitto")
        st.code("""
        SELECT kna1."NAME1", SUM(vbap."NETWR" - (mara."STPRS" * vbap."KWMENG")) AS "Profitto"
        FROM "VBAP" vbap
        JOIN "VBAK" vbak ON vbap."VBELN" = vbak."VBELN"
        JOIN "KNA1" kna1 ON vbak."KUNNR" = kna1."KUNNR"
        JOIN "MARA" mara ON vbap."MATNR" = mara."MATNR"
        GROUP BY kna1."NAME1";
        """, language="sql")
        st.markdown("**Anatomia:** Sottraiamo il costo standard (`STPRS`) dal ricavo (`NETWR`) per ottenere il margine netto.")

    with tab_dizionario:
        st.markdown("**VBAK (Testata Vendite)**")
        st.dataframe(get_table_schema("VBAK"), hide_index=True)
        st.markdown("**VBAP (Posizioni Vendite)**")
        st.dataframe(get_table_schema("VBAP"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox SD:", height=150, key="sandbox_sd", value="SELECT * FROM \"VBAK\" LIMIT 50;")
        if st.button("▶️ Esegui (Run SD)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "SD", user_query, "SUCCESS")
                st.dataframe(result_df)
            except Exception as e:
                write_audit_log(st.session_state.username, "SD", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: PM/PP PLANT & PRODUCTION
# =========================================================================
elif modulo == "PM/PP - Plant & Production":
    st.title("🏭 Moduli PM: Gestione Impianti")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Asset Management")
        st.markdown("#### 🟢 BEGINNER LEVEL: Censimento Asset")
        st.write("In SAP PM, i macchinari sono chiamati Equipment (`EQUI`).")
        st.code('SELECT "EQUNR", "EQKTX", "KOSTL" FROM "EQUI" LIMIT 10;', language="sql")
        
        st.markdown("#### 🔴 ADVANCED LEVEL: Manutenzione Preventiva vs Correttiva")
        st.write("Analizziamo i costi degli ordini PM01 (Guasto) rispetto a PM02 (Programmata).")
        st.code("""
        SELECT afih."ILART" AS "Tipo", SUM(afvc."COST_TOT") AS "Costo"
        FROM "AFIH" afih
        JOIN "AFVC" afvc ON afih."AUFNR" = afvc."AUFNR"
        GROUP BY afih."ILART";
        """, language="sql")

    with tab_dizionario:
        st.markdown("**EQUI (Equipment Master)**")
        st.dataframe(get_table_schema("EQUI"), hide_index=True)
        st.markdown("**AFVC (Costi Operazioni)**")
        st.dataframe(get_table_schema("AFVC"), hide_index=True)

    with tab_pratica:
        user_query = st.text_area("SQL Sandbox PM:", height=150, key="sandbox_pm", value="SELECT * FROM \"EQUI\" LIMIT 50;")
        if st.button("▶️ Esegui (Run PM)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "PM", user_query, "SUCCESS")
                st.dataframe(result_df)
            except Exception as e:
                write_audit_log(st.session_state.username, "PM", user_query, "ERROR")
                st.error(e)

# =========================================================================
# MODULO: CYBER SECURITY (SM20 AUDIT LOG)
# =========================================================================
elif modulo == "🛡️ Cyber Security (SM20)":
    st.title("🛡️ Cyber Security: SAP Audit Log (SM20)")
    st.info("ℹ️ Questa sezione simula il monitoraggio degli accessi al database. Ogni query lanciata dai Guest viene tracciata per scopi di Governance IT.")
    
    try:
        query_logs = "SELECT * FROM \"Z_SM20_AUDIT\" ORDER BY \"TIMESTAMP\" DESC LIMIT 50;"
        with engine.connect() as conn:
            df_logs = pd.read_sql(text(query_logs), conn)
        
        def color_status(val):
            color = '#E74C3C' if val == 'ERROR' else '#2ECC71'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_logs.style.map(color_status, subset=['STATUS']), use_container_width=True, hide_index=True)
    except:
        st.warning("Nessun log disponibile. Inizia a testare i moduli!")

# =========================================================================
# MODULO: DATA IMPORTER
# =========================================================================
elif modulo == "⚙️ Data Importer (CSV/Gemini)":
    st.title("⚙️ Data Importer & Custom Sandbox")
    uploaded_file = st.file_uploader("Carica CSV", type=["csv"])
    table_name = st.text_input("Nome Tabella SAP (es. Z_DATA):", "Z_CUSTOM_TABLE")
    
    if uploaded_file and st.button("☁️ Carica"):
        try:
            df = pd.read_csv(uploaded_file)
            df.to_sql(table_name.upper(), engine, if_exists='replace', index=False)
            write_audit_log(st.session_state.username, "IMPORTER", f"CREATE TABLE {table_name}", "SUCCESS")
            st.success(f"Tabella {table_name.upper()} caricata con {len(df)} record!")
        except Exception as e:
            write_audit_log(st.session_state.username, "IMPORTER", "UPLOAD_FAILED", "ERROR")
            st.error(e)