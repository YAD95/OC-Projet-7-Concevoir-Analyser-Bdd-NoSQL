![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-DataFrame-CD792C?style=for-the-badge&logo=polars&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

🇫🇷 Français | readme in english 👉 [🇬🇧 English](README.en.md)
#  Concevez et analysez une base de données NoSQL — Projet 7

> **Association NosCités** • Paris & Lyon • Été 2024

---

##  --- Contexte ---

L'association **NosCités** surveille les plateformes de location courte durée (Airbnb) pour mesurer leur impact sur l'offre de logements à Paris et Lyon. Suite à un crash de la base de données parisienne, une sauvegarde a été retrouvée — l'objectif est de la restaurer, l'analyser, et mettre en place une architecture robuste et pérenne.

**Données :** 95 885 annonces Paris + 9 973 annonces Lyon — scraping Airbnb juin 2024  
**Base de données :** MongoDB (NoSQL) — base `noscites`, collection `listings_paris`

---

## --- Stack technique ---

| Outil | Usage |
|---|---|
| MongoDB + MongoDB Compass | Stockage et exploration des données |
| Python / Pandas | Préparation et tagging des données CSV |
| Polars | Analyses avancées (moteur Rust, haute performance) |
| MongoDB Connector for BI (ODBC) | Connexion MongoDB → Power BI |
| Power BI | Dashboard et visualisation |

---

## --- Contenu du repository ---

| Fichier | Description |
|---|---|
| `presentation.pptx` | Support de présentation complet du projet |
| `presentation.pdf` | Version PDF de la présentation |
| `polars_request.py` | Script des requêtes analytiques avec Polars |
| `tagging_lyon_scripts.py` | Script Python de préparation des données Lyon |

> ⚠️ Les fichiers CSV bruts (données Airbnb) ne sont pas inclus en raison de leur taille.

---

## --- Ce qui a été fait ---

### Partie 1 — Restaurer & comprendre les données
- Import de 95 885 documents dans MongoDB via MongoDB Compass
- Description de la structure d'un document (types de champs, catégories de données)
- Justification du choix NoSQL face à SQL pour ce type de données
- Premières vérifications : nombre total de documents, nombre de logements disponibles

### Partie 2 — Analyser les données

**6 requêtes réalisées avec MongoDB :**
1. Nombre d'annonces par type de location
2. Les 5 annonces avec le plus d'évaluations
3. Nombre total d'hôtes différents
4. Nombre de locations réservables instantanément
5. Hôtes avec plus de 100 annonces
6. Nombre de super hôtes et leur proportion

**5 requêtes réalisées avec Polars :**
1. Taux de réservation moyen par mois et par type de logement
2. Médiane du nombre d'avis pour tous les logements
3. Médiane du nombre d'avis par catégorie d'hôte
4. Densité de logements par quartier de Paris
5. Quartiers avec le plus fort taux de réservation

> Polars a été utilisé pour ces requêtes car son moteur Rust offre de meilleures performances sur de grands volumes de données.

**Connexion MongoDB → Power BI :**  
Power BI n'acceptant que le moteur SQL, un intermédiaire a été installé : **MongoDB Connector for BI (ODBC)**. Ce connecteur traduit les requêtes SQL de Power BI en requêtes MongoDB, permettant d'importer les données NoSQL et de construire un dashboard.

### Partie 3 — Pérenniser la base de données

**Étape 1 — Import Paris + Lyon**  
Les données Lyon ont été taguées avec un champ `city: Lyon` via un script Python, puis importées dans la même collection que Paris.

**Étape 2 — Réplication avec ReplicaSet**  
Mise en place d'un ReplicaSet de 3 nœuds en local :
- **PRIMARY** (port 27020) : reçoit toutes les écritures
- **SECONDARY** (port 27021) : réplique les données en temps réel, prend le relais en cas de panne
- **ARBITRE** (port 27022) : gère les votes d'élection, ne stocke pas de données

**Étape 3 — Distribution avec le Sharding**  
Mise en place d'un cluster de sharding pour séparer les données Paris et Lyon sur des serveurs distincts. La clé de sharding est le champ `city` — chaque requête est routée directement vers le bon shard sans scanner les données de l'autre ville.

- **Config Server** (port 27030) : stocke la carte du cluster
- **Mongos** (port 27050) : routeur unique des requêtes
- **shardRS1** (port 27040) : données Paris
- **shardRS2** (port 27041) : données Lyon

---

📎 *Pour le détail des requêtes, résultats et captures d'écran, consultez la présentation.*

---

## --- 👤 Auteur---
YAD95 
Projet réalisé dans le cadre de la formation **Data Engineer** — OpenClassrooms  
