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

# --- 2. CONNESSIONE AL DATABASE E FUNZIONI CORE ---
@st.cache_resource
def init_connection():
    try:
        # Se siamo su Streamlit Cloud, prende la stringa dai Secrets
        return create_engine(st.secrets["DATABASE_URL"])
    except Exception:
        # Se siamo sul tuo PC locale, prende la stringa dal file .env
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        return create_engine(db_url)

engine = init_connection()

def get_table_schema(table_name):
    query = f"SELECT * FROM \"{table_name}\" LIMIT 3"
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)

def write_audit_log(username, modulo, query_eseguita, status):
    """Simula la transazione SM20 (Audit Log) di SAP - Tracciamento Silenzioso"""
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
    except Exception:
        pass # Ignora gli errori per non bloccare mai l'app all'utente

# Generazione ID Ospite Anonimo (Frictionless God Mode)
if 'username' not in st.session_state:
    st.session_state.username = f"GUEST_{random.randint(1000, 9999)}"

# --- 3. STRUTTURA DELL'ACADEMY (SIDEBAR) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/SAP_2011_logo.svg/512px-SAP_2011_logo.svg.png", width=100)
    st.markdown("## 🎓 Executive SAP Academy")
    st.markdown(f"**Utente Connesso:** 🟢 `{st.session_state.username}`")
    
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
    st.caption("Exec. Master Cyber Security Candidate @ LUM")

# =========================================================================
# MODULO: MM PROCURE TO PAY
# =========================================================================
if modulo == "MM - Procure to Pay":
    st.title("📦 Modulo MM: Ciclo Passivo (Procure-to-Pay)")
    
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Procurement")
        
        st.markdown("#### 🟢 BEGINNER LEVEL: Fondamentali Logistici")
        st.write("La base di tutto è capire la struttura Testata/Posizione. `EKKO` (Testata) contiene chi e quando. `EKPO` (Posizione) contiene cosa e quanto.")
        st.code('SELECT "EBELN", "LIFNR", "AEDAT" FROM "EKKO" LIMIT 10;', language="sql")
        st.info("💡 **Anatomia:** `EBELN` (Numero Ordine), `LIFNR` (Codice Fornitore), `AEDAT` (Data di Creazione).")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Integrazione EDI e IDoc (WE02/WE09)")
        st.write("Le grandi aziende usano l'EDI. Le transazioni **WE02/WE09** servono per monitorare gli **IDoc**. Un IDoc in ingresso può generare automaticamente un ordine in `EKKO`.")
        st.code("""
        SELECT lfa1."NAME1" AS "Fornitore", SUM(ekpo."NETWR") AS "Spesa Totale"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"
        GROUP BY lfa1."NAME1" ORDER BY "Spesa Totale" DESC;
        """, language="sql")
        st.info("""
        💡 **Anatomia della JOIN:** Il ponte tra logistica e anagrafiche. `EKKO` si collega a `EKPO` tramite l'ordine (`EBELN`). Poi, per non far leggere al manager solo un numero, colleghiamo `EKKO` a `LFA1` (Anagrafica Fornitori) usando `LIFNR` per estrarre la Ragione Sociale (`NAME1`). La funzione `SUM` aggrega il valore netto (`NETWR`).
        """)
        
        st.markdown("#### 🔴 ADVANCED LEVEL: Window Functions e KPI Direzionali")
        st.write("Calcoliamo l'impatto percentuale di un fornitore sulla spesa totale usando `OVER()`.")
        st.code("""
        SELECT 
            lfa1."NAME1" AS "Fornitore",
            SUM(ekpo."NETWR") AS "Spesa",
            ROUND( (SUM(ekpo."NETWR") / SUM(SUM(ekpo."NETWR")) OVER ()) * 100, 2) AS "% sul Totale"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"
        GROUP BY lfa1."NAME1" ORDER BY "Spesa" DESC;
        """, language="sql")
        st.info("💡 **Anatomia Window Function:** `OVER()` è un comando avanzato che permette di calcolare il Gran Totale globale senza dover fare una sub-query. Permette di calcolare dinamicamente l'incidenza percentuale di ogni riga rispetto alla spesa totale aziendale.")

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
            st.markdown("**MARA (Materiali)**")
            st.dataframe(get_table_schema("MARA"), hide_index=True)

    with tab_pratica:
        st.markdown("### 💻 SQL Sandbox & Analytics Dashboard")
        user_query = st.text_area("Dialetto PostgreSQL (S/4HANA):", height=200, key="sandbox_mm", value="SELECT * FROM \"EKKO\" LIMIT 50;")
        
        if st.button("▶️ Esegui (Run)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "MM", user_query, "SUCCESS")
                col_tab, col_chart = st.columns(2)
                with col_tab:
                    st.dataframe(result_df, use_container_width=True)
                with col_chart:
                    if len(result_df.columns) >= 2:
                        col1_name = result_df.columns[0]
                        col2_name = result_df.columns[1]
                        if pd.api.types.is_numeric_dtype(result_df[col2_name]):
                            st.markdown("**📊 SAC Story Mode**")
                            chart_data = result_df.set_index(col1_name)
                            st.bar_chart(chart_data[col2_name], color="#0A6ED1")
                        else:
                            st.info("💡 **SAC Hint:** Per generare un grafico a barre direzionale, assicurati che la tua query estragga una seconda colonna con valori numerici (es. SUM, COUNT). Due colonne di testo non possono generare KPI.")
                    else:
                        st.warning("⚠️ La tua query estrae solo una colonna. Estrai almeno due colonne (es. Fornitore e Spesa) per attivare i grafici automatici.")
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
        st.markdown("#### 🟢 BEGINNER LEVEL: La Partita Doppia in SAP")
        st.write("La chiave per leggere la contabilità `BSEG` è `SHKZG`: 'S' (Dare), 'H' (Avere).")
        st.code('SELECT "BELNR", "BUZEI", "HKONT", "WRBTR" FROM "BSEG" WHERE "SHKZG" = \'S\' LIMIT 10;', language="sql")
        st.info("💡 **Anatomia:** `BELNR` (Documento Contabile), `BUZEI` (Riga Contabile), `HKONT` (Conto Co.Ge.), `WRBTR` (Importo in Valuta).")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Controllo Budget (WBS Elements)")
        st.write("I progetti complessi usano gli elementi **WBS**. In SAC usiamo queste gerarchie per gli alert di over-budgeting.")
        st.code("""
        SELECT 
            ekko."EBELN" AS "Ordine",
            (bseg."WRBTR" - ekpo."NETWR") AS "Varianza EUR"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "BSEG" bseg ON ekko."EBELN" = bseg."EBELN" AND ekpo."EBELP" = bseg."EBELP"
        WHERE bseg."SHKZG" = 'S';
        """, language="sql")
        st.info("💡 **Anatomia della JOIN FI-MM:** Stiamo collegando la logistica alla contabilità per il 3-Way Match. `BSEG` (Contabilità) si aggancia a `EKPO` (Logistica) usando l'Ordine (`EBELN`) e la specifica riga (`EBELP`), calcolando in tempo reale le varianze di prezzo.")
        
        st.markdown("#### 🔴 ADVANCED LEVEL: Logica CASE WHEN per il Bilancio")
        st.write("Trasformiamo l'Avere ('H') in valori negativi per calcolare il saldo reale.")
        st.code("""
        SELECT 
            "BELNR" AS "Documento",
            SUM(CASE WHEN "SHKZG" = 'S' THEN "WRBTR" ELSE -"WRBTR" END) AS "Saldo"
        FROM "BSEG" GROUP BY "BELNR";
        """, language="sql")
        st.info("💡 **Anatomia logica Algebrica:** Il `CASE WHEN` è fondamentale nel modulo FI. Se il segno contabile `SHKZG` è 'S' (Dare, dal tedesco Soll), teniamo l'importo positivo. Altrimenti (Avere, Haben), applichiamo il segno meno `-"WRBTR"`. Il `SUM` raggruppa tutto per verificare se il documento quadra a zero.")

    with tab_dizionario:
        st.subheader("Tracciato Record (S/4HANA Schema)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**BKPF (Testata Contabile)**")
            st.dataframe(get_table_schema("BKPF"), hide_index=True)
        with col2:
            st.markdown("**BSEG (Posizioni Contabili / Libro Giornale)**")
            st.dataframe(get_table_schema("BSEG"), hide_index=True)

    with tab_pratica:
        st.markdown("### 💻 SQL Sandbox & Analytics Dashboard")
        user_query = st.text_area("Dialetto PostgreSQL (S/4HANA):", height=200, key="sandbox_fi", value="SELECT * FROM \"BSEG\" LIMIT 50;")
        if st.button("▶️ Esegui (Run)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "FI", user_query, "SUCCESS")
                col_tab, col_chart = st.columns(2)
                with col_tab:
                    st.dataframe(result_df, use_container_width=True)
                with col_chart:
                    if len(result_df.columns) >= 2:
                        col1_name = result_df.columns[0]
                        col2_name = result_df.columns[1]
                        if pd.api.types.is_numeric_dtype(result_df[col2_name]):
                            st.markdown("**📊 SAC Story Mode**")
                            chart_data = result_df.set_index(col1_name)
                            st.bar_chart(chart_data[col2_name], color="#E74C3C")
                        else:
                            st.info("💡 **SAC Hint:** Estrai un valore numerico nella seconda colonna (es. Varianza, WRBTR) per generare il grafico degli scostamenti.")
                    else:
                        st.warning("⚠️ Estrai almeno due colonne per visualizzare l'analisi grafica.")
            except Exception as e:
                write_audit_log(st.session_state.username, "FI", user_query, "ERROR")
                st.error(f"❌ Errore SQL: {e}")

# =========================================================================
# MODULO: SD ORDER TO CASH
# =========================================================================
elif modulo == "SD - Order to Cash":
    st.title("🚚 Modulo SD: Order to Cash")
    
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Sales")
        st.markdown("#### 🟢 BEGINNER LEVEL: Profilazione Clienti (`KNA1`)")
        st.code('SELECT "KUNNR", "NAME1", "ORT01" FROM "KNA1" LIMIT 10;', language="sql")
        st.info("💡 **Anatomia:** `KUNNR` (Codice Cliente, Kundennummer), `NAME1` (Ragione Sociale), `ORT01` (Città).")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Revenue Recognition")
        st.code("""
        SELECT kna1."NAME1" AS "Cliente", SUM(vbap."NETWR") AS "Fatturato"
        FROM "VBAK" vbak
        JOIN "VBAP" vbap ON vbak."VBELN" = vbap."VBELN"
        JOIN "KNA1" kna1 ON vbak."KUNNR" = kna1."KUNNR"
        GROUP BY kna1."NAME1" ORDER BY "Fatturato" DESC;
        """, language="sql")
        st.info("💡 **Anatomia del Fatturato:** L'ordine di vendita è diviso in `VBAK` (Testata) e `VBAP` (Posizioni). Unendoli al cliente in `KNA1` tramite `KUNNR`, otteniamo i Top Clienti dell'azienda ordinati per fatturato generato.")
        
        st.markdown("#### 🔴 ADVANCED LEVEL: Profit Margin Analysis (Integrazione SD-MM)")
        st.write("Uniamo Vendite e Materiali per estrarre il margine netto reale, KPI definitivo per il Direttore Commerciale.")
        st.code("""
        SELECT 
            kna1."NAME1" AS "Cliente",
            SUM(vbap."NETWR") AS "Ricavi",
            SUM(vbap."NETWR" - (mara."STPRS" * vbap."KWMENG")) AS "Margine Netto"
        FROM "VBAK" vbak
        JOIN "VBAP" vbap ON vbak."VBELN" = vbap."VBELN"
        JOIN "KNA1" kna1 ON vbak."KUNNR" = kna1."KUNNR"
        JOIN "MARA" mara ON vbap."MATNR" = mara."MATNR"
        GROUP BY kna1."NAME1" ORDER BY "Margine Netto" DESC;
        """, language="sql")
        st.info("💡 **Anatomia dell'Estrazione Margine:** Qui il vero Analyst fa la differenza. Attraversiamo 4 tabelle. Troviamo il Ricavo (`vbap.NETWR`) e sottraiamo il Costo del Venduto (Prezzo standard `mara.STPRS` moltiplicato per la quantità venduta `vbap.KWMENG`). Questo è l'unico modo per vedere quanto guadagna *davvero* l'azienda.")

    with tab_dizionario:
        st.subheader("Tracciato Record (S/4HANA Schema)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**VBAK (Testata Vendite)**")
            st.dataframe(get_table_schema("VBAK"), hide_index=True)
            st.markdown("**KNA1 (Clienti)**")
            st.dataframe(get_table_schema("KNA1"), hide_index=True)
        with col2:
            st.markdown("**VBAP (Posizioni Vendite)**")
            st.dataframe(get_table_schema("VBAP"), hide_index=True)

    with tab_pratica:
        st.markdown("### 💻 SQL Sandbox & Analytics Dashboard")
        user_query = st.text_area("Dialetto PostgreSQL (S/4HANA):", height=200, key="sandbox_sd", value="SELECT * FROM \"VBAK\" LIMIT 50;")
        if st.button("▶️ Esegui (Run)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "SD", user_query, "SUCCESS")
                col_tab, col_chart = st.columns(2)
                with col_tab:
                    st.dataframe(result_df, use_container_width=True)
                with col_chart:
                    if len(result_df.columns) >= 2:
                        col1_name = result_df.columns[0]
                        col2_name = result_df.columns[1]
                        if pd.api.types.is_numeric_dtype(result_df[col2_name]):
                            st.markdown("**📊 SAC Story Mode**")
                            chart_data = result_df.set_index(col1_name)
                            st.bar_chart(chart_data[col2_name], color="#2ECC71")
                        else:
                            st.info("💡 **SAC Hint:** Estrai i Ricavi o i Margini come seconda colonna per generare il grafico delle performance di vendita.")
                    else:
                        st.warning("⚠️ Estrai almeno due colonne (es. Cliente e Margine) per attivare la dashboard.")
            except Exception as e:
                write_audit_log(st.session_state.username, "SD", user_query, "ERROR")
                st.error(f"❌ Errore SQL: {e}")

# =========================================================================
# MODULO: PM/PP PLANT & PRODUCTION
# =========================================================================
elif modulo == "PM/PP - Plant & Production":
    st.title("🏭 Moduli PM: Gestione Impianti")
    
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Asset Management")
        st.markdown("#### 🟢 BEGINNER LEVEL: Mappatura Impianto")
        st.code('SELECT "EQUNR", "EQKTX", "KOSTL" FROM "EQUI" LIMIT 10;', language="sql")
        st.info("💡 **Anatomia:** `EQUNR` (Numero Equipment/Macchinario), `EQKTX` (Descrizione Breve Macchina), `KOSTL` (Centro di Costo assegnato).")
        
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Costi di Manutenzione per Macchinario")
        st.code("""
        SELECT equi."EQKTX" AS "Macchinario", SUM(afvc."COST_TOT") AS "Costo Totale"
        FROM "EQUI" equi
        JOIN "AFIH" afih ON equi."EQUNR" = afih."EQUNR"
        JOIN "AFVC" afvc ON afih."AUFNR" = afvc."AUFNR"
        GROUP BY equi."EQKTX" ORDER BY "Costo Totale" DESC;
        """, language="sql")
        st.info("💡 **Anatomia dell'Impianto:** Partiamo dall'asset fisico (`EQUI`), cerchiamo i suoi ordini di intervento (`AFIH`), scendiamo nel dettaglio delle singole operazioni tecniche svolte dai manutentori (`AFVC`) e sommiamo tutti i costi sostenuti (`COST_TOT`).")
        
        st.markdown("#### 🔴 ADVANCED LEVEL: Analisi Predittiva e Tipologia Guasto")
        st.code("""
        SELECT 
            csks."KTEXT" AS "Reparto",
            SUM(CASE WHEN afih."ILART" = 'PM01' THEN afvc."COST_TOT" ELSE 0 END) AS "Emergenze",
            SUM(CASE WHEN afih."ILART" = 'PM02' THEN afvc."COST_TOT" ELSE 0 END) AS "Prevenzione"
        FROM "CSKS" csks
        JOIN "EQUI" equi ON csks."KOSTL" = equi."KOSTL"
        JOIN "AFIH" afih ON equi."EQUNR" = afih."EQUNR"
        JOIN "AFVC" afvc ON afih."AUFNR" = afvc."AUFNR"
        GROUP BY csks."KTEXT";
        """, language="sql")
        st.info("💡 **Anatomia Direzionale:** Dividiamo strategicamente la spesa di ogni reparto (`CSKS.KTEXT`). Il campo `ILART` dell'ordine PM ci dice se l'intervento è PM01 (Riparazione improvvisa/Guasto) o PM02 (Prevenzione ciclica). Usiamo il `CASE WHEN` per incasellare i costi (`AFVC.COST_TOT`) in due colonne separate.")

    with tab_dizionario:
        st.subheader("Tracciato Record (S/4HANA Schema)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**EQUI (Equipment)**")
            st.dataframe(get_table_schema("EQUI"), hide_index=True)
            st.markdown("**AFIH (Testata Ordine PM)**")
            st.dataframe(get_table_schema("AFIH"), hide_index=True)
        with col2:
            st.markdown("**CSKS (Centri di Costo)**")
            st.dataframe(get_table_schema("CSKS"), hide_index=True)
            st.markdown("**AFVC (Operazioni e Costi PM)**")
            st.dataframe(get_table_schema("AFVC"), hide_index=True)

    with tab_pratica:
        st.markdown("### 💻 SQL Sandbox & Analytics Dashboard")
        user_query = st.text_area("Dialetto PostgreSQL (S/4HANA):", height=200, key="sandbox_pm", value="SELECT * FROM \"EQUI\" LIMIT 50;")
        if st.button("▶️ Esegui (Run)"):
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql(text(user_query), conn)
                write_audit_log(st.session_state.username, "PM", user_query, "SUCCESS")
                col_tab, col_chart = st.columns(2)
                with col_tab:
                    st.dataframe(result_df, use_container_width=True)
                with col_chart:
                    if len(result_df.columns) >= 2:
                        col1_name = result_df.columns[0]
                        col2_name = result_df.columns[1]
                        if pd.api.types.is_numeric_dtype(result_df[col2_name]):
                            st.markdown("**📊 SAC Story Mode**")
                            chart_data = result_df.set_index(col1_name)
                            st.bar_chart(chart_data[col2_name], color="#F39C12")
                        else:
                            st.info("💡 **SAC Hint:** Estrai il costo delle operazioni (es. COST_TOT) nella seconda colonna per generare il grafico dei costi di manutenzione.")
                    else:
                        st.warning("⚠️ Estrai almeno due colonne (es. Macchinario e Costo) per attivare la dashboard.")
            except Exception as e:
                write_audit_log(st.session_state.username, "PM", user_query, "ERROR")
                st.error(f"❌ Errore SQL: {e}")

# =========================================================================
# MODULO: CYBER SECURITY (SM20 AUDIT LOG)
# =========================================================================
elif modulo == "🛡️ Cyber Security (SM20)":
    st.title("🛡️ Cyber Security: SAP Audit Log (SM20)")
    st.info("ℹ️ **Privacy & Governance:** Questa sezione simula il tracciamento di sicurezza SM20 di SAP. Il sistema assegna automaticamente un ID univoco anonimo agli utenti per monitorare le attività sui database aziendali senza raccogliere dati personali.")
    
    st.markdown("La tabella sottostante registra in tempo reale chi si collega, da quale modulo opera e, soprattutto, l'esatta stringa di codice eseguita, evidenziando tentativi falliti (ERROR) e query di successo (SUCCESS).")
    
    try:
        query_logs = "SELECT * FROM \"Z_SM20_AUDIT\" ORDER BY \"TIMESTAMP\" DESC LIMIT 100;"
        with engine.connect() as conn:
            df_logs = pd.read_sql(text(query_logs), conn)
        
        def color_status(val):
            color = '#E74C3C' if val == 'ERROR' else '#2ECC71'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_logs.style.map(color_status, subset=['STATUS']), use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.warning("Il file di Log è attualmente vuoto. Esegui la prima operazione nei moduli operativi per generare l'Audit Trail.")

# =========================================================================
# MODULO: DATA IMPORTER (CSV & GEMINI)
# =========================================================================
elif modulo == "⚙️ Data Importer (CSV/Gemini)":
    st.title("⚙️ Data Importer & Custom Sandbox")
    st.markdown("Usa questo spazio per caricare dataset esterni. Le tabelle verranno salvate nel tuo S/4HANA locale.")
    
    st.info("💡 **Vuoi generare un dataset fittizio all'istante?** Clicca sul pulsante qui sotto per aprire Gemini, chiedigli di generare una tabella dati per SAP in formato CSV, salvala sul tuo PC e caricala qui!")
    st.link_button("🧠 Apri Gemini in una nuova scheda", "https://gemini.google.com")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Carica il tuo file CSV", type=["csv"])
    table_name_input = st.text_input("Nome della tabella da creare (es. Z_MY_TABLE):", "Z_CUSTOM_TABLE")
    
    if uploaded_file is not None and st.button("☁️ Carica su Database"):
        try:
            df_upload = pd.read_csv(uploaded_file)
            df_upload.to_sql(table_name_input.upper(), engine, if_exists='replace', index=False)
            write_audit_log(st.session_state.username, "IMPORTER", f"CREATE TABLE {table_name_input.upper()}", "SUCCESS")
            st.success(f"✅ Tabella '{table_name_input.upper()}' creata con successo! ({len(df_upload)} record).")
            st.dataframe(df_upload.head(3))
        except Exception as e:
            write_audit_log(st.session_state.username, "IMPORTER", f"Tentativo UPLOAD Tabella {table_name_input.upper()} FALLITO", "ERROR")
            st.error(f"❌ Errore durante il caricamento: {e}")
            
    st.markdown("---")
    st.markdown("### 💻 Custom SQL Sandbox")
    st.write("Interroga le tabelle custom che hai appena caricato.")
    custom_query = st.text_area("SQL Query:", height=150, value=f"SELECT * FROM \"{table_name_input.upper()}\" LIMIT 10;")
    if st.button("▶️ Esegui Query (F8)"):
        try:
            with engine.connect() as conn:
                res_df = pd.read_sql(text(custom_query), conn)
            write_audit_log(st.session_state.username, "IMPORTER Sandbox", custom_query, "SUCCESS")
            col_tab, col_chart = st.columns(2)
            with col_tab:
                st.dataframe(res_df, use_container_width=True)
            with col_chart:
                if len(res_df.columns) >= 2:
                    col1_name = res_df.columns[0]
                    col2_name = res_df.columns[1]
                    if pd.api.types.is_numeric_dtype(res_df[col2_name]):
                        st.markdown("**📊 Preview**")
                        chart_data = res_df.set_index(col1_name)
                        st.bar_chart(chart_data[col2_name])
                    else:
                        st.info("💡 Se la tua tabella custom ha un valore numerico nella seconda colonna, verrà generato un grafico in automatico.")
                else:
                    st.warning("⚠️ La tua query estrae solo una colonna. Estrai almeno due colonne per abilitare i grafici.")
        except Exception as e:
            write_audit_log(st.session_state.username, "IMPORTER Sandbox", custom_query, "ERROR")
            st.error(f"❌ Errore SQL: {e}")