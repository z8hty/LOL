import streamlit as st
import requests
import pandas as pd
import random

# --- CONFIGURATION & DESIGN HEXTECH ---
st.set_page_config(page_title="NEXUS TACTICS | LoL Matchup Analyzer", layout="wide", page_icon="⚔️")

st.markdown("""
    <style>
    .stApp { background-color: #091428; color: #F0E6D2; }
    h1, h2, h3 { color: #C89B3C !important; font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
    div[data-testid="metric-container"] {
        background-color: #0A1428;
        border: 1px solid #C89B3C;
        padding: 15px;
        border-radius: 2px;
        box-shadow: 0 0 10px rgba(200, 155, 60, 0.2);
    }
    .stSelectbox label { color: #C89B3C !important; font-weight: bold; }
    hr { border-color: #C89B3C; opacity: 0.3; }
    .vs-text { text-align: center; font-size: 40px; color: #C89B3C; font-weight: 900; font-style: italic; margin-top: 50px; }
    .advice-box { background-color: #0A1428; border-left: 4px solid #0AC8B9; padding: 20px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION AUX SERVEURS RIOT (DATA DRAGON) ---
@st.cache_data(ttl=86400) # Mise en cache 24h pour que l'app soit ultra rapide
def get_lol_data():
    try:
        # 1. Récupérer la dernière version du jeu (ex: 14.5.1)
        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        version = requests.get(version_url).json()[0]
        
        # 2. Récupérer la liste des champions en Français
        champs_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json"
        champs_data = requests.get(champs_url).json()['data']
        
        # Créer un dictionnaire pour faciliter l'affichage
        champions = {}
        for champ_id, info in champs_data.items():
            champions[info['name']] = {
                'id': champ_id,
                'title': info['title'],
                'tags': info['tags'],
                'image_url': f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{info['image']['full']}"
            }
        return champions
    except Exception as e:
        st.error("Erreur de connexion aux serveurs Riot Games.")
        return None

# --- GÉNÉRATEUR DE CONSEILS (Moteur de logique MVP) ---
def generer_analyse_matchup(mon_champ, son_champ, lane):
    # C'est ici que tu brancheras l'IA ou ton propre algo plus tard
    avantages = [
        f"Garde tes sorts de contrôle pour interrompre l'engage de {son_champ}.",
        f"Push la vague en {lane} avant le niveau 3, {mon_champ} a un meilleur clear.",
        f"Attention au trade niveau 6, l'ultimate de {son_champ} est très punitif.",
        f"Joue autour de la vision. Si le jungler n'est pas vu, freeze la lane.",
        f"Prends de l'anti-heal (Hémorragie) dès ton premier back contre ce champion."
    ]
    
    difficulte = random.choice(["Facile (Avantage)", "Skill Matchup (50/50)", "Difficile (Counter)"])
    if difficulte == "Difficile (Counter)": color = "#FF4B4B"
    elif difficulte == "Facile (Avantage)": color = "#00FF00"
    else: color = "#F0E6D2"
    
    return random.sample(avantages, 3), difficulte, color

# --- INTERFACE UTILISATEUR ---
champions_data = get_lol_data()

if champions_data:
    st.markdown("<h1 style='text-align: center;'>⚔️ NEXUS TACTICS ⚔️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #0AC8B9; font-size: 18px;'>L'outil d'analyse stratégique pour dominer la Faille de l'Invocateur</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. PARAMÉTRAGE DE LA GAME
    col_lane, col_elo = st.columns(2)
    lane = col_lane.selectbox("📍 Sélectionne ta Lane :", ["Toplane", "Jungle", "Midlane", "Botlane (ADC)", "Support"])
    elo = col_elo.selectbox("🏆 Sélectionne ton Élo (pour ajuster les stats) :", ["Iron - Silver", "Gold - Platinum", "Emerald - Diamond", "Master+"])

    st.markdown("---")

    # 2. SÉLECTION DU MATCHUP
    noms_champions = sorted(list(champions_data.keys()))
    
    c1, c2, c3 = st.columns([2, 1, 2])
    
    with c1:
        st.subheader("🔵 TON CHAMPION")
        mon_choix = st.selectbox("Qui joues-tu ?", noms_champions, index=noms_champions.index("Ahri") if "Ahri" in noms_champions else 0)
        mon_info = champions_data[mon_choix]
        
        # Affichage Portrait + Titre
        st.image(mon_info['image_url'], width=120)
        st.markdown(f"<h3 style='margin-top: 0px;'>{mon_choix}</h3>", unsafe_allow_html=True)
        st.write(f"*{mon_info['title'].capitalize()}*")
        st.write(f"**Classe :** {', '.join(mon_info['tags'])}")

    with c2:
        st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)

    with c3:
        st.subheader("🔴 ADVERSAIRE DIRECT")
        son_choix = st.selectbox("Qui affrontez-tu ?", noms_champions, index=noms_champions.index("Zed") if "Zed" in noms_champions else 1)
        son_info = champions_data[son_choix]
        
        # Affichage Portrait + Titre
        st.image(son_info['image_url'], width=120)
        st.markdown(f"<h3 style='margin-top: 0px;'>{son_choix}</h3>", unsafe_allow_html=True)
        st.write(f"*{son_info['title'].capitalize()}*")
        st.write(f"**Classe :** {', '.join(son_info['tags'])}")

    # 3. ANALYSE ET CONSEILS
    st.markdown("---")
    st.header(f"📊 Analyse du Matchup : {mon_choix} vs {son_choix}")
    
    conseils, difficulte, diff_color = generer_analyse_matchup(mon_choix, son_choix, lane)
    
    # Métriques factices pour le visuel MVP
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Winrate du Matchup", f"{random.uniform(45.0, 55.0):.1f} %")
    m2.metric("Difficulté estimée", difficulte)
    m3.metric("Gold Diff @15min", f"{random.choice(['+', '-'])}{random.randint(100, 600)} G")
    m4.metric("Kills Solo", f"{random.uniform(40.0, 60.0):.1f} % pour {mon_choix}")

    st.markdown("<div class='advice-box'>", unsafe_allow_html=True)
    st.subheader("🧠 Win Conditions & Gameplan")
    for conseil in conseils:
        st.markdown(f"- {conseil}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><p style='text-align: center; color: #888;'><em>Données brutes issues de Riot Games Data Dragon. L'intégration de l'API de stats en direct sera ajoutée prochainement.</em></p>", unsafe_allow_html=True)

else:
    st.warning("Chargement des données en cours...")
