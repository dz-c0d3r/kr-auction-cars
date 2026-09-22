import math
import json
import urllib.request
import urllib.error
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
    "GOTCHA — Bronze": {
        "kind": "auction", "rate": 2.2, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "service_usd": 250, "deposit_usd": 5000,
        "note": "Accès international aux enchères Glovis, AJ, K Car, Lotte et SK. Service Bronze : 250 USD/voiture, dépôt remboursable 5 000 USD. L'enchère maison (environ 2,2–2,585 %) et le fret maritime restent séparés."
    },
    "GOTCHA — Silver": {
        "kind": "auction", "rate": 2.2, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "service_usd": 180, "deposit_usd": 7500,
        "note": "Service Silver : 180 USD/voiture, dépôt remboursable 7 500 USD. Accès agrégé aux principales enchères coréennes."
    },
    "GOTCHA — Gold": {
        "kind": "auction", "rate": 2.2, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "service_usd": 80, "deposit_usd": 10000,
        "note": "Service Gold : 80 USD/voiture, dépôt remboursable 10 000 USD. Live bidding illimité selon le plan publié."
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


@st.cache_data(ttl=60)
def get_upbit_usdt_krw():
    """Public Upbit ticker. Returns KRW per 1 USDT or None."""
    try:
        req = urllib.request.Request(
            "https://api.upbit.com/v1/ticker?markets=KRW-USDT",
            headers={"User-Agent": "KR-Auction-Cars/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data and "trade_price" in data[0]:
            return float(data[0]["trade_price"])
    except Exception:
        return None
    return None


@st.cache_data(ttl=60)
def get_binance_p2p_usdt_dzd(amount_usdt=0.0):
    """
    Binance P2P benchmark for selling USDT and receiving DZD.
    Returns the LOWEST compatible listed price, per user preference.
    This endpoint is public but unofficial/undocumented and can change.
    """
    try:
        payload = {
            "page": 1,
            "rows": 20,
            "payTypes": [],
            "countries": [],
            "publisherType": None,
            "asset": "USDT",
            "fiat": "DZD",
            "tradeType": "SELL",
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 KR-Auction-Cars/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        ads = []
        for item in data.get("data", []):
            adv = item.get("adv", {})
            try:
                price = float(adv.get("price", 0))
                min_dzd = float(adv.get("minSingleTransAmount", 0) or 0)
                max_dzd = float(adv.get("maxSingleTransAmount", 0) or 0)
                available_usdt = float(adv.get("surplusAmount", 0) or 0)
            except (TypeError, ValueError):
                continue

            if price <= 0:
                continue

            if amount_usdt and amount_usdt > 0:
                order_dzd = amount_usdt * price
                if min_dzd and order_dzd < min_dzd:
                    continue
                if max_dzd and order_dzd > max_dzd:
                    continue
                if available_usdt and amount_usdt > available_usdt:
                    continue

            ads.append({
                "price": price,
                "min_dzd": min_dzd,
                "max_dzd": max_dzd,
                "available_usdt": available_usdt,
            })

        if not ads:
            return None

        return min(ads, key=lambda x: x["price"])
    except Exception:
        return None


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

    service_usd = float(p.get("service_usd", 0))
    deposit_usd = float(p.get("deposit_usd", 0))
    if profile.startswith("GOTCHA"):
        st.caption(f"Service GOTCHA publié : {service_usd:.0f} USD / voiture")

    management = st.number_input("매도비 / frais de gestion dealer (KRW)", min_value=0.0, value=float(p["management"]), step=10_000.0)
    performance = st.number_input("Assurance / garantie performance (KRW)", min_value=0.0, value=float(p["performance"]), step=10_000.0)

    st.divider()
    st.subheader("Compte professionnel")
    membership_deposit = st.number_input("Dépôt / caution (KRW, non inclus dans le véhicule)", min_value=0.0, value=float(p["membership_deposit"]), step=100_000.0)
    annual_fee = st.number_input("Cotisation annuelle (KRW, optionnel dans le calcul)", min_value=0.0, value=float(p["annual_fee"]), step=10_000.0)
    include_annual = st.toggle("Inclure la cotisation annuelle dans ce véhicule", value=False)

    if profile.startswith("GOTCHA"):
        st.info(f"Dépôt GOTCHA remboursable : {deposit_usd:,.0f} USD — non inclus dans le coût du véhicule.")


    st.divider()
    st.subheader("💱 FX / financement")

    upbit_live = get_upbit_usdt_krw()
    fx_source = st.selectbox(
        "Référence USDT → KRW",
        ["Upbit live", "OTC / bureau crypto Séoul (manuel)", "Taux personnalisé"],
        index=0,
    )

    if fx_source == "Upbit live":
        if upbit_live:
            st.success(f"Upbit live : 1 USDT ≈ {upbit_live:,.0f} KRW")
            usdt_krw_raw = upbit_live
        else:
            st.warning("Cours Upbit indisponible momentanément — utilise un taux manuel.")
            usdt_krw_raw = st.number_input(
                "KRW pour 1 USDT",
                min_value=1.0,
                value=1350.0,
                step=1.0,
                key="upbit_fallback",
            )

        upbit_fee_pct = st.number_input(
            "Frais de vente Upbit (%)",
            min_value=0.0,
            max_value=5.0,
            value=0.05,
            step=0.01,
            help="Le taux KRW market publié par Upbit est actuellement 0,05 % pour les ordres standards.",
        )
        krw_per_usdt = usdt_krw_raw * (1 - upbit_fee_pct / 100.0)
        st.caption(f"Taux net estimé après frais : 1 USDT ≈ {krw_per_usdt:,.2f} KRW")
    else:
        manual_default = float(upbit_live or 1350.0)
        krw_per_usdt = st.number_input(
            "Taux net proposé : KRW reçus pour 1 USDT",
            min_value=1.0,
            value=manual_default,
            step=1.0,
            help="Entre le taux NET réellement proposé après spread/commission par le desk OTC ou bureau crypto.",
        )
        if upbit_live:
            spread_vs_upbit = (krw_per_usdt / upbit_live - 1) * 100
            st.caption(f"Écart vs Upbit live : {spread_vs_upbit:+.2f} %")

    st.caption(
        "⚠️ Un bureau de change classique de Myeongdong échange surtout des devises cash (USD/EUR ↔ KRW), "
        "pas de l'USDT. Pour USDT → KRW, compare le taux net d'un desk OTC/crypto avec Upbit."
    )

    krw_per_eur = st.number_input(
        "KRW pour 1 EUR (référence séparée)",
        min_value=1.0,
        value=1555.0,
        step=5.0,
        help="Utilisé uniquement pour l'affichage EUR et le budget en EUR.",
    )
    usd_per_eur = st.number_input("USD pour 1 EUR", min_value=0.01, value=1.18, step=0.01)


    st.divider()
    st.subheader("🇩🇿 Binance P2P — USDT → DZD")
    st.caption(
        "Référence : annonces SELL USDT / DZD. L'app prend volontairement le prix compatible le plus bas, "
        "comme demandé. Pour vendre des USDT, un prix plus élevé serait normalement plus avantageux."
    )

    binance_manual = st.toggle("Saisir le taux Binance P2P manuellement", value=False)
    if binance_manual:
        dzd_per_usdt = st.number_input(
            "DZD pour 1 USDT",
            min_value=1.0,
            value=250.0,
            step=1.0,
            key="dzd_usdt_manual",
        )
        binance_ad = None
    else:
        binance_ad = get_binance_p2p_usdt_dzd(0.0)
        if binance_ad:
            dzd_per_usdt = binance_ad["price"]
            st.success(f"Binance P2P lowest : 1 USDT ≈ {dzd_per_usdt:,.2f} DZD")
        else:
            st.warning("Binance P2P indisponible depuis Streamlit — fallback manuel.")
            dzd_per_usdt = st.number_input(
                "DZD pour 1 USDT",
                min_value=1.0,
                value=250.0,
                step=1.0,
                key="dzd_usdt_fallback",
            )


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
        vehicle_type = st.selectbox(
            "Type de véhicule pour le RoRo",
            ["Berline / Sedan", "SUV / Crossover", "Grand SUV / 7 places", "Van / MPV", "Personnalisé"],
            index=0,
        )

        shipping_defaults = {
            "Berline / Sedan": 0.0,
            "SUV / Crossover": 0.0,
            "Grand SUV / 7 places": 0.0,
            "Van / MPV": 0.0,
            "Personnalisé": 0.0,
        }

        shipping_usdt = st.number_input(
            "RoRo shipping (USDT)",
            min_value=0.0,
            value=float(shipping_defaults[vehicle_type]),
            step=50.0,
            help="Tarif du devis RoRo. Le montant reste modifiable car le transporteur peut réviser ses prix.",
        )

        paperwork_usdt = st.number_input(
            "Paperasse export + acheminement jusqu'au port (USDT)",
            min_value=0.0,
            value=500.0,
            step=50.0,
            help="Forfait communiqué : 500 USDT.",
        )

        shipping = shipping_usdt * krw_per_usdt
        export_handling = paperwork_usdt * krw_per_usdt

        st.caption(
            f"RoRo : {shipping_usdt:,.0f} USDT ≈ {krw(shipping)} · "
            f"Paperasse/port : {paperwork_usdt:,.0f} USDT ≈ {krw(export_handling)}"
        )

        port = st.number_input("Autres frais port / terminal (KRW)", min_value=0.0, value=0.0, step=10_000.0)
        docs_usd = st.number_input("Documents export optionnels supplémentaires (USD)", min_value=0.0, value=0.0, step=100.0)
        docs = docs_usd / usd_per_eur * krw_per_eur
        other = st.number_input("Autres coûts Corée (KRW)", min_value=0.0, value=0.0, step=10_000.0)
    else:
        vehicle_type = "N/A"
        shipping_usdt = paperwork_usdt = 0.0
        export_handling = port = shipping = docs = other = 0.0

    gotcha_service_krw = (service_usd / usd_per_eur * krw_per_eur) if profile.startswith("GOTCHA") else 0.0

    if include_annual:
        fixed_for_vehicle = fixed_fee + annual_fee + gotcha_service_krw
    else:
        fixed_for_vehicle = fixed_fee + gotcha_service_krw

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
    total_usdt = grand_total / krw_per_usdt
    compatible_binance = None if binance_manual else get_binance_p2p_usdt_dzd(total_usdt)
    effective_dzd_rate = compatible_binance["price"] if compatible_binance else dzd_per_usdt
    total_dzd = total_usdt * effective_dzd_rate

    e1, e2, e3 = st.columns(3)
    e1.metric("Équivalent EUR", eur(grand_total / krw_per_eur))
    e2.metric("À financer en USDT", f"{total_usdt:,.2f} USDT")
    e3.metric("Équivalent DZD", f"{total_dzd:,.0f} DZD")

    if compatible_binance and not binance_manual:
        st.caption(
            f"Binance P2P : taux le plus bas compatible avec ~{total_usdt:,.0f} USDT = "
            f"{effective_dzd_rate:,.2f} DZD/USDT."
        )

    st.subheader("Détail")
    rows = [
        ("Prix véhicule", price),
        ("Commission acheteur", commission),
        ("Frais fixes plateforme / service", fixed_for_vehicle),
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
    budget_currency = st.selectbox("Devise du budget", ["EUR", "USDT", "DZD"], index=1)
    if budget_currency == "EUR":
        budget_value = st.number_input("Budget total maximum (EUR)", min_value=0.0, value=15_000.0, step=500.0)
        budget_krw = budget_value * krw_per_eur
    elif budget_currency == "USDT":
        budget_value = st.number_input("Budget total maximum (USDT)", min_value=0.0, value=15_000.0, step=500.0)
        budget_krw = budget_value * krw_per_usdt
    else:
        budget_value = st.number_input("Budget total maximum (DZD)", min_value=0.0, value=4_000_000.0, step=100_000.0)
        budget_krw = (budget_value / dzd_per_usdt) * krw_per_usdt

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
    st.caption(
        f"≈ {eur(low / krw_per_eur)} / {low / krw_per_usdt:,.2f} USDT pour la voiture, "
        f"avec {krw(extras)} de réserve frais."
    )

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
- L'association coréenne des maisons d'enchères recense aussi **AutoHub Auction, K Car Auction, SK Rent Car Auction, AutoInside, Car Auction**, entre autres. Leurs barèmes acheteurs n'étant pas tous publiés clairement, ils ne sont pas préremplis tant qu'un tarif fiable n'est pas disponible.

**Export international**
- **Autowini** : achat + export + shipping ; frais logistiques variables selon la voiture et la destination.
- **GOTCHA** : agrégateur international donnant accès à Glovis, AJ, K Car Auction, Lotte et SK, avec frais de service publics selon le plan.

### FX / USDT
- **Upbit** est utilisé comme benchmark live pour USDT/KRW.
- **Binance P2P** est utilisé comme benchmark USDT/DZD. L'app prend le prix SELL compatible le plus bas, conformément au choix de l'utilisateur, avec fallback manuel si Binance bloque l'accès serveur.
- Un **bureau de change classique** de Séoul donne surtout un taux cash USD/EUR/KRW : ce n'est pas directement le même marché.
- Pour un desk **OTC crypto**, utilise le taux net KRW réellement reçu par USDT et compare-le à Upbit.
- L'app affiche automatiquement l'écart en % par rapport à Upbit quand tu saisis un taux OTC manuel.

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
