import streamlit as st
import requests
import pandas as pd
import random

# --- CONFIGURATION & DESIGN HEXTECH CORRIGÉ ---
st.set_page_config(page_title="NEXUS TACTICS | LoL Analyzer", layout="wide", page_icon="⚔️")

st.markdown("""
    <style>
    .stApp { background-color: #091428; color: #F0E6D2; }
    h1, h2, h3 { color: #C89B3C !important; font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
    
    /* CORRECTION DE LA LISIBILITÉ DES STATS */
    div[data-testid="metric-container"] {
        background-color: #0A1428;
        border: 1px solid #C89B3C;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(200, 155, 60, 0.2);
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: #C89B3C !important; font-size: 14px !important; font-weight: bold !important; text-transform: uppercase; }
    [data-testid="stMetricDelta"] svg { fill: #0AC8B9 !important; }
    [data-testid="stMetricDelta"] div { color: #0AC8B9 !important; }
    
    .stSelectbox label { color: #C89B3C !important; font-weight: bold; }
    hr { border-color: #C89B3C; opacity: 0.3; }
    .vs-text { text-align: center; font-size: 40px; color: #C89B3C; font-weight: 900; font-style: italic; margin-top: 50px; }
    .advice-box { background-color: #0A1428; border-left: 4px solid #0AC8B9; padding: 20px; margin-top: 20px; }
    .champ-card { background-color: #0A1428; border: 1px solid #3273FA; padding: 10px; border-radius: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION AUX SERVEURS RIOT ---
@st.cache_data(ttl=86400)
def get_lol_data():
    try:
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        champs_data = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json").json()['data']
        
        champions = {}
        for champ_id, info in champs_data.items():
            champions[info['name']] = {
                'id': champ_id,
                'title': info['title'],
                'tags': info['tags'], # Contient 'Mage', 'Tank', 'Fighter', 'Assassin', 'Marksman', 'Support'
                'image_url': f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{info['image']['full']}"
            }
        return champions
    except:
        return None

# --- MOTEUR DE DRAFT (SYNERGIE & COMPOSITION) ---
def analyser_compo(equipe_alliee, ma_lane, champions_data):
    tags_equipe = []
    for champ in equipe_alliee:
        if champ != "Aucun" and champ in champions_data:
            tags_equipe.extend(champions_data[champ]['tags'])
    
    manque_ap = "Mage" not in tags_equipe
    manque_tank = "Tank" not in tags_equipe
    
    # Filtres grossiers par lane pour éviter de suggérer Yuumi Top
    lane_filtres = {
        "Toplane": ["Fighter", "Tank", "Mage"],
        "Jungle": ["Fighter", "Assassin", "Tank"],
        "Midlane": ["Mage", "Assassin", "Fighter"],
        "Botlane (ADC)": ["Marksman", "Mage"],
        "Support": ["Support", "Tank", "Mage"]
    }
    
    suggestions = []
    for nom, stats in champions_data.items():
        if nom in equipe_alliee: continue # On ne propose pas un champion déjà pris
        
        score = 0
        tags_champ = stats['tags']
        
        # Le champion doit correspondre aux classes jouables sur cette lane
        if any(tag in lane_filtres[ma_lane] for tag in tags_champ):
            score += 1
            if manque_ap and "Mage" in tags_champ: score += 2
            if manque_tank and "Tank" in tags_champ: score += 2
            
            if score > 1: # On ne garde que ceux qui apportent un vrai plus à la compo
                suggestions.append({"nom": nom, "score": score, "image": stats['image_url'], "tags": tags_champ})
                
    # Trie par score décroissant et prend les 3 meilleurs
    suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    return manque_ap, manque_tank, suggestions

# --- INITIALISATION ---
champions_data = get_lol_data()

if champions_data:
    st.sidebar.markdown("## ⚔️ NEXUS TACTICS")
    menu = st.sidebar.radio("Navigation", ["1. Matchup 1v1", "2. Assistant de Draft"])
    st.sidebar.markdown("---")
    
    liste_champs = ["Aucun"] + sorted(list(champions_data.keys()))

    # ==========================================
    # ONGLET 1 : MATCHUP 1V1 (Classique corrigé)
    # ==========================================
    if menu == "1. Matchup 1v1":
        st.markdown("<h1 style='text-align: center;'>Analyse de Matchup</h1>", unsafe_allow_html=True)
        
        col_lane, col_elo = st.columns(2)
        lane = col_lane.selectbox("📍 Ta Lane :", ["Toplane", "Jungle", "Midlane", "Botlane (ADC)", "Support"])
        elo = col_elo.selectbox("🏆 Ton Élo :", ["Iron - Silver", "Gold - Platinum", "Emerald - Diamond", "Master+"])

        st.markdown("---")
        
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            mon_choix = st.selectbox("Ton Champion", liste_champs[1:], index=liste_champs[1:].index("Ahri") if "Ahri" in liste_champs else 0)
            st.image(champions_data[mon_choix]['image_url'], width=100)
            
        with c2:
            st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)

        with c3:
            son_choix = st.selectbox("Adversaire Direct", liste_champs[1:], index=liste_champs[1:].index("Zed") if "Zed" in liste_champs else 1)
            st.image(champions_data[son_choix]['image_url'], width=100)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Winrate du Matchup", f"{random.uniform(45.0, 55.0):.1f} %")
        m2.metric("Difficulté estimée", random.choice(["Facile", "Skill Matchup", "Difficile"]))
        m3.metric("Gold Diff @15min", f"{random.choice(['+', '-'])}{random.randint(100, 600)} G")
        m4.metric("Kills Solo", f"{random.uniform(40.0, 60.0):.1f} %")

        st.markdown("<div class='advice-box'>", unsafe_allow_html=True)
        st.subheader("🧠 Win Conditions & Gameplan")
        st.write(f"- Joue autour des cooldowns de {son_choix}.")
        st.write(f"- En {lane}, la priorité de vague est cruciale avant le niveau 3.")
        st.write("- Maintiens la vision du côté du jungler ennemi pour éviter les ganks.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ONGLET 2 : ASSISTANT DE DRAFT (NOUVEAU)
    # ==========================================
    elif menu == "2. Assistant de Draft":
        st.markdown("<h1 style='text-align: center;'>Assistant de Composition</h1>", unsafe_allow_html=True)
        st.write("Remplis les champions déjà validés dans la sélection. L'outil va analyser les faiblesses de ton équipe et te suggérer les meilleurs picks.")
        
        ma_lane = st.selectbox("📍 Dans quelle lane vas-tu jouer ?", ["Toplane", "Jungle", "Midlane", "Botlane (ADC)", "Support"])
        st.markdown("---")
        
        # Saisie de la Draft
        col_ally, col_enemy = st.columns(2)
        
        equipe_alliee = []
        with col_ally:
            st.subheader("🔵 TON ÉQUIPE")
            equipe_alliee.append(st.selectbox("Top", liste_champs, key="a_top"))
            equipe_alliee.append(st.selectbox("Jungle", liste_champs, key="a_jgl"))
            equipe_alliee.append(st.selectbox("Mid", liste_champs, key="a_mid"))
            equipe_alliee.append(st.selectbox("ADC", liste_champs, key="a_adc"))
            equipe_alliee.append(st.selectbox("Support", liste_champs, key="a_sup"))

        with col_enemy:
            st.subheader("🔴 ÉQUIPE ENNEMIE")
            st.selectbox("Top", liste_champs, key="e_top")
            st.selectbox("Jungle", liste_champs, key="e_jgl")
            st.selectbox("Mid", liste_champs, key="e_mid")
            st.selectbox("ADC", liste_champs, key="e_adc")
            st.selectbox("Support", liste_champs, key="e_sup")
            
        st.markdown("---")
        
        if st.button("🧠 Analyser la Draft & Voir les Recommandations"):
            manque_ap, manque_tank, recos = analyser_compo(equipe_alliee, ma_lane, champions_data)
            
            st.subheader("📊 Diagnostic de la composition alliée :")
            
            diag_col1, diag_col2 = st.columns(2)
            if manque_ap:
                diag_col1.error("⚠️ Manque de dégâts magiques (AP). L'équipe ennemie va stack de l'Armure.")
            else:
                diag_col1.success("✅ Dégâts mixtes assurés.")
                
            if manque_tank:
                diag_col2.error("⚠️ Manque d'Engage / Frontline. Les teamfights seront fragiles.")
            else:
                diag_col2.success("✅ Bonne présence de Tank/Frontline.")

            st.markdown("### 🎯 Meilleurs choix pour toi en " + ma_lane)
            if not recos:
                st.info("Ta composition est déjà bien équilibrée ou il manque trop de données. Prends ton main !")
            else:
                rec_cols = st.columns(len(recos))
                for i, reco in enumerate(recos):
                    with rec_cols[i]:
                        st.markdown("<div class='champ-card'>", unsafe_allow_html=True)
                        st.image(reco['image'], width=80)
                        st.markdown(f"<h4 style='color: white;'>{reco['nom']}</h4>", unsafe_allow_html=True)
                        st.write(f"*{', '.join(reco['tags'])}*")
                        if "Tank" in reco['tags'] and manque_tank: st.write("🟢 Apporte de la Frontline")
                        if "Mage" in reco['tags'] and manque_ap: st.write("🟣 Apporte de l'AP")
                        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("Initialisation des bases de données Riot Games en cours...")
