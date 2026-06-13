import subprocess
import sys

# Automatikusan feltelepítjük a Google Sheets kezeléséhez szükséges csomagokat, ha hiányoznának
try:
    import gspread
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread", "gspread-dataframe"])
    import gspread

import streamlit as st
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# --- GOOGLE SHEETS BEÁLLÍTÁS ---
# IDE MÁSOLD BE A SAJÁT GOOGLE TÁBLÁZATOD LINKJÉT:
TABLAZAT_URL = "https://docs.google.com/spreadsheets/d/1ghAc8MnRFp3hdc2ovtbAUP-ymbRukWwl3qOMKqM-3p4/edit?usp=sharing"

# Csatlakozás a táblázathoz (nyilvános szerkesztő link esetén működik az anonim kliens)
try:
    gc = gspread.public()
    sh = gc.open_by_url(TABLAZAT_URL)
except Exception:
    # Ha a public mód nem támogatott bizonyos környezetben, alternatív elérés
    try:
        gc = gspread.oauth() # Helyi környezetben ha van credential
        sh = gc.open_by_url(TABLAZAT_URL)
    except Exception:
        st.error("Nem sikerült csatlakozni a Google Táblázathoz. Ellenőrizd a linket és hogy a megosztás Szerkesztőre van-e állítva!")

# Alapértelmezett 72 meccs listája
ALAP_MECCSEK = [
    "Mexikó - Dél-afrika", "Dél-korea - Csehország", "Kanada - Bih", "USA - Paraguay",
    "Katar - Svájc", "Brazil - Marokkó", "Anglia - Ausztrália", "Németország - Ghana",
    "Spanyolország - Kolumbia", "Franciaország - Japán", "Argentína - Nigéria", "Olaszország - Irán",
    "Egyiptom - Alizéria", "Honduras - Görögország", "Chile - Kamerun", "Új-zéland - Szlovákia",
    "Elefántcsontpart - Dánia", "Portugália - Észak-korea", "Ukrajna - Kína", "Hollandia - Ausztria",
    "Szerbia - Uruguay", "Paraguay - Algéria", "Oroszország - Szaúd-arábia", "Svédország - Peru",
    "Mexikó - Kanada", "Dél-afrika - Bih", "Dél-korea - USA", "Csehország - Paraguay",
    "Katar - Brazil", "Svájc - Marokkó", "Anglia - Németország", "Ausztrália - Ghana",
    "Spanyolország - Franciaország", "Kolumbia - Japán", "Argentína - Olaszország", "Nigéria - Irán",
    "Egyiptom - Honduras", "Alizéria - Görögország", "Chile - Új-zéland", "Kamerun - Szlovákia",
    "Elefántcsontpart - Portugália", "Dánia - Észak-korea", "Ukrajna - Hollandia", "Kína - Ausztria",
    "Szerbia - Paraguay", "Uruguay - Algéria", "Oroszország - Svédország", "Szaúd-arábia - Peru",
    "Mexikó - Bih", "Dél-afrika - Kanada", "Dél-korea - Paraguay", "Csehország - USA",
    "Katar - Marokkó", "Svájc - Brazil", "Anglia - Ghana", "Ausztrália - Németország",
    "Spanyolország - Japán", "Kolumbia - Franciaország", "Argentína - Irán", "Nigéria - Olaszország",
    "Egyiptom - Görögország", "Alizéria - Honduras", "Chile - Szlovákia", "Kamerun - Új-zéland",
    "Elefántcsontpart - Észak-korea", "Dánia - Portugália", "Ukrajna - Ausztria", "Kína - Hollandia",
    "Szerbia - Algéria", "Uruguay - Paraguay", "Oroszország - Peru", "Szaúd-arábia - Svédország"
]

# --- ADATBETÖLTÉS ÉS MENTÉS ---
def load_data_from_sheets():
    try:
        ws_meccsek = sh.worksheet("meccsek")
        df_m = pd.DataFrame(ws_meccsek.get_all_records())
    except Exception:
        df_m = pd.DataFrame(columns=["Meccs", "valos_hazai", "valos_vendeg"])
    
    try:
        ws_tippek = sh.worksheet("tippek")
        df_t = pd.DataFrame(ws_tippek.get_all_records())
    except Exception:
        df_t = pd.DataFrame(columns=["Jatekos", "Meccs", "tipp_hazai", "tipp_vendeg"])
        
    # Ha üres a meccs táblázat, feltöltjük az alap 72-vel
    if df_m.empty:
        df_m = pd.DataFrame([{"Meccs": m, "valos_hazai": "", "valos_vendeg": ""} for m in ALAP_MECCSEK])
        ws_m = sh.worksheet("meccsek")
        set_with_dataframe(ws_m, df_m)
        
    return df_m, df_t

df_meccsek, df_tippek = load_data_from_sheets()
jatekosok = ["Péter", "Barna", "Boldi", "Dana", "Szaba"]

def pont_szamit(valos_h, valos_v, tipp_h, tipp_v):
    try:
        v_h = int(valos_h)
        v_v = int(valos_v)
        t_h = int(tipp_h)
        t_v = int(tipp_v)
    except (ValueError, TypeError):
        return 0
        
    if v_h == t_h and v_v == t_v:
        return 3
    valos_kim = 1 if v_h > v_v else (2 if v_h < v_v else 0)
    tipp_kim = 1 if t_h > t_v else (2 if t_h < t_v else 0)
    if valos_kim == tipp_kim:
        return 1
    return 0

st.set_page_config(page_title="Foci Tippjáték", layout="wide")
st.title("Közös Foci Tippjáték")

menu = st.sidebar.radio("Navigáció", ["Ranglista és Meccsek", "Tippek leadása", "Admin Panel"])

# 1. RANGLISTA ÉS MECCSEK
if menu == "Ranglista és Meccsek":
    st.header("Aktuális Állás")
    
    osszes_pont = {j: 0 for j in jatekosok}
    meccs_tablazat = []
    
    for _, m_sor in df_meccsek.iterrows():
        m_id = m_sor["Meccs"]
        v_h = m_sor["valos_hazai"]
        v_v = m_sor["valos_vendeg"]
        
        eredmeny_szoveg = f"{v_h}-{v_v}" if (v_h != "" and v_h is not None and v_v != "" and v_v is not None) else "Még nincs végeredmény"
        sor = {"Meccs": m_id, "Végeredmény": eredmeny_szoveg}
        
        for j in jatekosok:
            j_tippek = df_tippek[(df_tippek["Jatekos"] == j) & (df_tippek["Meccs"] == m_id)]
            if not j_tippek.empty:
                t_h = j_tippek.iloc[0]["tipp_hazai"]
                t_v = j_tippek.iloc[0]["tipp_vendeg"]
                pont = pont_szamit(v_h, v_v, t_h, t_v)
                osszes_pont[j] += pont
                sor[f"{j} tipp"] = f"{t_h}-{t_v}"
                sor[f"{j} pont"] = pont
            else:
                sor[f"{j} tipp"] = "-"
                sor[f"{j} pont"] = 0
                
        meccs_tablazat.append(sor)
        
    ranglista_df = pd.DataFrame(list(osszes_pont.items()), columns=["Játékos", "Összes pont"]).sort_values(by="Összes pont", ascending=False)
    st.dataframe(ranglista_df, use_container_width=True, hide_index=True)
    
    st.header("Meccsek részletesen")
    st.dataframe(pd.DataFrame(meccs_tablazat), use_container_width=True, hide_index=True)

# 2. TIPPEK LEADÁSA
elif menu == "Tippek leadása":
    st.header("Tippek rögzítése")
    
    valasztott_jatekos = st.selectbox("Válaszd ki a neved:", jatekosok)
    
    # Aktív meccsek: ahol nincs még valós eredmény beírva
    aktiv_meccsek = df_meccsek[(df_meccsek["valos_hazai"] == "") | (df_meccsek["valos_hazai"].isna())]
    
    if aktiv_meccsek.empty:
        st.success("Jelenleg nincs tippelhető meccs.")
    else:
        st.write(f"Szia {valasztott_jatekos}! Itt adhatod le a tippjeidet a még le nem játszott meccsekre:")
        
        if st.button("Tippek mentése", type="primary"):
            ws_t = sh.worksheet("tippek")
            
            for _, m_sor in aktiv_meccsek.iterrows():
                m_id = m_sor["Meccs"]
                h_ertek = st.session_state.get(f"t_h_{m_id}", 0)
                v_ertek = st.session_state.get(f"t_v_{m_id}", 0)
                
                # Ha már van tippje erre a meccsre, töröljük a régit
                df_tippek = df_tippek[~((df_tippek["Jatekos"] == valasztott_jatekos) & (df_tippek["Meccs"] == m_id))]
                
                # Hozzáadjuk az újat
                uj_sor = pd.DataFrame([{"Jatekos": valasztott_jatekos, "Meccs": m_id, "tipp_hazai": h_ertek, "tipp_vendeg": v_ertek}])
                df_tippek = pd.concat([df_tippek, uj_sor], ignore_index=True)
                
            set_with_dataframe(ws_t, df_tippek)
            st.success("A tippjeidet elmentettem a Google Táblázatba.")
            st.rerun()

        st.write("---")

        for _, m_sor in aktiv_meccsek.iterrows():
            m_id = m_sor["Meccs"]
            
            korabbi = df_tippek[(df_tippek["Jatekos"] == valasztott_jatekos) & (df_tippek["Meccs"] == m_id)]
            alap_h = korabbi.iloc[0]["tipp_hazai"] if not korabbi.empty else 0
            alap_v = korabbi.iloc[0]["tipp_vendeg"] if not korabbi.empty else 0
            
            st.subheader(m_id)
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(f"Hazai tipp", min_value=0, max_value=20, value=int(alap_h), key=f"t_h_{m_id}")
            with col2:
                st.number_input(f"Vendég tipp", min_value=0, max_value=20, value=int(alap_v), key=f"t_v_{m_id}")

# 3. ADMIN PANEL
elif menu == "Admin Panel":
    st.header("Adminisztrációs felület")
    
    st.subheader("Új meccs hozzáadása")
    col1, col2 = st.columns(2)
    with col1:
        hazai_csapat = st.text_input("Hazai csapat neve:")
    with col2:
        vendeg_csapat = st.text_input("Vendég csapat neve:")
        
    if st.button("Meccs létrehozása"):
        if hazai_csapat and vendeg_csapat:
            meccs_kulcs = f"{hazai_csapat} - {vendeg_csapat}"
            if meccs_kulcs not in df_meccsek["Meccs"].values:
                ws_m = sh.worksheet("meccsek")
                uj_meccs = pd.DataFrame([{"Meccs": meccs_kulcs, "valos_hazai": "", "valos_vendeg": ""}])
                df_meccsek = pd.concat([df_meccsek, uj_meccs], ignore_index=True)
                set_with_dataframe(ws_m, df_meccsek)
                st.success(f"Meccs hozzáadva: {meccs_kulcs}")
                st.rerun()
            else:
                st.warning("Ez a meccs már létezik.")
                
    st.write("---")
    
    st.subheader("Eredmények beírása / Meccsek lezárása")
    for index, m_sor in df_meccsek.iterrows():
        m_id = m_sor["Meccs"]
        v_h = m_sor["valos_hazai"]
        v_v = m_sor["valos_vendeg"]
        
        st.write(f"**{m_id}**")
        
        is_checked = (v_h != "" and v_h is not None)
        alap_h = v_h if is_checked else 0
        alap_v = v_v if is_checked else 0
        
        lejatszott = st.checkbox("Lejátszva / Lezárva", value=is_checked, key=f"admin_ch_{m_id}")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            h_gól = st.number_input("Hazai gól", min_value=0, max_value=20, value=int(alap_h), key=f"admin_h_{m_id}", disabled=not lejatszott)
        with col2:
            v_gól = st.number_input("Vendég gól", min_value=0, max_value=20, value=int(alap_v), key=f"admin_v_{m_id}", disabled=not lejatszott)
        with col3:
            st.write("")
            if st.button("Mentés", key=f"btn_{m_id}"):
                ws_m = sh.worksheet("meccsek")
                if lejatszott:
                    df_meccsek.at[index, "valos_hazai"] = h_gól
                    df_meccsek.at[index, "valos_vendeg"] = v_gól
                else:
                    df_meccsek.at[index, "valos_hazai"] = ""
                    df_meccsek.at[index, "valos_vendeg"] = ""
                set_with_dataframe(ws_m, df_meccsek)
                st.success("Eredmény mentve.")
                st.rerun()
        st.write("---")