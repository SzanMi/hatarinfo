import streamlit as st
import googlemaps
import os
from datetime import datetime
import pytz

# Google Maps kliens indítása a felhő biztonságos tárolójából
gmaps = googlemaps.Client(key=os.environ.get("MY_GOOGLE_KEY", ""))

# A te általad beküldött koordináták tűpontos tizedes változatai mindkét irányra
hataradatok = {
    "Röszke (Autópálya)": {
        "nonstop": True,
        "KILÉPŐ": {"A": (46.19631, 19.95750), "B": (46.17189, 19.97414)},
        "BELÉPŐ": {"A": (46.15389, 19.93769), "B": (46.18589, 19.99111)}
    },
    "Röszke (Közúti)": {
        "nonstop": True,
        "KILÉPŐ": {"A": (46.18825, 19.99503), "B": (46.17539, 19.98386)},
        "BELÉPŐ": {"A": (46.15981, 19.96564), "B": (46.18494, 19.99194)}
    },
    "Tompa": {
        "nonstop": True,
        "KILÉPŐ": {"A": (46.20114, 19.52486), "B": (46.16397, 19.56292)},
        "BELÉPŐ": {"A": (46.08114, 19.60667), "B": (46.18169, 19.54767)}
    },
    "Ásotthalom": {
        "nonstop": True,
        "KILÉPŐ": {"A": (46.16128, 19.81694), "B": (46.14144, 19.84653)},
        "BELÉPŐ": {"A": (46.12997, 19.85592), "B": (46.14706, 19.83800)}
    },
    "Bácsalmás": {
        "nonstop": False,
        "KILÉPŐ": {"A": (46.06353, 19.38200), "B": (46.03381, 19.38136)},
        "BELÉPŐ": {"A": (45.99767, 19.39931), "B": (46.05036, 19.38142)}
    },
    "Bácsszentgyörgy": {
        "nonstop": False,
        "KILÉPŐ": {"A": (45.97758, 19.04997), "B": (45.96531, 19.05467)},
        "BELÉPŐ": {"A": (45.94972, 19.05678), "B": (45.97178, 19.05225)}
    },
    "Hercegszántó": {
        "nonstop": True,
        "KILÉPŐ": {"A": (45.94381, 18.94519), "B": (45.92939, 18.93472)},
        "BELÉPŐ": {"A": (45.90961, 18.93522), "B": (45.93753, 18.94242)}
    },
    "Kübekháza": {
        "nonstop": False,
        "KILÉPŐ": {"A": (46.14308, 20.28000), "B": (46.12589, 20.26372)},
        "BELÉPŐ": {"A": (46.09564, 20.25744), "B": (46.13514, 20.27106)}
    },
    "Tiszasziget": {
        "nonstop": False,
        "KILÉPŐ": {"A": (46.17189, 20.14608), "B": (46.15678, 20.11267)},
        "BELÉPŐ": {"A": (46.13128, 20.09339), "B": (46.16189, 20.12419)}
    }
}

st.set_page_config(page_title="HatárInfó PRO", page_icon="🚗", layout="centered")

st.title("🚗 Élő Sáv- és Zónabiztos Határinfó")
st.write("Valós idejű várakozási idők automatikus nyitvatartás-ellenőrzéssel.")

irany = st.radio(
    "Válassz útirányt:",
    ("Magyarország ➔ Szerbia (Kilépő)", "Szerbia ➔ Magyarország (Belépő)"),
    horizontal=True
)

if st.button("🔄 Adatok frissítése", type="primary", use_container_width=True):
    st.rerun()

helyi_idozona = pytz.timezone("Europe/Budapest")
most = datetime.now(helyi_idozona)
aktualis_ido = most.strftime("%H:%M:%S")
jelenlegi_ora = most.hour

st.caption(f"⏱️ Legutóbbi frissítés: **{aktualis_ido}**")
st.subheader("Aktuális várakozási idők:")

nyitva_van_a_kishatar = not (jelenlegi_ora >= 19 or jelenlegi_ora < 7)

for nev, info in hataradatok.items():
    kijelzendo_nev = nev if info["nonstop"] else f"⏱️ {nev} (07-19h)"
    
    if not info["nonstop"] and not nyitva_van_a_kishatar:
        st.info(f"**{kijelzendo_nev}**: 🔒 ZÁRVA (Este 19:00 és reggel 07:00 között zárva tart)")
        continue

    try:
        valasztott_irany = "BELÉPŐ" if "Szerbia ➔ Magyarország" in irany else "KILÉPŐ"
        pontok = info[valasztott_irany]

        matrix = gmaps.distance_matrix(
            origins=[pontok["A"]], destinations=[pontok["B"]],
            mode="driving", departure_time="now", traffic_model="best_guess"
        )
        
        # JAVÍTÁS: Listák pontos kibontása az [0] indexekkel
        element = matrix['rows'][0]['elements'][0]
        
        if element['status'] == 'OK':
            duration_normal = element['duration']['value']
            duration_traffic = element['duration_in_traffic']['value']
            keses_perc = max(0, round((duration_traffic - duration_normal) / 60))
            
            if keses_perc <= 15:
                st.success(f"**{kijelzendo_nev}**: {keses_perc} perc (🟢 Sima ügy)")
            elif keses_perc <= 45:
                st.warning(f"**{kijelzendo_nev}**: {keses_perc} perc (🟡 Lassú haladás)")
            else:
                st.error(f"**{kijelzendo_nev}**: {keses_perc} perc (🔴 Erős torlódás)")
        else:
            st.info(f"**{kijelzendo_nev}**: Az út jelenleg zárva van vagy nem tervezhető.")
    except Exception as e:
        st.info(f"**{kijelzendo_nev}**: Sikertelen lekérdezés.")
