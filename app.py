import math
import streamlit as st

st.set_page_config(page_title="KR Auction Cars", page_icon="🇰🇷", layout="centered")

PROFILES = {
    "Hyundai Glovis Autobell Smart Auction": {
        "kind": "auction", "rate": 2.2, "min_fee": 165_000, "max_fee": 440_000,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 3_000_000, "annual_fee": 150_000,
        "note": "B2B. Commission acheteur 2,2 %, min 165 000 KRW, max 440 000 KRW. Dépôt membre 3 M KRW et cotisation annuelle 150 000 KRW. Transport en supplément."
    },
    "Lotte Auto Auction — véhicule coréen": {
        "kind": "auction", "rate": 2.2, "min_fee": 110_000, "max_fee": 440_000,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 3_000_000, "annual_fee": 250_000,
        "note": "B2B / exportateur enregistré. Commission 2,2 % TTC, min 110 000 KRW, max 440 000 KRW pour une voiture coréenne. Dépôt 3 M KRW ; formule annuelle A publiée à 250 000 KRW."
    },
    "Lotte Auto Auction — véhicule importé": {
        "kind": "auction", "rate": 2.2, "min_fee": 110_000, "max_fee": 550_000,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 3_000_000, "annual_fee": 250_000,
        "note": "B2B / exportateur enregistré. Commission 2,2 % TTC, min 110 000 KRW, max 550 000 KRW pour une voiture importée."
    },
    "Encar — annonce vendeur / dealer": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 400_000, "performance": 150_000,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Marketplace : pas de commission acheteur Encar unique. Encar indique typiquement ~350–450k KRW de 매도비 (gestion/stockage) et une assurance performance souvent ~100–200k KRW sur véhicules coréens, davantage sur imports. Valeurs ci-dessous modifiables."
    },
    "KB ChaChaCha — annonce vendeur / dealer": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 440_000, "performance": 150_000,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Marketplace : KB précise que 매도관리비 et autres frais dépendent de la politique du vendeur. Des annonces actuelles affichent par exemple 440k KRW de management + assurance performance. Valeurs modifiables."
    },
    "K Car — véhicule direct": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Vente directe K Car. Le calculateur K Car sépare prix véhicule, frais de transfert/immatriculation, frais de gestion et livraison. Il n'y a pas de commission d'enchère standard à ajouter."
    },
    "K Car — marché direct sécurisé": {
        "kind": "percent", "rate": 0.5, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 33_000, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Marché direct K Car : protection acheteur 0,5 % du montant sécurisé + service de transfert de propriété en ligne 33 000 KRW si utilisé."
    },
    "Autowini — achat/export Corée": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Plateforme export. Les frais de véhicule/shipping varient selon le lot et la destination. Documents optionnels publics : 100 USD par document (certificat export anglais, origine, historique, etc.)."
    },
    "Personnalisé": {
        "kind": "auction", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "Saisis les frais exacts affichés par le vendeur ou la plateforme."
    },
}


def krw(v):
    return f"₩ {v:,.0f}".replace(",", " ")


def eur(v):
    return f"€ {v:,.2f}".replace(",", " ")


def calc_commission(price, kind, rate, min_fee, max_fee):
    if kind in ("retail",):
        return 0.0
    fee = price * rate / 100.0
    if min_fee:
        fee = max(fee, min_fee)
    if max_fee:
        fee = min(fee, max_fee)
    return fee


def total_cost(price, commission, fixed_fee, management, performance, acquisition_tax,
               registration, inland, export_handling, port, shipping, docs, other):
    platform_total = price + commission + fixed_fee + management + performance
    local_total = platform_total + acquisition_tax + registration + inland
    export_total = local_total + export_handling + port + shipping + docs + other
    return platform_total, local_total, export_total


st.title("🇰🇷 KR Auction Cars")
st.caption("Calculateur d'achat de voitures en Corée — enchères, marketplaces et export")

with st.sidebar:
    st.header("🏛️ Plateforme")
    profile = st.selectbox("Site / type d'achat", list(PROFILES.keys()))
    p = PROFILES[profile]
    st.info(p["note"])

    kind = p["kind"]

    st.subheader("Frais plateforme")
    rate = st.number_input("Commission (%)", min_value=0.0, max_value=50.0, value=float(p["rate"]), step=0.1)
    min_fee = st.number_input("Commission minimum (KRW)", min_value=0.0, value=float(p["min_fee"]), step=10_000.0)
    max_fee = st.number_input("Commission maximum (KRW, 0 = aucun)", min_value=0.0, value=float(p["max_fee"]), step=10_000.0)
    fixed_fee = st.number_input("Frais fixes plateforme (KRW)", min_value=0.0, value=float(p["fixed_fee"]), step=10_000.0)
    management = st.number_input("매도비 / frais de gestion dealer (KRW)", min_value=0.0, value=float(p["management"]), step=10_000.0)
    performance = st.number_input("Assurance / garantie performance (KRW)", min_value=0.0, value=float(p["performance"]), step=10_000.0)

    st.divider()
    st.subheader("Compte professionnel")
    membership_deposit = st.number_input("Dépôt / caution (KRW, non inclus dans le véhicule)", min_value=0.0, value=float(p["membership_deposit"]), step=100_000.0)
    annual_fee = st.number_input("Cotisation annuelle (KRW, optionnel dans le calcul)", min_value=0.0, value=float(p["annual_fee"]), step=10_000.0)
    include_annual = st.toggle("Inclure la cotisation annuelle dans ce véhicule", value=False)

    st.divider()
    st.subheader("Conversion")
    krw_per_eur = st.number_input("KRW pour 1 EUR", min_value=1.0, value=1650.0, step=10.0, help="Taux modifiable manuellement.")
    usd_per_eur = st.number_input("USD pour 1 EUR", min_value=0.01, value=1.18, step=0.01)


tab1, tab2, tab3 = st.tabs(["💶 Coût total", "🎯 Budget max", "ℹ️ Guide Corée"])

with tab1:
    price = st.number_input("Prix véhicule / adjudication (KRW)", min_value=0.0, value=20_000_000.0, step=100_000.0)
    commission = calc_commission(price, kind, rate, min_fee, max_fee)

    st.subheader("Achat local en Corée")
    local_purchase = st.toggle("Immatriculation en Corée avant export / usage local", value=False)

    if local_purchase:
        acquisition_rate = st.number_input("Taxe d'acquisition (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.1)
        acquisition_tax = price * acquisition_rate / 100.0
        registration = st.number_input("Frais d'immatriculation / obligations / agence (KRW)", min_value=0.0, value=0.0, step=10_000.0)
    else:
        acquisition_tax = 0.0
        registration = 0.0
        st.caption("Mode export direct : la taxe d'acquisition coréenne n'est pas ajoutée automatiquement.")

    inland = st.number_input("Transport intérieur Corée (KRW)", min_value=0.0, value=0.0, step=10_000.0)

    st.subheader("Export")
    export_mode = st.toggle("Ajouter les coûts export", value=True)
    if export_mode:
        export_handling = st.number_input("Frais export / agent / radiation (KRW)", min_value=0.0, value=0.0, step=10_000.0)
        port = st.number_input("Port / terminal / handling (KRW)", min_value=0.0, value=0.0, step=10_000.0)
        shipping = st.number_input("Fret maritime (KRW)", min_value=0.0, value=0.0, step=50_000.0)
        docs_usd = st.number_input("Documents export optionnels (USD)", min_value=0.0, value=0.0, step=100.0)
        docs = docs_usd / usd_per_eur * krw_per_eur
        other = st.number_input("Autres coûts Corée (KRW)", min_value=0.0, value=0.0, step=10_000.0)
    else:
        export_handling = port = shipping = docs = other = 0.0

    if include_annual:
        fixed_for_vehicle = fixed_fee + annual_fee
    else:
        fixed_for_vehicle = fixed_fee

    platform_total, local_total, grand_total = total_cost(
        price, commission, fixed_for_vehicle, management, performance,
        acquisition_tax, registration, inland,
        export_handling, port, shipping, docs, other
    )

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Prix voiture", krw(price))
    c2.metric("Frais Corée", krw(grand_total - price))
    c3.metric("TOTAL", krw(grand_total))
    st.metric("Équivalent EUR", eur(grand_total / krw_per_eur))

    st.subheader("Détail")
    rows = [
        ("Prix véhicule", price),
        ("Commission acheteur", commission),
        ("Frais fixes plateforme", fixed_for_vehicle),
        ("매도비 / gestion dealer", management),
        ("Assurance performance", performance),
        ("Taxe d'acquisition", acquisition_tax),
        ("Immatriculation / agence", registration),
        ("Transport intérieur", inland),
        ("Export / radiation / agent", export_handling),
        ("Port / terminal", port),
        ("Fret maritime", shipping),
        ("Documents", docs),
        ("Autres", other),
    ]
    for label, amount in rows:
        if amount:
            a, b = st.columns([3, 1])
            a.write(label)
            b.markdown(f"**{krw(amount)}**")

    if membership_deposit:
        st.info(f"Caution membre à immobiliser : **{krw(membership_deposit)}** — elle n'est pas ajoutée au coût du véhicule car elle est normalement remboursable/maintenue sur le compte.")

with tab2:
    budget_eur = st.number_input("Budget total maximum (EUR)", min_value=0.0, value=15_000.0, step=500.0)
    budget_krw = budget_eur * krw_per_eur

    extras = st.number_input("Réserve frais fixes/export hors prix véhicule (KRW)", min_value=0.0, value=1_000_000.0, step=100_000.0)

    low, high = 0.0, budget_krw
    for _ in range(80):
        mid = (low + high) / 2
        fee = calc_commission(mid, kind, rate, min_fee, max_fee)
        est = mid + fee + fixed_fee + management + performance + extras + (annual_fee if include_annual else 0)
        if est <= budget_krw:
            low = mid
        else:
            high = mid

    st.metric("Prix voiture maximum estimé", krw(low))
    st.caption(f"≈ {eur(low / krw_per_eur)} pour la voiture, avec {krw(extras)} de réserve frais.")

with tab3:
    st.markdown("""
### Types de sites coréens

**Marketplaces grand public**
- **Encar** : très gros inventaire de dealers et particuliers ; frais dealer variables.
- **KB ChaChaCha** : marketplace KB ; les frais de gestion dépendent du vendeur.
- **K Car** : stock détenu/vendu directement par K Car + marché direct sécurisé.

**Enchères professionnelles**
- **Hyundai Glovis Autobell Smart Auction** : réservé aux professionnels du commerce automobile.
- **Lotte Auto Auction** : réservé aux entreprises automobiles ou exportateurs enregistrés.

**Export international**
- **Autowini** : achat + export + shipping ; frais logistiques variables selon la voiture et la destination.

### À retenir pour un export
Si la voiture est achetée directement pour export et radiée en Corée, ne traite pas automatiquement les **7 % de taxe d'acquisition** comme un coût certain. Le montage dépend de l'acheteur/importateur/exportateur et de la façon dont le véhicule est transféré/radié. C'est pourquoi l'app laisse cette taxe désactivée par défaut en mode export direct.

### Frais non inclus automatiquement
- fret maritime vers Algérie / autre pays ;
- assurance maritime ;
- frais portuaires destination ;
- douane, TVA et taxes d'importation du pays d'arrivée ;
- frais d'agent/exportateur lorsque non publiés.
""")

st.caption("KR Auction Cars · Calculateur indicatif. Les conditions du vendeur, de la plateforme et de l'exportateur font foi.")
