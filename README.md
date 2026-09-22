# KR Auction Cars 🇰🇷

Calculateur Streamlit pour estimer le coût réel d'une voiture achetée en Corée du Sud, en achat direct, via marketplace, enchère professionnelle ou export.

## Plateformes intégrées

- Hyundai Glovis Autobell Smart Auction
- Lotte Auto Auction
- Encar
- KB ChaChaCha
- K Car
- Autowini
- GOTCHA
- Profil personnalisé

L'application gère :
- commission d'enchère avec minimum/maximum ;
- 매도비 / frais de gestion vendeur ;
- assurance/performance ;
- cotisation et caution professionnelles ;
- transport intérieur Corée ;
- export / radiation / port / shipping ;
- documents export ;
- conversion KRW / EUR / USD ;
- calcul inverse budget total → prix véhicule maximum.

## Déploiement Streamlit

1. Ouvrir https://share.streamlit.io
2. Create app
3. Repository : `dz-c0d3r/kr-auction-cars`
4. Branch : `main`
5. Main file path : `app.py`
6. App URL souhaitée : `kr-auction-cars`

URL cible : https://kr-auction-cars.streamlit.app

## Remarque

Les marketplaces coréennes n'ont pas toutes une commission acheteur unique. Encar et KB ChaChaCha affichent des véhicules de vendeurs/dealers dont les frais de gestion peuvent varier. Les enchères B2B comme Hyundai Glovis et Lotte ont des barèmes plus structurés. GOTCHA donne aux acheteurs internationaux un accès agrégé à plusieurs maisons d'enchères coréennes.

Les conditions de la plateforme, du vendeur et de l'exportateur font toujours foi.
