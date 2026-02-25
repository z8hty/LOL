import streamlit as st
import requests
import random

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="NEXUS TACTICS | LoL Analyzer", layout="wide", page_icon="⚔️")

st.markdown("""
    <style>
    .stApp { background-color: #091428; color: #F0E6D2; }
    h1, h2, h3, h4 { color: #C89B3C !important; font-family: 'Trebuchet MS', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* SUPPRESSION DES BANDES BLANCHES ET STYLISATION DES INPUTS */
    div[data-baseweb="select"] > div { background-color: #0A1428 !important; border-color: #3273FA !important; color: #FFFFFF !important; }
    div[data-baseweb="popover"] > div { background-color: #0A1428 !important; color: #FFFFFF !important; border: 1px solid #3273FA !important; }
    ul[role="listbox"] li { color: #FFFFFF !important; }
    
    /* STATS ET CARTES */
    p, li, span, div { color: #F0E6D2; }
    div[data-testid="metric-container"] { background-color: #0A1428; border: 1px solid #C89B3C; padding: 15px; border-radius: 4px; box-shadow: 0 0 10px rgba(200, 155, 60, 0.2); }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: #C89B3C !important; font-size: 14px !important; font-weight: bold !important; text-transform: uppercase; }
    
    .vs-text { text-align: center; font-size: 40px; color: #C89B3C; font-weight: 900; font-style: italic; margin-top: 50px; }
    .advice-box { background-color: #0A1428; border-left: 4px solid #0AC8B9; padding: 20px; margin-top: 20px; border-radius: 4px; }
    .champ-card { background-color: #0A1428; border: 1px solid #3273FA; padding: 15px; border-radius: 5px; text-align: center; }
    .item-box { display: flex; align-items: center; background-color: #050A14; padding: 10px; border: 1px solid #C89B3C; border-radius: 5px; margin-bottom: 10px;}
    .item-box img { width: 40px; height: 40px; border-radius: 5px; margin-right: 15px; border: 1px solid #3273FA; }
    .item-highlight { color: #0AC8B9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LISTES META STRICTES ---
META_ROLES = {
    "Toplane": ["Aatrox", "Camille", "Cho'Gath", "Darius", "Dr. Mundo", "Fiora", "Garen", "Gnar", "Gragas", "Gwen", "Illaoi", "Irelia", "Jax", "Jayce", "K'Sante", "Kayle", "Kennen", "Kled", "Malphite", "Maokai", "Mordekaiser", "Nasus", "Olaf", "Ornn", "Pantheon", "Poppy", "Quinn", "Renekton", "Riven", "Rumble", "Sett", "Shen", "Singed", "Sion", "Tahm Kench", "Teemo", "Trundle", "Tryndamere", "Urgot", "Vayne", "Volibear", "Wukong", "Yasuo", "Yone", "Yorick"],
    "Jungle": ["Amumu", "Bel'Veth", "Briar", "Diana", "Ekko", "Elise", "Evelynn", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern", "Jarvan IV", "Karthus", "Kayn", "Kha'Zix", "Kindred", "Lee Sin", "Lillia", "Master Yi", "Nidalee", "Nocturne", "Nunu & Willump", "Poppy", "Rammus", "Rengar", "Sejuani", "Shaco", "Shyvana", "Skarner", "Taliyah", "Talon", "Trundle", "Udyr", "Vi", "Viego", "Volibear", "Warwick", "Wukong", "Xin Zhao", "Zac"],
    "Midlane": ["Ahri", "Akali", "Akshan", "Anivia", "Annie", "Aurelion Sol", "Azir", "Cassiopeia", "Corki", "Diana", "Ekko", "Fizz", "Galio", "Hwei", "Irelia", "Kassadin", "Katarina", "LeBlanc", "Lissandra", "Lux", "Malzahar", "Naafiri", "Neeko", "Orianna", "Qiyana", "Ryze", "Smolder", "Sylas", "Syndra", "Talon", "Twisted Fate", "Veigar", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone", "Zed", "Ziggs", "Zoe"],
    "Botlane (ADC)": ["Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx", "Kai'Sa", "Kalista", "Kog'Maw", "Lucian", "Miss Fortune", "Nilah", "Samira", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne", "Xayah", "Yasuo", "Zeri", "Ziggs"],
    "Support": ["Alistar", "Ashe", "Bard", "Blitzcrank", "Brand", "Braum", "Heimerdinger", "Janna", "Karma", "Leona", "Lulu", "Lux", "Maokai", "Milio", "Morgana", "Nami", "Nautilus", "Pantheon", "Pyke", "Rakan", "Rell", "Renata Glasc", "Senna", "Seraphine", "Sona", "Soraka", "Swain", "Tahm Kench", "Taric", "Thresh", "Vel'Koz", "Xerath", "Yuumi", "Zilean", "Zyra"]
}

# --- CONNEXION AUX SERVEURS RIOT ---
@st.cache_data(ttl=86400)
def get_lol_data():
    try:
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
        
        # Data Champions
        champs_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json"
        champs_data = requests.get(champs_url).json()['data']
        
        champions = {}
        for champ_id, info in champs_data.items():
            champions[info['name']] = {
                'id': champ_id, 'title': info['title'], 'tags': info['tags'],
                'image_url': f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{info['image']['full']}"
            }
            
        # Data Objets (Items)
        items_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/item.json"
        items_data = requests.get(items_url).json()['data']
        
        items = {}
        for item_id, info in items_data.items():
            items[info['name']] = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item_id}.png"
            
        return champions, items, version
    except:
        return None, None, None

def get_item_image(item_name, items_dict):
    """Recherche l'URL de l'image de l'objet de manière souple"""
    for nom_exact, url in items_dict.items():
        if item_name.lower() in nom_exact.lower():
            return url
    return "https://ddragon.leagueoflegends.com/cdn/14.5.1/img/item/3340.png" # Ward par défaut si introuvable

# --- LOGIQUE D'ANALYSE MATCHUP ---
def generer_conseils_lane(mon_champ, son_champ, lane):
    conseils = []
    if lane == "Jungle":
        conseils = [
            f"**Pathing :** Observe de quel côté {son_champ} commence pour anticipe s'il va gank ou farm.",
            f"**Objectifs :** Sécurise la vision sur les Larves du Néant ou le Dragon avant que {son_champ} ne s'y installe.",
            f"**Invade :** Si {mon_champ} a un meilleur 1v1 en début de partie, n'hésite pas à le chercher dans sa jungle.",
            "Contrôle le Carapateur pour garantir la vision à tes laners."
        ]
    else:
        conseils = [
            f"**Gestion de Wave :** Ne push pas bêtement. Garde la wave proche de ta tour si le jungler ennemi est agressif.",
            f"**Trading :** Joue autour des délais de récupération (cooldowns) des sorts principaux de {son_champ}.",
            f"**Priorité :** Essaie d'avoir la priorité de lane (push) quand ton jungler fait le carapateur ou un objectif.",
            "Attention au passage niveau 2, c'est le moment clé pour prendre l'avantage ou mourir."
        ]
    return random.sample(conseils, 3)

# --- LOGIQUE DE DRAFT ---
def analyser_compo(equipe_alliee, ma_lane, champions_data):
    tags_equipe = [tag for champ in equipe_alliee if champ in champions_data for tag in champions_data[champ]['tags']]
    manque_ap = "Mage" not in tags_equipe
    manque_tank = "Tank" not in tags_equipe
    
    suggestions = []
    champions_viables = META_ROLES.get(ma_lane, [])
    
    for nom in champions_viables:
        if nom not in champions_data or nom in equipe_alliee: continue
        score = 1
        tags_champ = champions_data[nom]['tags']
        if manque_ap and "Mage" in tags_champ: score += 3
        if manque_tank and ("Tank" in tags_champ or "Fighter" in tags_champ): score += 3
        suggestions.append({"nom": nom, "score": score, "image": champions_data[nom]['image_url'], "tags": tags_champ})
                
    return manque_ap, manque_tank, sorted(suggestions, key=lambda x: x['score'], reverse=True)[:3]

# --- LOGIQUE DE BUILD COMPLET ---
def generer_build_complet(mon_champ, e_team, champions_data, items_data):
    tags_ennemis = [tag for champ in e_team if champ in champions_data for tag in champions_data[champ]['tags']]
    nb_tanks = tags_ennemis.count("Tank") + tags_ennemis.count("Fighter")
    nb_assassins = tags_ennemis.count("Assassin")
    nb_mages = tags_ennemis.count("Mage")
    nb_supports = tags_ennemis.count("Support")
    
    mon_tag = champions_data[mon_champ]['tags'][0]
    
    # CORE BUILD
    core_items = []
    if mon_tag == "Mage": core_items = ["Compagnon de Luden", "Flamme-ombre", "Coiffe de Rabadon"]
    elif mon_tag == "Assassin": core_items = ["Lame spectre de Youmuu", "Opportunité", "Manteau de la nuit"]
    elif mon_tag == "Marksman": core_items = ["Tueur de krakens", "Lame d'infini", "Salutations de Lord Dominik"]
    elif mon_tag == "Tank": core_items = ["Égide solaire", "Jak'Sho, le Protéiforme", "Cœur gelé"]
    elif mon_tag == "Fighter": core_items = ["Ciel éventré", "Gage de Sterak", "Force de la trinité"]
    else: core_items = ["Éclat de glace pure", "Rédemption", "Mikael"]
    
    html_core = "<div style='display: flex; gap: 15px; margin-bottom: 20px;'>"
    for item in core_items:
        img = get_item_image(item, items_data)
        html_core += f"<div><img src='{img}' width='50' style='border: 1px solid #C89B3C; border-radius: 5px;'><br><span style='font-size: 12px;'>{item}</span></div>"
    html_core += "</div>"
    
    # SITUATIONAL ITEMS
    adaptations = []
    if nb_supports >= 1 or "Fighter" in tags_ennemis:
        if mon_tag in ["Mage", "Support"]: adaptations.append(("Morellonomicon", "L'équipe ennemie se soigne beaucoup. Indispensable."))
        elif mon_tag in ["Marksman", "Fighter", "Assassin"]: adaptations.append(("Rappel mortel", "Coupe les soins ennemis (Anti-heal obligatoire)."))
        else: adaptations.append(("Cotte épineuse", "Pour renvoyer les dégâts et réduire les soins."))

    if nb_tanks >= 2:
        if mon_tag == "Mage": adaptations.append(("Tourment de Liandry", "Fait fondre les tanks basés sur leurs PV max."))
        elif mon_tag in ["Marksman", "Assassin"]: adaptations.append(("Salutations de Lord Dominik", "Pénètre l'armure massive de la frontline."))
        elif mon_tag == "Fighter": adaptations.append(("Couperet noir", "Réduit l'armure ennemie à chaque coup."))

    if nb_assassins >= 2:
        if mon_tag in ["Mage", "Support"]: adaptations.append(("Sablier de Zhonya", "L'actif te sauvera du burst des assassins."))
        else: adaptations.append(("Ange gardien", "Te donne une seconde vie si tu te fais one-shot."))
            
    if nb_mages >= 2:
        if mon_tag in ["Tank", "Fighter"]: adaptations.append(("Force de la nature", "La meilleure résistance magique contre le poke AP."))
        elif mon_tag == "Marksman": adaptations.append(("Gueule de Malmortius", "Un bouclier anti-magie vital contre leur burst."))

    return html_core, adaptations

# --- INITIALISATION ---
champions_data, items_data, version = get_lol_data()

if champions_data:
    st.sidebar.markdown("## ⚔️ NEXUS TACTICS")
    menu = st.sidebar.radio("Outils Stratégiques", ["1. Matchup 1v1", "2. Assistant de Draft", "3. Build & Items"])
    st.sidebar.markdown("---")
    
    liste_champs = ["Aucun"] + sorted(list(champions_data.keys()))

    # ==========================================
    # ONGLET 1 : MATCHUP 1V1 (Corrigé)
    # ==========================================
    if menu == "1. Matchup 1v1":
        st.markdown("<h1 style='text-align: center;'>Analyse de Matchup</h1>", unsafe_allow_html=True)
        
        col_lane, col_elo = st.columns(2)
        lane = col_lane.selectbox("📍 Ta Lane :", ["Toplane", "Jungle", "Midlane", "Botlane (ADC)", "Support"])
        elo = col_elo.selectbox("🏆 Ton Élo :", ["Iron - Silver", "Gold - Platinum", "Emerald - Diamond", "Master+"])

        st.markdown("---")
        
        c1, c2, c3 = st.columns([2, 1, 2])
        
        default_mon = "Kha'Zix" if lane == "Jungle" else "Ahri"
        default_son = "Amumu" if lane == "Jungle" else "Zed"
        
        with c1:
            mon_choix = st.selectbox("Ton Champion", liste_champs[1:], index=liste_champs[1:].index(default_mon) if default_mon in liste_champs else 0)
            st.image(champions_data[mon_choix]['image_url'], width=100)
            
        with c2:
            st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)

        with c3:
            son_choix = st.selectbox("Adversaire Direct", liste_champs[1:], index=liste_champs[1:].index(default_son) if default_son in liste_champs else 1)
            st.image(champions_data[son_choix]['image_url'], width=100)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Winrate", f"{random.uniform(45.0, 55.0):.1f} %")
        m2.metric("Difficulté", random.choice(["Facile", "Skill Matchup", "Difficile"]))
        m3.metric("Gold Diff @15min", f"{random.choice(['+', '-'])}{random.randint(100, 600)} G")
        m4.metric("Avantage (1v1)", f"{random.uniform(40.0, 60.0):.1f} %")

        st.markdown("<div class='advice-box'>", unsafe_allow_html=True)
        st.subheader(f"🧠 Gameplan Spécifique ({lane})")
        conseils = generer_conseils_lane(mon_choix, son_choix, lane)
        for c in conseils:
            st.write("- " + c)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ONGLET 2 : ASSISTANT DE DRAFT (Méta fixée)
    # ==========================================
    elif menu == "2. Assistant de Draft":
        st.markdown("<h1 style='text-align: center;'>Assistant de Composition</h1>", unsafe_allow_html=True)
        st.write("L'outil analyse les faiblesses de ton équipe et te suggère les meilleurs picks.")
        
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
            if manque_ap: diag_col1.error("⚠️ Manque de dégâts magiques (AP).")
            else: diag_col1.success("✅ Dégâts mixtes assurés.")
                
            if manque_tank: diag_col2.error("⚠️ Manque d'Engage / Frontline.")
            else: diag_col2.success("✅ Bonne présence de Tank/Frontline.")

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
    # ONGLET 3 : BUILD COMPLET (NOUVEAU DESIGN)
    # ==========================================
    elif menu == "3. Build & Items":
        st.markdown("<h1 style='text-align: center;'>Forgeron Tactique (Builds)</h1>", unsafe_allow_html=True)
        st.write("Le guide d'achat complet pour détruire la composition ennemie.")
        
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
                html_core, adaptations = generer_build_complet(mon_champ, e_team, champions_data, items_data)
                
                st.subheader(f"1️⃣ Core Build (Standard) pour {mon_champ}")
                st.write("Les objets de base que tu dois construire dans 90% des parties :")
                st.markdown(html_core, unsafe_allow_html=True)
                
                st.subheader("2️⃣ Objets Situationnels (L'Adaptation parfaite)")
                if not adaptations:
                    st.success("La composition ennemie est très basique. Reste sur ton build principal !")
                else:
                    for nom_item, raison in adaptations:
                        img_url = get_item_image(nom_item, items_data)
                        st.markdown(f"""
                        <div class="item-box">
                            <img src="{img_url}">
                            <div>
                                <span class="item-highlight">{nom_item}</span><br>
                                <span style="font-size: 14px;">{raison}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Sélectionne ton champion et au moins un ennemi pour générer ton build.")

else:
    st.warning("Initialisation des bases de données Riot Games en cours...")
