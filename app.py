import math
import json
import urllib.request
import urllib.error
import urllib.parse
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
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "EXPORT ALGÉRIE : commission acheteur Encar = 0 sur une annonce standard. Le contrat est conclu avec le vendeur/dealer. Les frais dealer (매도비, souvent ~350–450k KRW en retail Corée) et l'assurance performance (~100–200k KRW typiquement sur une voiture coréenne) ne sont PAS des commissions Encar et peuvent varier. Ils restent à 0 par défaut ici : entre uniquement les montants réellement facturés sur le devis export. Encar 믿고 est optionnel (88k–220k KRW) et n'est pas inclus."
    },
    "KB ChaChaCha — annonce vendeur / dealer": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "EXPORT ALGÉRIE : KB ChaChaCha est une marketplace ; pas de commission acheteur KB fixe ajoutée automatiquement. Les frais proviennent du dealer. Des annonces récentes affichent 440k KRW de frais de gestion et une assurance performance variable, mais ce n'est pas universel. Pour un achat export, entre uniquement les frais confirmés par le vendeur/exportateur."
    },
    "K Car — véhicule direct": {
        "kind": "retail", "rate": 0, "min_fee": 0, "max_fee": 0,
        "fixed_fee": 0, "management": 0, "performance": 0,
        "membership_deposit": 0, "annual_fee": 0,
        "note": "K Car vend directement son propre stock : pas de commission d'enchère acheteur séparée. La marge commerciale de K Car est déjà incorporée au prix affiché. Pour l'export, n'ajoute que les frais explicitement facturés."
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
def get_binance_dzd_payment_method():
    """
    Discover Binance's current payment-method identifier for Algeria Poste CCP.
    This avoids hardcoding an identifier that Binance may rename.
    """
    try:
        url = "https://www.binance.com/bapi/c2c/v1/public/c2c/agent/trade-methods?fiat=DZD"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 KR-Auction-Cars/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        data = payload.get("data", payload)
        if isinstance(data, dict):
            candidates = (
                data.get("tradeMethods")
                or data.get("paymentMethods")
                or data.get("list")
                or []
            )
        elif isinstance(data, list):
            candidates = data
        else:
            candidates = []

        best = None
        for item in candidates:
            if not isinstance(item, dict):
                continue
            identifier = str(
                item.get("identifier")
                or item.get("tradeMethodIdentifier")
                or item.get("code")
                or ""
            )
            name = str(
                item.get("tradeMethodName")
                or item.get("name")
                or item.get("paymentMethodName")
                or ""
            )
            haystack = (identifier + " " + name).lower()
            score = sum(token in haystack for token in ("algeria", "poste", "ccp"))
            if score >= 2:
                best = {
                    "identifier": identifier or "AlgeriaPosteCCP",
                    "name": name or "Algeria Poste CCP",
                }
                if score == 3:
                    break

        return best or {
            "identifier": "AlgeriaPosteCCP",
            "name": "Algeria Poste CCP",
        }
    except Exception:
        return {
            "identifier": "AlgeriaPosteCCP",
            "name": "Algeria Poste CCP",
        }


def _normalize_binance_agent_ad(item):
    """Normalize both Binance agent API and legacy friendly API ad shapes."""
    if not isinstance(item, dict):
        return None

    adv = item.get("adv", item)
    advertiser = item.get("advertiser", {})

    def num(*keys):
        for key in keys:
            value = adv.get(key)
            if value not in (None, ""):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass
        return 0.0

    price = num("price", "advPrice")
    if price <= 0:
        return None

    return {
        "price": price,
        "min_dzd": num("minSingleTransAmount", "minAmount", "minFiatAmount"),
        "max_dzd": num("maxSingleTransAmount", "maxAmount", "maxFiatAmount"),
        "available_usdt": num("surplusAmount", "availableAmount", "tradableQuantity"),
        "month_orders": int(float(advertiser.get("monthOrderCount", 0) or 0)),
        "month_finish_rate": float(advertiser.get("monthFinishRate", 0) or 0),
    }


@st.cache_data(ttl=30)
def get_binance_p2p_usdt_dzd(amount_usdt=0.0):
    """
    Dynamic Binance P2P BUY USDT/DZD quote for Algeria Poste CCP.

    Returns:
      - market_lowest: cheapest visible Algeria Poste CCP ad right now
      - compatible_lowest: cheapest ad compatible with amount_usdt, if any
      - payment_method: Binance payment-method metadata
      - count: number of valid ads inspected
    """
    payment = get_binance_dzd_payment_method()
    identifier = payment["identifier"]
    ads = []

    # Preferred public Binance Agent endpoint.
    try:
        params = urllib.parse.urlencode({
            "fiat": "DZD",
            "asset": "USDT",
            "tradeType": "BUY",
            "limit": 20,
            "order": "asc",
            "tradeMethodIdentifiers": identifier,
        })
        url = "https://www.binance.com/bapi/c2c/v1/public/c2c/agent/ad-list?" + params
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 KR-Auction-Cars/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        data = payload.get("data", payload)
        if isinstance(data, dict):
            items = data.get("ads") or data.get("list") or data.get("data") or []
        elif isinstance(data, list):
            items = data
        else:
            items = []

        for item in items:
            ad = _normalize_binance_agent_ad(item)
            if ad:
                ads.append(ad)
    except Exception:
        pass

    # Fallback to the legacy public P2P web endpoint used by Binance's website.
    if not ads:
        try:
            for page in range(1, 4):
                payload = {
                    "page": page,
                    "rows": 20,
                    "payTypes": [identifier],
                    "countries": [],
                    "publisherType": None,
                    "asset": "USDT",
                    "fiat": "DZD",
                    "tradeType": "BUY",
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
                    payload = json.loads(response.read().decode("utf-8"))

                page_items = payload.get("data", [])
                if not page_items:
                    break

                for item in page_items:
                    ad = _normalize_binance_agent_ad(item)
                    if ad:
                        ads.append(ad)
        except Exception:
            pass

    if not ads:
        return None

    # Remove exact duplicates returned across pages/endpoints.
    unique = {}
    for ad in ads:
        key = (
            round(ad["price"], 4),
            round(ad["min_dzd"], 2),
            round(ad["max_dzd"], 2),
            round(ad["available_usdt"], 4),
        )
        unique[key] = ad
    ads = list(unique.values())

    market_lowest = min(ads, key=lambda x: x["price"])

    compatible = []
    if amount_usdt and amount_usdt > 0:
        for ad in ads:
            order_dzd = amount_usdt * ad["price"]
            if ad["min_dzd"] and order_dzd < ad["min_dzd"]:
                continue
            if ad["max_dzd"] and order_dzd > ad["max_dzd"]:
                continue
            if ad["available_usdt"] and amount_usdt > ad["available_usdt"]:
                continue
            compatible.append(ad)

    compatible_lowest = (
        min(compatible, key=lambda x: x["price"])
        if compatible
        else None
    )

    return {
        "market_lowest": market_lowest,
        "compatible_lowest": compatible_lowest,
        "payment_method": payment,
        "count": len(ads),
    }


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

    management = st.number_input(
        "매도비 / frais dealer réellement facturés (KRW)",
        min_value=0.0,
        value=float(p["management"]),
        step=10_000.0,
        help="Ce n'est pas une commission de la marketplace. Pour Encar/KB en export, saisis uniquement ce que le vendeur te facture réellement."
    )
    performance = st.number_input(
        "Assurance performance réellement facturée (KRW)",
        min_value=0.0,
        value=float(p["performance"]),
        step=10_000.0,
        help="Variable selon véhicule et type de transaction. Laisse 0 si elle n'apparaît pas sur le devis export."
    )

    if profile.startswith("Encar"):
        with st.expander("ℹ️ Frais retail indicatifs Encar"):
            st.write("• Commission Encar sur annonce standard : 0 KRW")
            st.write("• 매도비 dealer observé / indiqué par Encar : ~350 000 à 450 000 KRW")
            st.write("• Assurance performance voiture coréenne : ~100 000 à 200 000 KRW")
            st.write("• Encar 믿고 (optionnel) : 88 000 à 220 000 KRW")
            st.caption("Pour l'export, ne les ajoute que s'ils figurent réellement sur le devis du vendeur/exportateur.")

    st.divider()
    st.subheader("Compte professionnel")
    membership_deposit = st.number_input("Dépôt / caution (KRW, non inclus dans le véhicule)", min_value=0.0, value=float(p["membership_deposit"]), step=100_000.0)
    annual_fee = st.number_input("Cotisation annuelle (KRW, optionnel dans le calcul)", min_value=0.0, value=float(p["annual_fee"]), step=10_000.0)
    include_annual = st.toggle("Inclure la cotisation annuelle dans ce véhicule", value=False)

    if profile.startswith("GOTCHA"):
        st.info(f"Dépôt GOTCHA remboursable : {deposit_usd:,.0f} USD — non inclus dans le coût du véhicule.")


    st.divider()
    st.subheader("💱 Exchangeur Séoul — USDT → KRW")

    upbit_live = get_upbit_usdt_krw()
    if upbit_live:
        st.caption(f"Benchmark Upbit live : 1 USDT ≈ {upbit_live:,.0f} KRW")

    use_upbit_proxy = st.toggle(
        "Utiliser Upbit comme proxy si je n'ai pas encore le taux de l'exchangeur",
        value=False,
    )

    if use_upbit_proxy and upbit_live:
        krw_per_usdt = float(upbit_live)
        st.success(f"Taux utilisé : {krw_per_usdt:,.0f} KRW / USDT (proxy Upbit)")
    else:
        exchanger_default = float(upbit_live or 1350.0)
        krw_per_usdt = st.number_input(
            "Taux NET de l'exchangeur : KRW reçus pour 1 USDT",
            min_value=1.0,
            value=exchanger_default,
            step=1.0,
            help="Entre le taux réellement proposé à Séoul, après tous spreads/frais.",
        )
        if upbit_live:
            spread_vs_upbit = (krw_per_usdt / upbit_live - 1) * 100
            st.caption(f"Écart exchangeur vs Upbit : {spread_vs_upbit:+.2f} %")

    st.caption(
        "Le coût final utilise toujours le taux NET de l'exchangeur sélectionné. "
        "Upbit sert seulement de benchmark pour vérifier le spread."
    )

    krw_per_eur = st.number_input(
        "KRW pour 1 EUR (information)",
        min_value=1.0,
        value=1555.0,
        step=5.0,
    )
    usd_per_eur = st.number_input("USD pour 1 EUR", min_value=0.01, value=1.18, step=0.01)

    st.divider()
    st.subheader("🇩🇿 Binance P2P — acheter USDT avec DZD")
    st.caption(
        "L'app recherche les annonces BUY USDT / DZD et retient le prix vendeur le plus bas "
        "compatible avec le montant nécessaire (limites + quantité disponible)."
    )

    binance_manual = st.toggle("Saisir le taux Binance P2P manuellement", value=False)
    if binance_manual:
        dzd_per_usdt = st.number_input(
            "DZD nécessaires pour acheter 1 USDT",
            min_value=1.0,
            value=250.0,
            step=1.0,
            key="dzd_usdt_manual",
        )
        binance_ad = None
    else:
        binance_quote = get_binance_p2p_usdt_dzd(0.0)
        if binance_quote:
            binance_ad = binance_quote["market_lowest"]
            dzd_per_usdt = binance_ad["price"]
            payment_name = binance_quote["payment_method"]["name"]
            st.success(
                f"Binance P2P live — {payment_name}: "
                f"1 USDT ≈ {dzd_per_usdt:,.2f} DZD"
            )
            st.caption(
                f"Prix le plus bas parmi {binance_quote['count']} annonce(s) inspectée(s). "
                "Actualisation toutes les 30 secondes."
            )
        else:
            binance_ad = None
            st.warning("Binance P2P indisponible depuis Streamlit — fallback manuel.")
            dzd_per_usdt = st.number_input(
                "DZD nécessaires pour acheter 1 USDT",
                min_value=1.0,
                value=253.5,
                step=0.5,
                key="dzd_usdt_fallback",
            )


tab1, tab2, tab3 = st.tabs(["💶 Coût total", "🎯 Budget max", "ℹ️ Guide Corée"])

with tab1:
    price = st.number_input("Prix véhicule / adjudication (KRW)", min_value=0.0, value=20_000_000.0, step=100_000.0)
    commission = calc_commission(price, kind, rate, min_fee, max_fee)

    st.subheader("🚢 Export Corée → Algérie")
    st.caption("Le calcul principal est configuré pour un achat destiné directement à l'export vers l'Algérie.")

    acquisition_tax = 0.0
    registration = 0.0
    inland = 0.0

    vehicle_type = st.selectbox(
        "Type de véhicule — tarif CIG RoRo",
        ["Compact / petite voiture", "Berline / Sedan", "SUV", "Van / MPV", "Personnalisé"],
        index=1,
    )

    cig_shipping_usd = {
        "Compact / petite voiture": 1820.0,
        "Berline / Sedan": 1920.0,
        "SUV": 2120.0,
        "Van / MPV": 2320.0,
        "Personnalisé": 0.0,
    }

    shipping_usd = st.number_input(
        "CIG RoRo — fret maritime (USD)",
        min_value=0.0,
        value=float(cig_shipping_usd[vehicle_type]),
        step=10.0,
        key=f"cig_roro_{vehicle_type}",
        help="Barème CIG communiqué, effectif MV YOUNG SHIN V.2607. BAF 120 USD déjà inclus.",
    )

    is_ev = st.toggle("Véhicule 100 % électrique : surcharge EV +300 USD", value=False)
    ev_surcharge_usd = 300.0 if is_ev else 0.0

    paperwork_usdt = st.number_input(
        "Paperasse export + acheminement jusqu'au port (USDT)",
        min_value=0.0,
        value=500.0,
        step=50.0,
        help="Forfait communiqué : 500 USDT.",
    )

    usd_to_usdt = st.number_input(
        "Conversion budget : USDT pour 1 USD",
        min_value=0.90,
        max_value=1.10,
        value=1.00,
        step=0.001,
        format="%.3f",
        help="Le devis CIG est en USD. 1,000 signifie que l'on budgète 1 USD = 1 USDT.",
    )

    shipping_usdt = (shipping_usd + ev_surcharge_usd) * usd_to_usdt
    shipping = shipping_usdt * krw_per_usdt
    export_handling = paperwork_usdt * krw_per_usdt

    st.caption(
        f"RoRo CIG : {shipping_usd:,.0f} USD"
        + (f" + {ev_surcharge_usd:,.0f} USD EV" if ev_surcharge_usd else "")
        + f" ≈ {shipping_usdt:,.2f} USDT · Paperasse/port : {paperwork_usdt:,.0f} USDT"
    )

    port = st.number_input("Autres frais port / terminal en Corée (KRW)", min_value=0.0, value=0.0, step=10_000.0)
    docs_usd = st.number_input("Documents export supplémentaires (USD)", min_value=0.0, value=0.0, step=100.0)
    docs = docs_usd * usd_to_usdt * krw_per_usdt
    other = st.number_input("Autres coûts Corée (KRW)", min_value=0.0, value=0.0, step=10_000.0)

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
    base_total_usdt = grand_total / krw_per_usdt

    # Find a Binance BUY rate compatible with the real amount.
    compatible_quote = None if binance_manual else get_binance_p2p_usdt_dzd(base_total_usdt)
    compatible_binance = compatible_quote["compatible_lowest"] if compatible_quote else None
    market_binance = compatible_quote["market_lowest"] if compatible_quote else None

    # User preference: final DZD estimate always uses the cheapest Algeria Poste CCP
    # price visible on Binance P2P. Compatibility is displayed separately.
    effective_dzd_rate = market_binance["price"] if market_binance else dzd_per_usdt
    base_total_dzd = base_total_usdt * effective_dzd_rate

    st.subheader("📈 Marge")
    margin_mode = st.selectbox(
        "Mode de marge",
        ["Aucune", "Pourcentage (%)", "Fixe en USDT", "Fixe en DZD"],
        index=0,
    )

    margin_usdt = 0.0
    margin_dzd = 0.0

    if margin_mode == "Pourcentage (%)":
        margin_pct = st.number_input("Marge (%)", min_value=0.0, value=10.0, step=0.5)
        margin_usdt = base_total_usdt * margin_pct / 100.0
        margin_dzd = margin_usdt * effective_dzd_rate
    elif margin_mode == "Fixe en USDT":
        margin_usdt = st.number_input("Marge fixe (USDT)", min_value=0.0, value=1000.0, step=100.0)
        margin_dzd = margin_usdt * effective_dzd_rate
    elif margin_mode == "Fixe en DZD":
        margin_dzd = st.number_input("Marge fixe (DZD)", min_value=0.0, value=200000.0, step=10000.0)
        margin_usdt = margin_dzd / effective_dzd_rate if effective_dzd_rate else 0.0

    final_usdt = base_total_usdt + margin_usdt

    # Refresh P2P compatibility after adding margin.
    final_quote = None if binance_manual else get_binance_p2p_usdt_dzd(final_usdt)
    final_binance = final_quote["market_lowest"] if final_quote else None
    final_compatible = final_quote["compatible_lowest"] if final_quote else None
    if final_binance:
        effective_dzd_rate = final_binance["price"]
        base_total_dzd = base_total_usdt * effective_dzd_rate
        if margin_mode == "Fixe en DZD":
            margin_usdt = margin_dzd / effective_dzd_rate
            final_usdt = base_total_usdt + margin_usdt
        else:
            margin_dzd = margin_usdt * effective_dzd_rate

    final_dzd = base_total_dzd + margin_dzd

    st.subheader("💰 Résultat export Algérie")
    c1, c2, c3 = st.columns(3)
    c1.metric("Coût Corée + export", krw(grand_total))
    c2.metric("Coût total USDT", f"{base_total_usdt:,.2f} USDT")
    c3.metric("Coût total DZD", f"{base_total_dzd:,.0f} DZD")

    if margin_mode != "Aucune":
        s1, s2, s3 = st.columns(3)
        s1.metric("Marge", f"{margin_usdt:,.2f} USDT")
        s2.metric("Marge DZD", f"{margin_dzd:,.0f} DZD")
        s3.metric("Prix avec marge", f"{final_usdt:,.2f} USDT")
        st.success(f"Prix cible avec marge : **{final_usdt:,.2f} USDT** ≈ **{final_dzd:,.0f} DZD**")

    st.caption(
        f"Exchangeur Séoul utilisé : {krw_per_usdt:,.2f} KRW/USDT · "
        f"Binance P2P BUY utilisé : {effective_dzd_rate:,.2f} DZD/USDT"
    )

    if final_binance and not binance_manual:
        st.caption(
            f"Binance P2P Algeria Poste CCP — meilleur prix marché : "
            f"{effective_dzd_rate:,.2f} DZD/USDT."
        )
        if final_compatible:
            st.caption(
                f"Meilleure annonce compatible avec ~{final_usdt:,.0f} USDT : "
                f"{final_compatible['price']:,.2f} DZD/USDT · "
                f"dispo ~{final_compatible['available_usdt']:,.0f} USDT."
            )
        else:
            st.warning(
                "L'annonce la moins chère sert au calcul comme demandé, mais aucune annonce inspectée "
                "n'accepte à elle seule la totalité du montant. Il faudra probablement répartir l'achat "
                "sur plusieurs annonces, avec un coût moyen potentiellement un peu supérieur."
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
        ("Paperasse export + acheminement port", export_handling),
        ("Autres frais port / terminal Corée", port),
        (f"RoRo CIG — {vehicle_type}", shipping),
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
        budget_rate = dzd_per_usdt
        budget_krw = (budget_value / budget_rate) * krw_per_usdt

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
- **Binance P2P** est interrogé dynamiquement sur **BUY USDT / DZD + Algeria Poste CCP**. L'app affiche le **prix marché le plus bas** (celui visible en haut de la page Binance) et, séparément, le meilleur prix réellement compatible avec le montant de la voiture.
- Un **bureau de change classique** de Séoul donne surtout un taux cash USD/EUR/KRW : ce n'est pas directement le même marché.
- Pour un desk **OTC crypto**, utilise le taux net KRW réellement reçu par USDT et compare-le à Upbit.
- L'app affiche automatiquement l'écart en % par rapport à Upbit quand tu saisis un taux OTC manuel.

### À retenir pour un export vers l'Algérie
L'app est configurée pour un **achat destiné directement à l'export**. Elle ne rajoute donc pas automatiquement la taxe d'acquisition/immatriculation coréenne. Le flux principal est : prix véhicule + frais plateforme + export Corée + RoRo → coût USDT → coût DZD → marge éventuelle.

### Frais non inclus automatiquement
- assurance maritime si elle n'est pas incluse dans le devis CIG ;
- frais portuaires destination ;
- douane, TVA et taxes d'importation du pays d'arrivée ;
- frais d'agent/exportateur lorsque non publiés.
""")

st.caption("KR Auction Cars · Calculateur indicatif. Les conditions du vendeur, de la plateforme et de l'exportateur font foi.")
