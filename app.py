import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

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

# Kapcsolat létrehozása a Google Sheets-szel (a titkos beállításokból olvassa be a linket)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data_from_sheets():
    try:
        df_m = conn.read(worksheet="meccsek", ttl=0)
        # Ha a beolvasott táblázat teljesen üres vagy hibás formátumú
        if df_m.empty or "Meccs" not in df_m.columns:
            raise Exception("Ures")
    except Exception:
        df_m = pd.DataFrame([{"Meccs": m, "valos_hazai": "", "valos_vendeg": ""} for m in ALAP_MECCSEK])
        conn.update(worksheet="meccsek", data=df_m)
    
    try:
        df_t = conn.read(worksheet="tippek", ttl=0)
        if df_t.empty or "Jatekos" not in df_t.columns:
            df_t = pd.DataFrame(columns=["Jatekos", "Meccs", "tipp_hazai", "tipp_vendeg"])
    except Exception:
        df_t = pd.DataFrame(columns=["Jatekos", "Meccs", "tipp_hazai", "tipp_vendeg"])
        
    return df_m, df_t

df_meccsek, df_tippek = load_data_from_sheets()
jatekosok = ["Péter", "Barna", "Boldi", "Dana", "Szaba"]

def pont_szamit(valos_h, valos_v, tipp_h, tipp_v):
    try:
        if pd.isna(valos_h) or pd.isna(valos_v) or valos_h == "" or valos_v == "":
            return 0
        v_h, v_v = int(valos_h), int(valos_v)
        t_h, t_v = int(tipp_h), int(tipp_v)
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
        
        has_eredmeny = not pd.isna(v_h) and v_h != "" and not pd.isna(v_v) and v_v != ""
        eredmeny_szoveg = f"{int(v_h)}-{int(v_v)}" if has_eredmeny else "Még nincs végeredmény"
        sor = {"Meccs": m_id, "Végeredmény": eredmeny_szoveg}
        
        for j in jatekosok:
            j_tippek = df_tippek[(df_tippek["Jatekos"] == j) & (df_tippek["Meccs"] == m_id)]
            if not j_tippek.empty:
                t_h = j_tippek.iloc[0]["tipp_hazai"]
                t_v = j_tippek.iloc[0]["tipp_vendeg"]
                pont = pont_szamit(v_h, v_v, t_h, t_v)
                osszes_pont[j] += pont
                sor[f"{j} tipp"] = f"{int(t_h)}-{int(t_v)}"
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
    
    aktiv_meccsek = df_meccsek[df_meccsek["valos_hazai"].isna() | (df_meccsek["valos_hazai"] == "")]
    
    if aktiv_meccsek.empty:
        st.success("Jelenleg nincs tippelhető meccs.")
    else:
        st.write(f"Szia {valasztott_jatekos}! Itt adhatod le a tippjeidet:")
        
        if st.button("Tippek mentése", type="primary"):
            for _, m_sor in aktiv_meccsek.iterrows():
                m_id = m_sor["Meccs"]
                h_ertek = st.session_state.get(f"t_h_{m_id}", 0)
                v_ertek = st.session_state.get(f"t_v_{m_id}", 0)
                
                df_tippek = df_tippek[~((df_tippek["Jatekos"] == valasztott_jatekos) & (df_tippek["Meccs"] == m_id))]
                uj_sor = pd.DataFrame([{"Jatekos": valasztott_jatekos, "Meccs": m_id, "tipp_hazai": int(h_ertek), "tipp_vendeg": int(v_ertek)}])
                df_tippek = pd.concat([df_tippek, uj_sor], ignore_index=True)
                
            conn.update(worksheet="tippek", data=df_tippek)
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
                uj_meccs = pd.DataFrame([{"Meccs": meccs_kulcs, "valos_hazai": "", "valos_vendeg": ""}])
                df_meccsek = pd.concat([df_meccsek, uj_meccs], ignore_index=True)
                conn.update(worksheet="meccsek", data=df_meccsek)
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
        is_checked = not pd.isna(v_h) and v_h != ""
        alap_h = v_h if is_checked else 0
        alap_v = v_v if is_checked else 0
        
        lejatszott = st.checkbox("Lejátszva / Lezárva", value=is_checked, key=f"admin_ch_{index}")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            h_gól = st.number_input("Hazai gól", min_value=0, max_value=20, value=int(alap_h), key=f"admin_h_{index}", disabled=not lejatszott)
        with col2:
            v_gól = st.number_input("Vendég gól", min_value=0, max_value=20, value=int(alap_v), key=f"admin_v_{index}", disabled=not lejatszott)
        with col3:
            st.write("")
            if st.button("Mentés", key=f"btn_{index}"):
                if lejatszott:
                    df_meccsek.at[index, "valos_hazai"] = int(h_gól)
                    df_meccsek.at[index, "valos_vendeg"] = int(v_gól)
                else:
                    df_meccsek.at[index, "valos_hazai"] = ""
                    df_meccsek.at[index, "valos_vendeg"] = ""
                conn.update(worksheet="meccsek", data=df_meccsek)
                st.success("Eredmény mentve.")
                st.rerun()
        st.write("---")