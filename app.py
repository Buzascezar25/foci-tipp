import streamlit as st
import pandas as pd
import json
import os
import copy

DB_FILE = "tippjatek_adatok.json"

# ==========================================
# 1. ADATOK ÉS STRUKTÚRÁK DEFINIÁLÁSA
# ==========================================

# A hivatalos 2026-os világbajnokság 72 csoportmeccse zászlókkal
ALAP_MECCSEK = [
    # 1. Forduló
    "Mexikó 🇲🇽 - Dél-Afrika 🇿🇦", "Dél-Korea 🇰🇷 - Csehország 🇨🇿",
    "Kanada 🇨🇦 - Bosznia-Hercegovina 🇧🇦", "Katar 🇶🇦 - Svájc 🇨🇭",
    "Brazília 🇧🇷 - Marokkó 🇲🇦", "Haiti 🇭🇹 - Skócia 🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA 🇺🇸 - Paraguay 🇵🇾", "Ausztrália 🇦🇺 - Törökország 🇹🇷",
    "Németország 🇩🇪 - Curaçao 🇨🇼", "Elefántcsontpart 🇨🇮 - Ecuador 🇪🇨",
    "Hollandia 🇳🇱 - Japán 🇯🇵", "Svédország 🇸🇪 - Tunézia 🇹🇳",
    "Belgium 🇧🇪 - Egyiptom 🇪🇬", "Irán 🇮🇷 - Új-Zéland 🇳🇿",
    "Spanyolország 🇪🇸 - Zöld-foki-szigetek 🇨🇻", "Szaúd-Arábia 🇸🇦 - Uruguay 🇺🇾",
    "Franciaország 🇫🇷 - Szenegál 🇸🇳", "Irak 🇮🇶 - Norvégia 🇳🇴",
    "Argentína 🇦🇷 - Algéria 🇩🇿", "Ausztria 🇦🇹 - Jordánia 🇯🇴",
    "Portugália 🇵🇹 - Kongói DK 🇨🇩", "Üzbegisztán 🇺🇿 - Kolumbia 🇨🇴",
    "Ghána 🇬🇭 - Panama 🇵🇦", "Anglia 🏴󠁧󠁢󠁥󠁮󠁧󠁿 - Horvátország 🇭🇷",

    # 2. Forduló
    "Csehország 🇨🇿 - Dél-Afrika 🇿🇦", "Mexikó 🇲🇽 - Dél-Korea 🇰🇷",
    "Svájc 🇨🇭 - Bosznia-Hercegovina 🇧🇦", "Kanada 🇨🇦 - Katar 🇶🇦",
    "Skócia 🏴󠁧󠁢󠁳󠁣󠁴󠁿 - Marokkó 🇲🇦", "Brazília 🇧🇷 - Haiti 🇭🇹",
    "Törökország 🇹🇷 - Paraguay 🇵🇾", "USA 🇺🇸 - Ausztrália 🇦🇺",
    "Ecuador 🇪🇨 - Curaçao 🇨🇼", "Németország 🇩🇪 - Elefántcsontpart 🇨🇮",
    "Tunézia 🇹🇳 - Japán 🇯🇵", "Hollandia 🇳🇱 - Svédország 🇸🇪",
    "Új-Zéland 🇳🇿 - Egyiptom 🇪🇬", "Belgium 🇧🇪 - Irán 🇮🇷",
    "Uruguay 🇺🇾 - Zöld-foki-szigetek 🇨🇻", "Spanyolország 🇪🇸 - Szaúd-Arábia 🇸🇦",
    "Norvégia 🇳🇴 - Szenegál 🇸🇳", "Franciaország 🇫🇷 - Irak 🇮🇶",
    "Jordánia 🇯🇴 - Algéria 🇩🇿", "Argentína 🇦🇷 - Ausztria 🇦🇹",
    "Kolumbia 🇨🇴 - Kongói DK 🇨🇩", "Portugália 🇵🇹 - Üzbegisztán 🇺🇿",
    "Horvátország 🇭🇷 - Panama 🇵🇦", "Ghána 🇬🇭 - Anglia 🏴󠁧󠁢󠁥󠁮󠁧󠁿",

    # 3. Forduló
    "Csehország 🇨🇿 - Mexikó 🇲🇽", "Dél-Afrika 🇿🇦 - Dél-Korea 🇰🇷",
    "Svájc 🇨🇭 - Kanada 🇨🇦", "Bosznia-Hercegovina 🇧🇦 - Katar 🇶🇦",
    "Skócia 🏴󠁧󠁢󠁳󠁣󠁴󠁿 - Brazília 🇧🇷", "Marokkó 🇲🇦 - Haiti 🇭🇹",
    "Törökország 🇹🇷 - USA 🇺🇸", "Paraguay 🇵🇾 - Ausztrália 🇦🇺",
    "Ecuador 🇪🇨 - Németország 🇩🇪", "Curaçao 🇨🇼 - Elefántcsontpart 🇨🇮",
    "Tunézia 🇹🇳 - Hollandia 🇳🇱", "Japán 🇯🇵 - Svédország 🇸🇪",
    "Új-Zéland 🇳🇿 - Belgium 🇧🇪", "Egyiptom 🇪🇬 - Irán 🇮🇷",
    "Uruguay 🇺🇾 - Spanyolország 🇪🇸", "Zöld-foki-szigetek 🇨🇻 - Szaúd-Arábia 🇸🇦",
    "Norvégia 🇳🇴 - Franciaország 🇫🇷", "Szenegál 🇸🇳 - Irak 🇮🇶",
    "Jordánia 🇯🇴 - Argentína 🇦🇷", "Algéria 🇩🇿 - Ausztria 🇦🇹",
    "Kolumbia 🇨🇴 - Portugália 🇵🇹", "Kongói DK 🇨🇩 - Üzbegisztán 🇺🇿",
    "Horvátország 🇭🇷 - Ghána 🇬🇭", "Panama 🇵🇦 - Anglia 🏴󠁧󠁢󠁥󠁮󠁧󠁿"
]

# A kieséses szakasz logikai ágrajza a beküldött képek alapján
KO_ALAP_STRUKTURA = {
    # Legjobb 32 (Round of 32)
    "R32_1": {"nev": "Legjobb 32 - 1. meccs", "hazai": "Németország", "vendeg": "Paraguay ", "next": "R16_1", "next_pos": "hazai"},
    "R32_2": {"nev": "Legjobb 32 - 2. meccs", "hazai": "Franciaország ", "vendeg": "Svédország ", "next": "R16_1", "next_pos": "vendeg"},
    "R32_3": {"nev": "Legjobb 32 - 3. meccs", "hazai": "Dél-Afrika ", "vendeg": "Kanada ", "next": "R16_2", "next_pos": "hazai"},
    "R32_4": {"nev": "Legjobb 32 - 4. meccs", "hazai": "Hollandia ", "vendeg": "Marokkó ", "next": "R16_2", "next_pos": "vendeg"},
    "R32_5": {"nev": "Legjobb 32 - 5. meccs", "hazai": "Portugália ", "vendeg": "Horvátország ", "next": "R16_3", "next_pos": "hazai"},
    "R32_6": {"nev": "Legjobb 32 - 6. meccs", "hazai": "Spanyolország ", "vendeg": "Ausztria ", "next": "R16_3", "next_pos": "vendeg"},
    "R32_7": {"nev": "Legjobb 32 - 7. meccs", "hazai": "USA ", "vendeg": "Bosznia-Hercegovina ", "next": "R16_4", "next_pos": "hazai"},
    "R32_8": {"nev": "Legjobb 32 - 8. meccs", "hazai": "Belgium ", "vendeg": "Szenegál ", "next": "R16_4", "next_pos": "vendeg"},
    "R32_9": {"nev": "Legjobb 32 - 9. meccs", "hazai": "Brazília ", "vendeg": "Japán ", "next": "R16_5", "next_pos": "hazai"},
    "R32_10": {"nev": "Legjobb 32 - 10. meccs", "hazai": "Elefántcsontpart ", "vendeg": "Norvégia ", "next": "R16_5", "next_pos": "vendeg"},
    "R32_11": {"nev": "Legjobb 32 - 11. meccs", "hazai": "Mexikó ", "vendeg": "Ecuador ", "next": "R16_6", "next_pos": "hazai"},
    "R32_12": {"nev": "Legjobb 32 - 12. meccs", "hazai": "Anglia ", "vendeg": "Kongói ", "next": "R16_6", "next_pos": "vendeg"},
    "R32_13": {"nev": "Legjobb 32 - 13. meccs", "hazai": "Argentína ", "vendeg": "Zöld-foki-szigetek ", "next": "R16_7", "next_pos": "hazai"},
    "R32_14": {"nev": "Legjobb 32 - 14. meccs", "hazai": "Ausztrália 🇦🇺", "vendeg": "Egyiptom ", "next": "R16_7", "next_pos": "vendeg"},
    "R32_15": {"nev": "Legjobb 32 - 15. meccs", "hazai": "Svájc ", "vendeg": "Algéria ", "next": "R16_8", "next_pos": "hazai"},
    "R32_16": {"nev": "Legjobb 32 - 16. meccs", "hazai": "Kolumbia ", "vendeg": "Ghána ", "next": "R16_8", "next_pos": "vendeg"},
    
    # Nyolcaddöntő (Round of 16)
    "R16_1": {"nev": "Nyolcaddöntő 1", "hazai": "TBD", "vendeg": "TBD", "next": "QF_1", "next_pos": "hazai"},
    "R16_2": {"nev": "Nyolcaddöntő 2", "hazai": "TBD", "vendeg": "TBD", "next": "QF_1", "next_pos": "vendeg"},
    "R16_3": {"nev": "Nyolcaddöntő 3", "hazai": "TBD", "vendeg": "TBD", "next": "QF_2", "next_pos": "hazai"},
    "R16_4": {"nev": "Nyolcaddöntő 4", "hazai": "TBD", "vendeg": "TBD", "next": "QF_2", "next_pos": "vendeg"},
    "R16_5": {"nev": "Nyolcaddöntő 5", "hazai": "TBD", "vendeg": "TBD", "next": "QF_3", "next_pos": "hazai"},
    "R16_6": {"nev": "Nyolcaddöntő 6", "hazai": "TBD", "vendeg": "TBD", "next": "QF_3", "next_pos": "vendeg"},
    "R16_7": {"nev": "Nyolcaddöntő 7", "hazai": "TBD", "vendeg": "TBD", "next": "QF_4", "next_pos": "hazai"},
    "R16_8": {"nev": "Nyolcaddöntő 8", "hazai": "TBD", "vendeg": "TBD", "next": "QF_4", "next_pos": "vendeg"},
    
    # Negyeddöntő (Quarterfinals)
    "QF_1": {"nev": "Negyeddöntő 1", "hazai": "TBD", "vendeg": "TBD", "next": "SF_1", "next_pos": "hazai"},
    "QF_2": {"nev": "Negyeddöntő 2", "hazai": "TBD", "vendeg": "TBD", "next": "SF_1", "next_pos": "vendeg"},
    "QF_3": {"nev": "Negyeddöntő 3", "hazai": "TBD", "vendeg": "TBD", "next": "SF_2", "next_pos": "hazai"},
    "QF_4": {"nev": "Negyeddöntő 4", "hazai": "TBD", "vendeg": "TBD", "next": "SF_2", "next_pos": "vendeg"},
    
    # Elődöntő (Semifinals)
    "SF_1": {"nev": "Elődöntő 1", "hazai": "TBD", "vendeg": "TBD", "next": "F_1", "next_pos": "hazai"},
    "SF_2": {"nev": "Elődöntő 2", "hazai": "TBD", "vendeg": "TBD", "next": "F_1", "next_pos": "vendeg"},
    
    # Döntő (Final)
    "F_1": {"nev": "Döntő", "hazai": "TBD", "vendeg": "TBD", "next": None, "next_pos": None},
}

# ==========================================
# 2. ADATBÁZIS KEZELÉS ÉS PONTOSÍTÁS
# ==========================================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            adat = json.load(f)
            if "ko_eredmenyek" not in adat: adat["ko_eredmenyek"] = {}
            if "ko_tippek" not in adat: adat["ko_tippek"] = {}
            return adat
            
    alap_struktura = {"meccsek": {}, "tippek": {}, "ko_eredmenyek": {}, "ko_tippek": {}}
    for meccs in ALAP_MECCSEK:
        alap_struktura["meccsek"][meccs] = {"valos_hazai": None, "valos_vendeg": None}
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(alap_struktura, f, ensure_ascii=False, indent=4)
    return alap_struktura

def save_data(adat):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(adat, f, ensure_ascii=False, indent=4)

data = load_data()
jatekosok = ["Péter", "Barna", "Boldi", "Dana", "Szaba"]

def pont_szamit(valos_h, valos_v, tipp_h, tipp_v):
    if valos_h is None or valos_v is None or tipp_h is None or tipp_v is None:
        return 0, False
    if valos_h == tipp_h and valos_v == tipp_v:
        return 3, True
    valos_kim = 1 if valos_h > valos_v else (2 if valos_h < valos_v else 0)
    tipp_kim = 1 if tipp_h > tipp_v else (2 if tipp_h < tipp_v else 0)
    if valos_kim == tipp_kim:
        return 1, False
    return 0, False

def ko_pont_szamit(valos_h, valos_v, valos_tovabb, tipp_h, tipp_v, tipp_tovabb):
    if valos_h is None or valos_v is None or valos_tovabb is None or valos_tovabb == 0:
        return 0, False
    alap_pont, telitalalat = pont_szamit(valos_h, valos_v, tipp_h, tipp_v)
    plusz_pont = 1 if (valos_tovabb == tipp_tovabb and valos_tovabb in [1, 2]) else 0
    return alap_pont + plusz_pont, telitalalat

def get_aktualis_bracket():
    bracket = copy.deepcopy(KO_ALAP_STRUKTURA)
    for szakasz in ["R32", "R16", "QF", "SF", "F"]:
        for m_id, m_adat in bracket.items():
            if m_id.startswith(szakasz):
                if m_id in data.get("ko_eredmenyek", {}):
                    eredmeny = data["ko_eredmenyek"][m_id]
                    tovabbjuto = eredmeny.get("tovabbjuto")
                    gyoztes = m_adat["hazai"] if tovabbjuto == 1 else (m_adat["vendeg"] if tovabbjuto == 2 else None)
                    
                    next_match = m_adat["next"]
                    next_pos = m_adat["next_pos"]
                    if next_match and gyoztes:
                        bracket[next_match][next_pos] = gyoztes
    return bracket

aktualis_bracket = get_aktualis_bracket()

# ==========================================
# 3. FELHASZNÁLÓI FELÜLET (ROUTER FIX)
# ==========================================
st.set_page_config(page_title="Foci Tippjáték", layout="wide")
st.title("🏆 Közös Foci Tippjáték")

# Szigorúan tiszta szöveges menü az összeomlások elkerülésére
menu = st.sidebar.radio("Navigáció", ["Ranglista és Meccsek", "Tippek leadása", "Admin Panel"])

# --- 1. MENÜPONT: RANGLISTA ÉS MECCSEK ---
if menu == "Ranglista és Meccsek":
    st.header("📊 Aktuális Ranglista")
    
    tab1, tab2 = st.tabs(["🏟️ Csoportkör", "🏆 Egyenes Kieséses Szakasz"])
    
    osszes_pont = {j: 0 for j in jatekosok}
    telitalalatok = {j: 0 for j in jatekosok}
    
    for m_id, m_adat in data["meccsek"].items():
        v_h, v_v = m_adat["valos_hazai"], m_adat["valos_vendeg"]
        for j in jatekosok:
            tipp = data["tippek"].get(j, {}).get(m_id, None)
            if tipp:
                pont, is_teli = pont_szamit(v_h, v_v, tipp[0], tipp[1])
                osszes_pont[j] += pont
                if is_teli: telitalalatok[j] += 1

    for m_id, m_adat in data.get("ko_eredmenyek", {}).items():
        v_h, v_v, v_tovabb = m_adat.get("v_h"), m_adat.get("v_v"), m_adat.get("tovabbjuto")
        for j in jatekosok:
            tipp = data.get("ko_tippek", {}).get(j, {}).get(m_id, None)
            if tipp:
                pont, is_teli = ko_pont_szamit(v_h, v_v, v_tovabb, tipp["h"], tipp["v"], tipp["tovabbjuto"])
                osszes_pont[j] += pont
                if is_teli: telitalalatok[j] += 1

    ranglista_adatok = [{"Játékos": j, "Összes pont": osszes_pont[j], "Telitalálatok (3p)": telitalalatok[j]} for j in jatekosok]
    ranglista_df = pd.DataFrame(ranglista_adatok).sort_values(by=["Összes pont", "Telitalálatok (3p)"], ascending=[False, False])
    st.dataframe(ranglista_df, use_container_width=True, hide_index=True)
    st.write("---")
    
    with tab1:
        st.subheader("Csoportmérkőzések Részletesen")
        meccs_tablazat = []
        for m_id, m_adat in data["meccsek"].items():
            v_h, v_v = m_adat["valos_hazai"], m_adat["valos_vendeg"]
            eredmeny_szoveg = f"{v_h}-{v_v}" if v_h is not None else "Még nincs végeredmény"
            sor = {"Meccs": m_id, "Végeredmény": eredmeny_szoveg}
            for j in jatekosok:
                tipp = data["tippek"].get(j, {}).get(m_id, None)
                if tipp:
                    pont, _ = pont_szamit(v_h, v_v, tipp[0], tipp[1])
                    sor[f"{j} tipp"] = f"{tipp[0]}-{tipp[1]}"
                    sor[f"{j} pont"] = pont
                else:
                    sor[f"{j} tipp"] = "-"
                    sor[f"{j} pont"] = 0
            meccs_tablazat.append(sor)
        st.dataframe(pd.DataFrame(meccs_tablazat), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Kieséses Szakasz Részletesen")
        ko_tablazat = []
        for m_id, bracket_adat in aktualis_bracket.items():
            eredmeny_adat = data.get("ko_eredmenyek", {}).get(m_id, {})
            v_h = eredmeny_adat.get("v_h")
            v_v = eredmeny_adat.get("v_v")
            v_tovabb = eredmeny_adat.get("tovabbjuto")
            
            nev_szoveg = f"{bracket_adat['nev']}: {bracket_adat['hazai']} - {bracket_adat['vendeg']}"
            if v_h is not None:
                tovabb_nev = bracket_adat['hazai'] if v_tovabb == 1 else bracket_adat['vendeg']
                eredmeny_szoveg = f"{v_h}-{v_v} (Tovább: {tovabb_nev})"
            else:
                eredmeny_szoveg = "Még nincs eredmény"
                
            sor = {"Mérkőzés": nev_szoveg, "Végeredmény": eredmeny_szoveg}
            for j in jatekosok:
                tipp = data.get("ko_tippek", {}).get(j, {}).get(m_id, None)
                if tipp:
                    pont, _ = ko_pont_szamit(v_h, v_v, v_tovabb, tipp["h"], tipp["v"], tipp["tovabbjuto"])
                    t_t_nev = bracket_adat['hazai'] if tipp["tovabbjuto"] == 1 else (bracket_adat['vendeg'] if tipp["tovabbjuto"]==2 else "?")
                    sor[f"{j} tipp"] = f"{tipp['h']}-{tipp['v']} (Tov: {t_t_nev})"
                    sor[f"{j} pont"] = pont
                else:
                    sor[f"{j} tipp"] = "-"
                    sor[f"{j} pont"] = 0
            ko_tablazat.append(sor)
        st.dataframe(pd.DataFrame(ko_tablazat), use_container_width=True, hide_index=True)

# --- 2. MENÜPONT: TIPPEK LEADÁSA ---
elif menu == "Tippek leadása":
    st.header(" Tippek rögzítése")
    valasztott_jatekos = st.selectbox("Melyik Fars Fc tag vagy:", jatekosok)
    
    tab1, tab2 = st.tabs([" Csoportkör", " Egyenes Kieséses Szakasz"])
    
    with tab1:
        aktiv_meccsek = {m_id: m_adat for m_id, m_adat in data["meccsek"].items() if m_adat["valos_hazai"] is None}
        if not aktiv_meccsek:
            st.success("Jelenleg nincs tippelhető csoportmeccs.")
        else:
            if st.button("Csoportkör Tippek mentése ", type="primary"):
                if valasztott_jatekos not in data["tippek"]: data["tippek"][valasztott_jatekos] = {}
                for m_id in aktiv_meccsek.keys():
                    h_ertek = st.session_state.get(f"t_h_{valasztott_jatekos}_{m_id}", 0)
                    v_ertek = st.session_state.get(f"t_v_{valasztott_jatekos}_{m_id}", 0)
                    data["tippek"][valasztott_jatekos][m_id] = [h_ertek, v_ertek]
                save_data(data)
                st.success("A csoportkörös tippjeidet elmentettem!")
                st.rerun()

            for m_id in aktiv_meccsek.keys():
                st.subheader(m_id)
                korabbi_tipp = data["tippek"].get(valasztott_jatekos, {}).get(m_id, [0, 0])
                col1, col2 = st.columns(2)
                with col1: st.number_input(f"Hazai tipp", min_value=0, max_value=20, value=int(korabbi_tipp[0]), key=f"t_h_{valasztott_jatekos}_{m_id}")
                with col2: st.number_input(f"Vendég tipp", min_value=0, max_value=20, value=int(korabbi_tipp[1]), key=f"t_v_{valasztott_jatekos}_{m_id}")

    with tab2:
        ko_aktiv = {m_id: m_adat for m_id, m_adat in aktualis_bracket.items() 
                    if m_adat["hazai"] != "TBD" and m_adat["vendeg"] != "TBD" and m_id not in data.get("ko_eredmenyek", {})}
        
        if not ko_aktiv:
            st.success("Jelenleg nincs tippelhető kieséses mérkőzés.")
        else:
            st.info(" A kieséses szakaszban +1 pont jár, ha eltalálod a továbbjutó csapatot is!")
            if st.button("Kieséses Tippek mentése ", type="primary"):
                if "ko_tippek" not in data: data["ko_tippek"] = {}
                if valasztott_jatekos not in data["ko_tippek"]: data["ko_tippek"][valasztott_jatekos] = {}
                
                for m_id, b_adat in ko_aktiv.items():
                    h_ertek = st.session_state.get(f"ko_h_{valasztott_jatekos}_{m_id}", 0)
                    v_ertek = st.session_state.get(f"ko_v_{valasztott_jatekos}_{m_id}", 0)
                    tov_val = st.session_state.get(f"ko_tovabb_val_{valasztott_jatekos}_{m_id}", "Válassz...")
                    t_num = 1 if tov_val == b_adat["hazai"] else (2 if tov_val == b_adat["vendeg"] else 0)
                    data["ko_tippek"][valasztott_jatekos][m_id] = {"h": h_ertek, "v": v_ertek, "tovabbjuto": t_num}
                save_data(data)
                st.success("Kieséses szakasz tippjei elmentve!")
                st.rerun()

            for m_id, m_adat in ko_aktiv.items():
                st.subheader(f"{m_adat['nev']}: {m_adat['hazai']} - {m_adat['vendeg']}")
                elozo = data.get("ko_tippek", {}).get(valasztott_jatekos, {}).get(m_id, {"h":0, "v":0, "tovabbjuto":0})
                opciok = ["Válassz...", m_adat["hazai"], m_adat["vendeg"]]
                def_idx = elozo["tovabbjuto"] if elozo["tovabbjuto"] in [1, 2] else 0
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1: st.number_input(f"Hazai Gól", min_value=0, max_value=20, value=int(elozo["h"]), key=f"ko_h_{valasztott_jatekos}_{m_id}")
                with col2: st.number_input(f"Vendég Gól", min_value=0, max_value=20, value=int(elozo["v"]), key=f"ko_v_{valasztott_jatekos}_{m_id}")
                with col3: st.selectbox(f"Ki jut tovább?", opciok, index=def_idx, key=f"ko_tovabb_val_{valasztott_jatekos}_{m_id}")
                st.write("---")

# --- 3. MENÜPONT: ADMIN PANEL ---
elif menu == "Admin Panel":
    st.header(" Adminisztrációs felület")
    
    tab1, tab2 = st.tabs(["Csoportkör Eredmények", " Egyenes Kiesés Eredmények"])
    
    with tab1:
        st.subheader("Csoportkör Meccsek lezárása")
        for m_id, m_adat in data["meccsek"].items():
            alap_h = 0 if m_adat["valos_hazai"] is None else m_adat["valos_hazai"]
            alap_v = 0 if m_adat["valos_vendeg"] is None else m_adat["valos_vendeg"]
            is_checked = m_adat["valos_hazai"] is not None
            
            lejatszott = st.checkbox(f"Lejátszva: {m_id}", value=is_checked, key=f"admin_ch_{m_id}")
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: h_g = st.number_input("Hazai gól", min_value=0, max_value=20, value=int(alap_h), key=f"admin_h_{m_id}", disabled=not lejatszott)
            with col2: v_g = st.number_input("Vendég gól", min_value=0, max_value=20, value=int(alap_v), key=f"admin_v_{m_id}", disabled=not lejatszott)
            with col3:
                st.write("")
                if st.button("Mentés", key=f"btn_{m_id}"):
                    if lejatszott:
                        data["meccsek"][m_id]["valos_hazai"] = h_g
                        data["meccsek"][m_id]["valos_vendeg"] = v_g
                    else:
                        data["meccsek"][m_id]["valos_hazai"] = None
                        data["meccsek"][m_id]["valos_vendeg"] = None
                    save_data(data)
                    st.success("Eredmény mentve.")
                    st.rerun()
            st.write("---")

    with tab2:
        st.subheader("Kieséses Szakasz Meccsek lezárása")
        for m_id, m_adat in aktualis_bracket.items():
            if m_adat["hazai"] != "TBD" and m_adat["vendeg"] != "TBD":
                st.write(f"**{m_adat['nev']}: {m_adat['hazai']} - {m_adat['vendeg']}**")
                eredmeny_adat = data.get("ko_eredmenyek", {}).get(m_id, {})
                is_checked = bool(eredmeny_adat)
                
                alap_h = eredmeny_adat.get("v_h", 0)
                alap_v = eredmeny_adat.get("v_v", 0)
                alap_tovabb = eredmeny_adat.get("tovabbjuto", 0)
                
                opciok = ["Válassz...", m_adat["hazai"], m_adat["vendeg"]]
                def_idx = alap_tovabb if alap_tovabb in [1, 2] else 0
                
                lejatszott = st.checkbox(f"Lezárva", value=is_checked, key=f"ko_admin_ch_{m_id}")
                col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
                
                with col1: h_g = st.number_input("H gól", min_value=0, max_value=20, value=int(alap_h), key=f"ko_admin_h_{m_id}", disabled=not lejatszott)
                with col2: v_g = st.number_input("V gól", min_value=0, max_value=20, value=int(alap_v), key=f"ko_admin_v_{m_id}", disabled=not lejatszott)
                with col3: valasztas = st.selectbox("Továbbjutott:", opciok, index=def_idx, key=f"ko_admin_tovabb_{m_id}", disabled=not lejatszott)
                with col4:
                    st.write("")
                    if st.button("Mentés", key=f"ko_btn_{m_id}"):
                        if lejatszott:
                            if valasztas == "Válassz...":
                                st.error("Kötelező kiválasztani a továbbjutót!")
                            else:
                                t_num = 1 if valasztas == m_adat["hazai"] else 2
                                if "ko_eredmenyek" not in data: data["ko_eredmenyek"] = {}
                                data["ko_eredmenyek"][m_id] = {"v_h": h_g, "v_v": v_g, "tovabbjuto": t_num}
                                save_data(data)
                                st.success("Mentve! A sorsolás frissült.")
                                st.rerun()
                        else:
                            if "ko_eredmenyek" in data and m_id in data["ko_eredmenyek"]:
                                del data["ko_eredmenyek"][m_id]
                                save_data(data)
                                st.success("Eredmény törölve.")
                                st.rerun()
                st.write("---")

    # ==========================================
    # BIZTONSÁGI MENTÉS ÉS VISSZAÁLLÍTÁS
    # ==========================================
    st.header(" Biztonsági mentés (Adatbázis kezelése)")
    col_export, col_import = st.columns(2)
    with col_export:
        st.subheader("Adatok letöltése")
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: json_string = f.read()
            st.download_button(label="⬇️ Adatbázis letöltése (.json)", file_name="tippjatek_adatok_backup.json", mime="application/json", data=json_string, type="primary")
        except: st.warning("Még nincs mentett adat.")
    with col_import:
        st.subheader("Adatok visszaállítása")
        uploaded_file = st.file_uploader("Válassz ki egy korábban letöltött fájlt", type=["json"])
        if uploaded_file is not None:
            if st.button("⚠️ Visszaállítás megerősítése"):
                uj_adat = json.load(uploaded_file)
                save_data(uj_adat)
                st.success("Az adatbázis sikeresen visszaállítva!")
                st.rerun()