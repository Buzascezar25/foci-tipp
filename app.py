import streamlit as st
import pandas as pd
import json
import os

DB_FILE = "tippjatek_adatok.json"

#
   # A hivatalos 2026-os világbajnokság 72 csoportmeccse zászlókkal
ALAP_MECCSEK = [
    # 1. Forduló
    "Mexikó 🇲🇽 - Dél-Afrika 🇿🇦", "Dél-Korea 🇰🇷 - Csehország 🇨🇿",
    "Kanada 🇨🇦 - Bosznia-Hercegovina 🇧🇦","USA 🇺🇸 - Paraguay 🇵🇾", "Katar 🇶🇦 - Svájc 🇨🇭",
    "Brazília 🇧🇷 - Marokkó 🇲🇦", "Haiti 🇭🇹 - Skócia 🏴󠁧󠁢󠁳󠁣󠁴󠁿","Ausztrália 🇦🇺 - Törökország 🇹🇷",
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


def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Ha nincs még mentés, legeneráljuk az alap 72 meccset
    alap_struktura = {"meccsek": {}, "tippek": {}}
    for meccs in ALAP_MECCSEK:
        alap_struktura["meccsek"][meccs] = {"valos_hazai": None, "valos_vendeg": None}
    
    # El is mentjük azonnal, hogy meglegyen a fájl
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(alap_struktura, f, ensure_ascii=False, indent=4)
        
    return alap_struktura

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()
jatekosok = ["Péter", "Barna", "Boldi", "Dana", "Szaba"]

def pont_szamit(valos_h, valos_v, tipp_h, tipp_v):
    if valos_h is None or valos_v is None or tipp_h is None or tipp_v is None:
        return 0
    if valos_h == tipp_h and valos_v == tipp_v:
        return 3
    valos_kim = 1 if valos_h > valos_v else (2 if valos_h < valos_v else 0)
    tipp_kim = 1 if tipp_h > tipp_v else (2 if tipp_h < tipp_v else 0)
    if valos_kim == tipp_kim:
        return 1
    return 0

st.set_page_config(page_title="Tippelde", layout="wide")
st.title("Tippelde Fars Fcnek <3")

menu = st.sidebar.radio("Navigáció", ["Ranglista és Meccsek", "Tippek leadása", "Admin Panel"])

# 1. RANGLISTA ÉS MECCSEK MEGJELENÍTÉSE
if menu == "Ranglista és Meccsek":
    st.header("Aktuális Állás")
    
    if not data["meccsek"]:
        st.info("Nincsenek meccsek a rendszerben.")
    else:
        osszes_pont = {j: 0 for j in jatekosok}
        meccs_tablazat = []
        
        for m_id, m_adat in data["meccsek"].items():
            v_h, v_v = m_adat["valos_hazai"], m_adat["valos_vendeg"]
            eredmeny_szoveg = f"{v_h}-{v_v}" if v_h is not None else "Még nincs végeredmény"
            
            sor = {"Meccs": m_id, "Végeredmény": eredmeny_szoveg}
            
            for j in jatekosok:
                tipp = data["tippek"].get(j, {}).get(m_id, None)
                if tipp:
                    pont = pont_szamit(v_h, v_v, tipp[0], tipp[1])
                    osszes_pont[j] += pont
                    sor[f"{j} tipp"] = f"{tipp[0]}-{tipp[1]}"
                    sor[f"{j} pont"] = pont
                else:
                    sor[f"{j} tipp"] = "-"
                    sor[f"{j} pont"] = 0
            
            meccs_tablazat.append(sor)
            
        ranglista_df = pd.DataFrame(list(osszes_pont.items()), columns=["Játékos", "Összes pont"]).sort_values(by="Összes pont", ascending=False)
        st.dataframe(ranglista_df, use_container_width=True, hide_index=True)
        
        st.header("Meccsek részletesen")
        st.dataframe(pd.DataFrame(meccs_tablazat), use_container_width=True, hide_index=True)

# 2. TIPPEK LEADÁSA (GOMB A TETEJÉN - JAVÍTOTT, JÁTÉKOSONKÉNTI MEZŐKKEL)
elif menu == "Tippek leadása":
    st.header("Tippek rögzítése")
    
    valasztott_jatekos = st.selectbox("Melyi Fars Fc tag vagy?", jatekosok)
    aktiv_meccsek = {m_id: m_adat for m_id, m_adat in data["meccsek"].items() if m_adat["valos_hazai"] is None}
    
    if not aktiv_meccsek:
        st.success("Jelenleg nincs tippelhető meccs (minden meccs lezárult).")
    else:
        st.write(f"Szia Mr Fars {valasztott_jatekos}! Itt adhatod le a tippjeidet a még le nem játszott meccsekre:")
        
        # MENTÉS GOMB A TETEJÉN
        if st.button("Tippek mentése", type="primary"):
            if valasztott_jatekos not in data["tippek"]:
                data["tippek"][valasztott_jatekos] = {}
            
            # Most már a játékos-specifikus session_state kulcsokból olvassuk ki az adatot
            for m_id in aktiv_meccsek.keys():
                h_ertek = st.session_state.get(f"t_h_{valasztott_jatekos}_{m_id}", 0)
                v_ertek = st.session_state.get(f"t_v_{valasztott_jatekos}_{m_id}", 0)
                data["tippek"][valasztott_jatekos][m_id] = [h_ertek, v_ertek]
            
            save_data(data)
            st.success("A tippjeidet elmentettem.")
            st.rerun()

        st.write("---")

        for m_id in aktiv_meccsek.keys():
            st.subheader(m_id)
            korabbi_tipp = data["tippek"].get(valasztott_jatekos, {}).get(m_id, [0, 0])
            
            col1, col2 = st.columns(2)
            with col1:
                # A 'key' most már tartalmazza a játékos nevét is!
                st.number_input(
                    f"Hazai tipp", 
                    min_value=0, 
                    max_value=20, 
                    value=int(korabbi_tipp[0]), 
                    key=f"t_h_{valasztott_jatekos}_{m_id}"
                )
            with col2:
                st.number_input(
                    f"Vendég tipp", 
                    min_value=0, 
                    max_value=20, 
                    value=int(korabbi_tipp[1]), 
                    key=f"t_v_{valasztott_jatekos}_{m_id}"
                )

# 3. ADMIN PANEL
elif menu == "Admin Panel":
    st.header("Adminisztrációs felület")
    
    st.subheader("Új meccs hozzáadása")
    col1, col2 = st.columns(2)
    with col1:
        hazai_csapat = st.text_input("Hazai csapat neve:", placeholder="Pl: Brazília")
    with col2:
        vendeg_csapat = st.text_input("Vendég csapat neve:", placeholder="Pl: Marokkó")
        
    if st.button("Meccs létrehozása"):
        if hazai_csapat and vendeg_csapat:
            meccs_kulcs = f"{hazai_csapat} - {vendeg_csapat}"
            if meccs_kulcs not in data["meccsek"]:
                data["meccsek"][meccs_kulcs] = {"valos_hazai": None, "valos_vendeg": None}
                save_data(data)
                st.success(f"Meccs hozzáadva: {meccs_kulcs}")
                st.rerun()
            else:
                st.warning("Ez a meccs már létezik.")
        else:
            st.error("Kérlek add meg mindkét csapat nevét.")
            
    st.write("---")
    
    st.subheader("Eredmények beírása / Meccsek lezárása")
    if not data["meccsek"]:
        st.write("Nincsenek meccsek.")
    else:
        for m_id, m_adat in data["meccsek"].items():
            st.write(f"**{m_id}**")
            
            alap_h = 0 if m_adat["valos_hazai"] is None else m_adat["valos_hazai"]
            alap_v = 0 if m_adat["valos_vendeg"] is None else m_adat["valos_vendeg"]
            is_checked = m_adat["valos_hazai"] is not None
            
            lejatszott = st.checkbox("Lejátszva / Lezárva", value=is_checked, key=f"admin_ch_{m_id}")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                h_gól = st.number_input("Hazai gól", min_value=0, max_value=20, value=int(alap_h), key=f"admin_h_{m_id}", disabled=not lejatszott)
            with col2:
                v_gól = st.number_input("Vendég gól", min_value=0, max_value=20, value=int(alap_v), key=f"admin_v_{m_id}", disabled=not lejatszott)
            with col3:
                st.write("")
                if st.button("Mentés", key=f"btn_{m_id}"):
                    if lejatszott:
                        data["meccsek"][m_id]["valos_hazai"] = h_gól
                        data["meccsek"][m_id]["valos_vendeg"] = v_gól
                    else:
                        data["meccsek"][m_id]["valos_hazai"] = None
                        data["meccsek"][m_id]["valos_vendeg"] = None
                    save_data(data)
                    st.success("Eredmény mentve.")
                    st.rerun()
            st.write("---")

    # ==========================================
    # BIZTONSÁGI MENTÉS ÉS VISSZAÁLLÍTÁS
    # ==========================================
    st.header(" Biztonsági mentés ")
    
    col_export, col_import = st.columns(2)
    
    # LETÖLTÉS (EXPORT)
    with col_export:
        st.subheader("Adatok letöltése")
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                json_string = f.read()
            
            st.download_button(
                label=" Adatbázis letöltése (.json)",
                file_name="tippjatek_adatok_backup.json",
                mime="application/json",
                data=json_string,
                type="primary"
            )
        except Exception as e:
            st.warning("Még nincs mentett adat.")

    # FELTÖLTÉS (IMPORT)
    with col_import:
        st.subheader("Adatok visszaállítása")
        uploaded_file = st.file_uploader("Válassz ki egy korábban letöltött fájlt", type=["json"])
        
        if uploaded_file is not None:
            if st.button(" Visszaállítás megerősítése"):
                try:
                    uj_adat = json.load(uploaded_file)
                    save_data(uj_adat)
                    st.success("Az adatbázis sikeresen visszaállítva!")
                    st.rerun()
                except Exception as e:
                    st.error("Hiba történt a fájl beolvasásakor. Biztos, hogy a jó fájlt töltötted fel?")