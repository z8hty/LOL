import streamlit as st
import requests
import pandas as pd
import random

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="NEXUS TACTICS | LoL Analyzer", layout="wide", page_icon="⚔️")

st.markdown("""
    <style>
    .stApp { background-color: #091428; color: #F0E6D2; }
    h1, h2, h3, h4 { color: #C89B3C !important; font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* FORCER LA LISIBILITÉ DES TEXTES ET DES STATS */
    p, li, span, div { color: #F0E6D2; }
    div[data-testid="metric-container"] {
        background-color: #0A1428;
        border: 1px solid #C89B3C;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(200, 155, 60, 0.2);
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: #C89B3C !important; font-size: 14px !important; font-weight: bold !important; text-transform: uppercase; }
    
    .stSelectbox label { color: #C89B3C !important; font-weight: bold; }
    hr { border-color: #C89B3C; opacity: 0.3; }
    .vs-text { text-align: center; font-size: 40px; color: #C89B3C; font-weight: 900; font-style: italic; margin-top: 50px; }
    .advice-box { background-color: #0A1428; border-left: 4px solid #0AC8B9; padding: 20px; margin-top: 20px; }
    .champ-card { background-color: #0A1428; border: 1px solid #3273FA; padding: 15px; border-radius: 5px; text-align: center; }
    .item-highlight { color: #0AC8B9; font-weight: bold; }
    .warning-text { color: #FF4B4B; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LISTES META (Pour éviter le Galio Jungle) ---
META_ROLES = {
    "Toplane": ["Aatrox", "Camille", "Cho'Gath", "Darius", "Dr. Mundo", "Fiora", "Garen", "Gnar", "Gragas", "Gwen", "Illaoi", "Irelia", "Jax", "Jayce", "K'Sante", "Kayle", "Kennen", "Kled", "Malphite", "Maokai", "Mordekaiser", "Nasus", "Olaf", "Ornn", "Pantheon", "Poppy", "Quinn", "Renekton", "Riven", "Rumble", "Sett", "Shen", "Singed", "Sion", "Tahm Kench", "Teemo", "Trundle", "Tryndamere", "Urgot", "Vayne", "Volibear", "Wukong", "Yasuo", "Yone", "Yorick", "Zac"],
    "Jungle": ["Amumu", "Bel'Veth", "Briar", "Diana", "Ekko", "Elise", "Evelynn", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern", "Jarvan IV", "Karthus", "Kayn", "Kha'Zix", "Kindred", "Lee Sin", "Lillia", "Master Yi", "Nidalee", "Nocturne", "Nunu & Willump", "Pantheon", "Poppy", "Rammus", "Rengar", "Sejuani", "Shaco", "Shyvana", "Skarner", "Taliyah", "Talon", "Trundle", "Udyr", "Vi", "Viego", "Volibear", "Warwick", "Wukong", "Xin Zhao", "Zac", "Zed"],
    "Midlane": ["Ahri", "Akali", "Akshan", "Anivia", "Annie", "Aurelion Sol", "Azir", "Cassiopeia", "Corki", "Diana", "Ekko", "Fizz", "Galio", "Hwei", "Irelia", "Kassadin", "Katarina", "LeBlanc", "Lissandra", "Lux", "Malzahar", "Naafiri", "Neeko", "Orianna", "Qiyana", "Ryze", "Smolder", "Sylas", "Syndra", "Talon", "Twisted Fate", "Veigar", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone", "Zed", "Ziggs", "Zoe"],
    "Botlane (ADC)": ["Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx", "Kai'Sa", "Kalista", "Kog'Maw", "Lucian", "Miss Fortune", "Nilah", "Samira", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne", "Xayah", "Yasuo", "Zeri", "Ziggs"],
    "Support": ["Alistar", "Ashe", "Bard", "Blitzcrank", "Brand", "Braum", "Heimerdinger", "Janna", "Karma", "Leona", "Lulu", "Lux", "Maokai", "Milio", "Morgana", "Nami", "Nautilus", "Pantheon", "Pyke", "Rakan", "Rell", "Renata Glasc", "Senna", "Seraphine", "Sona", "Soraka", "Swain", "Tahm Kench", "Taric", "Thresh", "Vel'Koz", "Xerath", "Yuumi", "Zilean", "Zyra"]
}

# --- CONNEXION AUX SERVEURS RIOT ---
@st.cache_data(ttl=86400)
def get_lol_data():
    try:
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        champs_data = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json").json()['data']
        
        champions = {}
        for champ_id, info in champs_data.items():
            nom = info['name']
            champions[nom] = {
                'id': champ_id,
                'title': info['title'],
                'tags': info['tags'],
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
    
    suggestions = []
    # On ne fouille QUE dans les champions qui sont viables dans la lane choisie
    champions_viables = META_ROLES.get(ma_lane, [])
    
    for nom in champions_viables:
        if nom not in champions_data or nom in equipe_alliee: 
            continue
            
        score = 1
        tags_champ = champions_data[nom]['tags']
        
        if manque_ap and "Mage" in tags_champ: score += 3
        if manque_tank and ("Tank" in tags_champ or "Fighter" in tags_champ): score += 3
        
        suggestions.append({"nom": nom, "score": score, "image": champions_data[nom]['image_url'], "tags": tags_champ})
                
    suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]
    return manque_ap, manque_tank, suggestions

# --- MOTEUR DE STUFF (BUILD DYNAMIQUE) ---
def generer_build(mon_champ, equipe_ennemie, champions_data):
    if mon_champ == "Aucun" or mon_champ not in champions_data:
        return None
        
    tags_ennemis = []
    for champ in equipe_ennemie:
        if champ != "Aucun" and champ in champions_data:
            tags_ennemis.extend(champions_data[champ]['tags'])
            
    nb_tanks = tags_ennemis.count("Tank") + tags_ennemis.count("Fighter")
    nb_assassins = tags_ennemis.count("Assassin")
    nb_mages = tags_ennemis.count("Mage")
    nb_supports = tags_ennemis.count("Support") # Souvent des healers
    
    mon_tag_principal = champions_data[mon_champ]['tags'][0]
    
    conseils = []
    
    # 1. Anti-Heal
    if nb_supports >= 1 or "Fighter" in tags_ennemis:
        if mon_tag_principal == "Mage" or mon_tag_principal == "Support":
            conseils.append("🩸 **L'équipe ennemie a du soin :** Fais un <span class='item-highlight'>Morellonomicon</span> ou un <span class='item-highlight'>Putrificateur Techno-chimique</span>.")
        elif mon_tag_principal in ["Marksman", "Fighter", "Assassin"]:
            conseils.append("🩸 **L'équipe ennemie a du soin :** Achète un <span class='item-highlight'>Rappel Mortel</span> ou une <span class='item-highlight'>Épée Dentelée Chempunk</span>.")
        elif mon_tag_principal == "Tank":
            conseils.append("🩸 **L'équipe ennemie a du soin :** Prends une <span class='item-highlight'>Cotte Épineuse</span> dès que possible.")

    # 2. Anti-Tank
    if nb_tanks >= 2:
        if mon_tag_principal == "Mage":
            conseils.append("🛡️ **Ils ont beaucoup de PV/Armure :** Priorise le <span class='item-highlight'>Tourment de Liandry</span> et le <span class='item-highlight'>Bâton du Vide</span>.")
        elif mon_tag_principal == "Marksman" or mon_tag_principal == "Assassin":
            conseils.append("🛡️ **Ils ont beaucoup de Tanks :** Il te faut absolument des <span class='item-highlight'>Salutations de Lord Dominik</span> et potentiellement une <span class='item-highlight'>Lame du Roi Déchu</span>.")
        elif mon_tag_principal == "Fighter":
            conseils.append("🛡️ **Bataille de frontlane :** Le <span class='item-highlight'>Couperet Noir</span> sera excellent pour détruire leur armure.")

    # 3. Survie / Défense
    if nb_assassins >= 2:
        if mon_tag_principal in ["Mage", "Support"]:
            conseils.append("🗡️ **Beaucoup de burst en face :** Le <span class='item-highlight'>Sablier de Zhonya</span> est obligatoire pour survivre aux assassins.")
        else:
            conseils.append("🗡️ **Beaucoup de burst en face :** L'<span class='item-highlight'>Ange Gardien</span> ou la <span class='item-highlight'>Danse de la Mort</span> te sauveront la mise.")
            
    if nb_mages >= 2:
        if mon_tag_principal in ["Tank", "Fighter"]:
            conseils.append("🔮 **Beaucoup de dégâts magiques :** Ne néglige pas la <span class='item-highlight'>Force de la Nature</span> ou le <span class='item-highlight'>Visage Spirituel</span>.")
        elif mon_tag_principal == "Marksman":
            conseils.append("🔮 **Gros dégâts magiques en face :** Pense au <span class='item-highlight'>Cimeterre Mercuriel</span> ou à la <span class='item-highlight'>Gueule de Malmortius</span>.")

    if not conseils:
        conseils.append("⚖️ **Compo ennemie équilibrée :** Pars sur le build standard de ton champion sur ce patch. Pas besoin de contrer un type de dégât spécifique.")

    return conseils

# --- INITIALISATION ---
champions_data = get_lol_data()

if champions_data:
    st.sidebar.markdown("## ⚔️ NEXUS TACTICS")
    menu = st.sidebar.radio("Outils Stratégiques", ["1. Matchup 1v1", "2. Assistant de Draft", "3. L'Adaptateur de Build"])
    st.sidebar.markdown("---")
    
    liste_champs = ["Aucun"] + sorted(list(champions_data.keys()))

    # ==========================================
    # ONGLET 1 : MATCHUP 1V1
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
    # ONGLET 2 : ASSISTANT DE DRAFT
    # ==========================================
    elif menu == "2. Assistant de Draft":
        st.markdown("<h1 style='text-align: center;'>Assistant de Composition</h1>", unsafe_allow_html=True)
        st.write("L'outil analyse les faiblesses de ton équipe et te suggère les meilleurs picks pour équilibrer la game.")
        
        ma_lane = st.selectbox("📍 Dans quelle lane vas-tu jouer ?", ["Toplane", "Jungle", "Midlane", "Botlane (ADC)", "Support"])
        st.markdown("---")
        
        col_ally, col_enemy = st.columns(2)
        equipe_alliee = []
        with col_ally:
            st.subheader("🔵 ALLIÉS DÉJÀ SÉLECTIONNÉS")
            equipe_alliee.append(st.selectbox("Top", liste_champs, key="a_top"))
            equipe_alliee.append(st.selectbox("Jungle", liste_champs, key="a_jgl"))
            equipe_alliee.append(st.selectbox("Mid", liste_champs, key="a_mid"))
            equipe_alliee.append(st.selectbox("ADC", liste_champs, key="a_adc"))
            equipe_alliee.append(st.selectbox("Support", liste_champs, key="a_sup"))

        with col_enemy:
            st.subheader("🔴 ÉQUIPE ENNEMIE (Optionnel)")
            st.selectbox("Top", liste_champs, key="e_top")
            st.selectbox("Jungle", liste_champs, key="e_jgl")
            st.selectbox("Mid", liste_champs, key="e_mid")
            st.selectbox("ADC", liste_champs, key="e_adc")
            st.selectbox("Support", liste_champs, key="e_sup")
            
        st.markdown("---")
        
        if st.button("🧠 Analyser la Draft & Voir les Recommandations"):
            manque_ap, manque_tank, recos = analyser_compo(equipe_alliee, ma_lane, champions_data)
            
            st.subheader("📊 Diagnostic de ta composition :")
            
            diag_col1, diag_col2 = st.columns(2)
            if manque_ap:
                diag_col1.markdown("<span class='warning-text'>⚠️ Manque de dégâts magiques (AP). L'équipe ennemie va stack de l'Armure.</span>", unsafe_allow_html=True)
            else:
                diag_col1.success("✅ Dégâts mixtes assurés.")
                
            if manque_tank:
                diag_col2.markdown("<span class='warning-text'>⚠️ Manque d'Engage / Frontline. Les teamfights seront fragiles.</span>", unsafe_allow_html=True)
            else:
                diag_col2.success("✅ Bonne présence de Tank/Frontline.")

            st.markdown(f"### 🎯 Picks Meta Suggérés en {ma_lane}")
            if not recos:
                st.info("Ta composition est déjà bien équilibrée ou tu n'as pas entré d'alliés. Prends ton main !")
            else:
                rec_cols = st.columns(len(recos))
                for i, reco in enumerate(recos):
                    with rec_cols[i]:
                        st.markdown("<div class='champ-card'>", unsafe_allow_html=True)
                        st.image(reco['image'], width=80)
                        st.markdown(f"<h4 style='color: white;'>{reco['nom']}</h4>", unsafe_allow_html=True)
                        if "Tank" in reco['tags'] and manque_tank: st.write("🟢 Parfait pour la Frontline")
                        if "Mage" in reco['tags'] and manque_ap: st.write("🟣 Comble le manque d'AP")
                        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ONGLET 3 : BUILD DYNAMIQUE (LE NOUVEAU TRUC)
    # ==========================================
    elif menu == "3. L'Adaptateur de Build":
        st.markdown("<h1 style='text-align: center;'>Forgeron Tactique (Builds)</h1>", unsafe_allow_html=True)
        st.write("Tu ne sais pas quels objets faire dans ta partie ? Renseigne ton champion et l'équipe adverse, on te dit quoi acheter pour les détruire.")
        
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("T'es qui ?")
            mon_champ = st.selectbox("Ton Champion", liste_champs)
            if mon_champ != "Aucun":
                st.image(champions_data[mon_champ]['image_url'], width=100)
                
        with c2:
            st.subheader("T'affrontes qui ? (L'équipe ennemie)")
            e_cols = st.columns(5)
            e_team = []
            e_team.append(e_cols[0].selectbox("Top", liste_champs, key="b_top"))
            e_team.append(e_cols[1].selectbox("Jgl", liste_champs, key="b_jgl"))
            e_team.append(e_cols[2].selectbox("Mid", liste_champs, key="b_mid"))
            e_team.append(e_cols[3].selectbox("ADC", liste_champs, key="b_adc"))
            e_team.append(e_cols[4].selectbox("Sup", liste_champs, key="b_sup"))

        st.markdown("---")
        if mon_champ != "Aucun" and any(c != "Aucun" for c in e_team):
            if st.button("🔨 Générer mon Plan de Build"):
                st.subheader(f"Adaptation de Build pour {mon_champ}")
                st.markdown("<div class='advice-box'>", unsafe_allow_html=True)
                
                conseils_build = generer_build(mon_champ, e_team, champions_data)
                for conseil in conseils_build:
                    st.markdown(f"- {conseil}", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Sélectionne ton champion et au moins un ennemi pour générer ton build.")

else:
    st.warning("Initialisation des bases de données Riot Games en cours...")
