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

# --- FUNZIONI DI SUPPORTO ---
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
    except Exception as e:
        pass 

# --- 3. ASSEGNAZIONE ANONIMA GUEST ID ---
if 'username' not in st.session_state:
    st.session_state.username = f"GUEST_{random.randint(1000, 9999)}"

# --- 4. STRUTTURA DELL'ACADEMY (SIDEBAR) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/SAP_2011_logo.svg/512px-SAP_2011_logo.svg.png", width=100)
    st.markdown(f"**Utente connesso:** 🟢 `{st.session_state.username}`")
    st.caption("*(Accesso ospite anonimo)*")
    st.markdown("---")
    
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
    st.caption("Ingegnere Gestionale")
    st.caption("SAP Functional Analyst")
    st.caption("*Master Cyber Security LUM*")

# =========================================================================
# MODULO: MM PROCURE TO PAY
# =========================================================================
if modulo == "MM - Procure to Pay":
    st.title("📦 Modulo MM: Ciclo Passivo (Procure-to-Pay)")
    tab_teoria, tab_dizionario, tab_pratica = st.tabs(["📚 Master Handbook", "🗄️ Data Dictionary", "⚔️ Live Sandbox"])
    
    with tab_teoria:
        st.markdown("### 📘 Il Manuale del Data Analyst: Procurement")
        st.markdown("#### 🟡 INTERMEDIATE LEVEL: Aggregazione Spesa")
        st.write("Questa è la query fondamentale per ogni cruscotto acquisti: calcolare quanto abbiamo speso per ogni singolo fornitore.")
        st.code("""
        SELECT lfa1."NAME1" AS "Fornitore", SUM(ekpo."NETWR") AS "Spesa Totale"
        FROM "EKKO" ekko
        JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"
        JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"
        GROUP BY lfa1."NAME1" ORDER BY "Spesa Totale" DESC;
        """, language="sql")
        
        st.markdown("#### 🔬 L'Anatomia della Query (Spiegazione Passo-Passo)")
        st.markdown("""
        * **`SELECT lfa1."NAME1" AS "Fornitore"`**: `LFA1` è l'Anagrafica Fornitori SAP. `NAME1` è la Ragione Sociale. `AS "Fornitore"` serve per dare un nome leggibile alla colonna nel grafico.
        * **`SUM(ekpo."NETWR") AS "Spesa Totale"`**: `EKPO` è la tabella delle Posizioni degli Ordini. `NETWR` è il Valore Netto in Euro. La funzione `SUM()` somma tutti i valori netti di un fornitore.
        * **`FROM "EKKO" ekko`**: `EKKO` è la Testata dell'Ordine. Contiene i dati generali (chi compra, da chi, in che data).
        * **`JOIN "EKPO" ekpo ON ekko."EBELN" = ekpo."EBELN"`**: Colleghiamo Testata e Riga usando la chiave `EBELN` (Numero Ordine di Acquisto).
        * **`JOIN "LFA1" lfa1 ON ekko."LIFNR" = lfa1."LIFNR"`**: Colleghiamo l'Ordine all'Anagrafica usando la chiave `LIFNR` (Codice Fornitore) per estrarre il nome testuale dell'azienda, che in EKKO non c'è.
        """)

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
                    if len(result_df.columns) >= 2 and pd.api.types.is_numeric_dtype(result_df[result_df.columns[1]]):
                        st.markdown("**📊 SAC Story Mode**")
                        st.bar_chart(result_df.set_index(result_df.columns[0])[result_df.columns[1]], color="#0A6ED1")
                    else:
                        st.info("💡 **SAC Hint:** Estrai una seconda colonna numerica per il grafico.")
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
        st.markdown("#### 🔴 ADVANCED LEVEL: Logica CASE WHEN per il Bilancio")
        st.write("La query definitiva per trasformare la logica SAP Dare/Avere in un Saldo algebrico reale per il bilancio (Balance Sheet).")
        st.code("""
        SELECT "BELNR" AS "Documento",
               SUM(CASE WHEN "SHKZG" = 'S' THEN "WRBTR" ELSE -"WRBTR" END) AS "Saldo Netto"
        FROM "BSEG" GROUP BY "BELNR";
        """, language="sql")
        
        st.markdown("#### 🔬 L'Anatomia della Query (Spiegazione Passo-Passo)")
        st.markdown("""
        * **`FROM "BSEG"`**: `BSEG` è il "Libro Giornale" di SAP. Contiene ogni singola riga contabile registrata in azienda.
        * **`SELECT "BELNR" AS "Documento"`**: `BELNR` è il Numero del Documento Contabile (es. una fattura). Lo rinominiamo "Documento" per la reportistica.
        * **`CASE WHEN "SHKZG" = 'S' THEN "WRBTR"`**: `SHKZG` è il segno contabile. La lettera 'S' (dal tedesco *Soll*) significa DARE. Se la riga è in Dare, prendiamo il valore in Euro `WRBTR` così com'è (positivo).
        * **`ELSE -"WRBTR" END`**: Se il segno non è 'S', è 'H' (dal tedesco *Haben*, AVERE). In questo caso, invertiamo il segno matematico dell'importo (`-"WRBTR"`) rendendolo negativo.
        * **`SUM(...) AS "Saldo Netto"`**: Questa funzione prende tutti i valori positivi e negativi di un documento e li somma. Se la quadratura SAP è corretta (principio della partita doppia), la maggior parte dei saldi dei documenti totali dovrebbe dare zero.
        * **`GROUP BY "BELNR"`**: Raggruppiamo i calcoli per singolo documento.
        """)

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
                    if len(result_df.columns) >= 2 and pd.api.types.is_numeric_dtype(result_df[result_df.columns[1]]):
                        st.markdown("**📊 SAC Story Mode**")
                        st.bar_chart(result_df.set_index(result_df.columns[0])[result_df.columns[1]], color="#E74C3C")
                    else:
                        st.info("💡 **SAC Hint:** Estrai un valore numerico nella seconda colonna per generare il grafico.")
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
        st.markdown("#### 🔴 ADVANCED LEVEL: Profit Margin Analysis (SD-MM)")
        st.write("Come estrarre il VERO margine di profitto unendo le vendite (SD) ai costi dei materiali (MM).")
        st.code("""
        SELECT kna1."NAME1" AS "Cliente",
               SUM(vbap."NETWR" - (mara."STPRS" * vbap."KWMENG")) AS "Margine Netto EUR"
        FROM "VBAK" vbak
        JOIN "VBAP" vbap ON vbak."VBELN" = vbap."VBELN"
        JOIN "KNA1" kna1 ON vbak."KUNNR" = kna1."KUNNR"
        JOIN "MARA" mara ON vbap."MATNR" = mara."MATNR"
        GROUP BY kna1."NAME1" ORDER BY "Margine Netto EUR" DESC;
        """, language="sql")
        
        st.markdown("#### 🔬 L'Anatomia della Query (Spiegazione Passo-Passo)")
        st.markdown("""
        * **`FROM "VBAK" vbak JOIN "VBAP" vbap ...`**: Partiamo dalla Testata Ordini di Vendita (`VBAK`) e la uniamo alle sue righe interne (`VBAP`) usando `VBELN` (Numero Ordine).
        * **`JOIN "KNA1" kna1 ...`**: Colleghiamo l'ordine al cliente (`KNA1`) tramite `KUNNR` (Codice Cliente) per mostrare il nome dell'azienda e non un numero anonimo.
        * **`JOIN "MARA" mara ...`**: Colleghiamo la riga di vendita all'Anagrafica Materiali (`MARA`) tramite `MATNR` (Codice Materiale). Questo è il "ponte" tra vendite e logistica.
        * **`SUM(vbap."NETWR" - (mara."STPRS" * vbap."KWMENG"))`**: Il cuore analitico. 
            * `vbap.NETWR` = Quanto ha pagato il cliente (Ricavo).
            * `mara.STPRS` = Quanto costa a noi produrre 1 pezzo (Prezzo Standard SAP).
            * `vbap.KWMENG` = Quanti pezzi gli abbiamo venduto.
            * *Logica:* Ricavo - (Costo Unitario * Quantità) = **Margine di Profitto Puro**.
        """)

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
                    if len(result_df.columns) >= 2 and pd.api.types.is_numeric_dtype(result_df[result_df.columns[1]]):
                        st.markdown("**📊 SAC Story Mode**")
                        st.bar_chart(result_df.set_index(result_df.columns[0])[result_df.columns[1]], color="#2ECC71")
                    else:
                        st.info("💡 **SAC Hint:** Estrai i Margini come seconda colonna per il grafico.")
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
        st.markdown("#### 🔴 ADVANCED LEVEL: Tipologia Guasto (PM01 vs PM02)")
        st.write("Come separare i costi di Manutenzione a Guasto (Emergenze) dalla Manutenzione Preventiva per Centro di Costo.")
        st.code("""
        SELECT csks."KTEXT" AS "Reparto",
               SUM(CASE WHEN afih."ILART" = 'PM01' THEN afvc."COST_TOT" ELSE 0 END) AS "Emergenze",
               SUM(CASE WHEN afih."ILART" = 'PM02' THEN afvc."COST_TOT" ELSE 0 END) AS "Prevenzione"
        FROM "CSKS" csks
        JOIN "EQUI" equi ON csks."KOSTL" = equi."KOSTL"
        JOIN "AFIH" afih ON equi."EQUNR" = afih."EQUNR"
        JOIN "AFVC" afvc ON afih."AUFNR" = afvc."AUFNR"
        GROUP BY csks."KTEXT";
        """, language="sql")
        
        st.markdown("#### 🔬 L'Anatomia della Query (Spiegazione Passo-Passo)")
        st.markdown("""
        * **`FROM "CSKS" ... JOIN "EQUI" ...`**: `CSKS` è l'anagrafica dei Centri di Costo (i reparti fisici). Lo colleghiamo a `EQUI` (i Macchinari fisici) tramite `KOSTL` (Centro di costo).
        * **`JOIN "AFIH" ... JOIN "AFVC" ...`**: `AFIH` è l'Ordine di Manutenzione (l'intervento). Lo uniamo ad `AFVC`, che contiene le singole operazioni tecniche e i costi orari (`COST_TOT`).
        * **`CASE WHEN afih."ILART" = 'PM01'`**: `ILART` è il campo SAP per il "Tipo Manutenzione". `PM01` indica un macchinario rotto (Guasto Improvviso). 
        * **`THEN afvc."COST_TOT" ELSE 0`**: Se è PM01, prendiamo il costo. Se non lo è, aggiungiamo zero (non lo contiamo). Facciamo la stessa cosa in una seconda colonna per `PM02` (Manutenzione Preventiva programmata).
        * **Risultato:** Il direttore d'impianto vedrà esattamente quali reparti sprecano soldi rincorrendo le emergenze, e quali investono saggiamente in prevenzione.
        """)

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
                    if len(result_df.columns) >= 2 and pd.api.types.is_numeric_dtype(result_df[result_df.columns[1]]):
                        st.markdown("**📊 SAC Story Mode**")
                        st.bar_chart(result_df.set_index(result_df.columns[0])[result_df.columns[1]], color="#F39C12")
                    else:
                        st.info("💡 **SAC Hint:** Estrai i Costi nella seconda colonna per generare il grafico.")
            except Exception as e:
                write_audit_log(st.session_state.username, "PM", user_query, "ERROR")
                st.error(f"❌ Errore SQL: {e}")

# =========================================================================
# MODULO: CYBER SECURITY (SM20 AUDIT LOG)
# =========================================================================
elif modulo == "🛡️ Cyber Security (SM20)":
    st.title("🛡️ Cyber Security: SAP Audit Log (SM20)")
    
    st.info("ℹ️ **Privacy Policy & GDPR Compliance:** Nessun dato personale o IP viene salvato. Il sistema assegna un ID ospite anonimo a scopo puramente dimostrativo. I log del database vengono periodicamente resettati.")
    
    st.markdown("Questa schermata simula la transazione **SM20 di SAP**. Mostra in tempo reale il monitoraggio del Database: chi si è connesso, quando, in quale modulo e la sintassi esatta delle query eseguite. Uno strumento vitale per la Governance IT e la Data Security.")
    
    try:
        query_logs = "SELECT * FROM \"Z_SM20_AUDIT\" ORDER BY \"TIMESTAMP\" DESC LIMIT 100;"
        with engine.connect() as conn:
            df_logs = pd.read_sql(text(query_logs), conn)
        
        def color_status(val):
            color = '#E74C3C' if val == 'ERROR' else '#2ECC71'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_logs.style.map(color_status, subset=['STATUS']), use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.info("Nessun log presente al momento. Lancia qualche query nella Sandbox per attivare l'Audit Log!")

# =========================================================================
# MODULO: DATA IMPORTER (CSV & GEMINI)
# =========================================================================
elif modulo == "⚙️ Data Importer":
    st.title("⚙️ Data Importer & Custom Sandbox")
    st.markdown("Usa questo spazio per caricare dataset esterni.")
    st.info("💡 **Vuoi generare un dataset fittizio all'istante?** Clicca sul pulsante qui sotto per aprire Gemini, chiedigli di generare un file CSV, e caricalo qui!")
    st.link_button("🧠 Apri Gemini in una nuova scheda", "https://gemini.google.com")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Carica il tuo file CSV", type=["csv"])
    table_name_input = st.text_input("Nome della tabella da creare (es. Z_MY_TABLE):", "Z_CUSTOM_TABLE")
    
    if uploaded_file is not None and st.button("☁️ Carica su Database"):
        try:
            df_upload = pd.read_csv(uploaded_file)
            df_upload.to_sql(table_name_input.upper(), engine, if_exists='replace', index=False)
            write_audit_log(st.session_state.username, "IMPORTER", f"Creata tabella: {table_name_input.upper()}", "SUCCESS")
            st.success(f"✅ Tabella '{table_name_input.upper()}' creata con successo! ({len(df_upload)} record).")
            st.dataframe(df_upload.head(3))
        except Exception as e:
            write_audit_log(st.session_state.username, "IMPORTER", f"Tentativo creazione tabella fallito", "ERROR")
            st.error(f"❌ Errore durante il caricamento: {e}")