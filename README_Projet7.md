# 🗄️ Concevez et analysez une base de données NoSQL — Projet 7

<div align="center">

![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-DataFrame-CD792C?style=for-the-badge&logo=polars&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

**Association NosCités** • Paris & Lyon • Été 2024

*Conception, analyse et pérennisation d'une base de données MongoDB à partir de données Airbnb scrapées.*

</div>

---

## 📋 Contexte du projet

L'association **NosCités** surveille les plateformes de location courte durée (Airbnb, etc.) pour mesurer leur impact sur l'offre de logements à Paris et Lyon.

Suite à un **crash total** de la base de données des locations parisiennes dès la première semaine, une sauvegarde a été retrouvée — son intégrité devait être vérifiée et la base reconstruite sur une architecture robuste et pérenne.

**Objectif :** Importer, analyser, et pérenniser les données de location courte durée de Paris et Lyon dans une base de données NoSQL MongoDB, puis connecter cette base à Power BI pour l'analyse visuelle.

---

## 🛠️ Stack technique

| Outil | Rôle |
|---|---|
| **MongoDB** | Base de données NoSQL principale (stockage des documents) |
| **MongoDB Compass** | Interface graphique d'import et d'exploration |
| **mongosh** | Shell MongoDB pour les requêtes et la configuration |
| **Python / Pandas** | Préparation et tagging des données CSV avant import |
| **Polars** | Analyse de données avancée (requêtes analytiques rapides, moteur Rust) |
| **MongoDB Connector for BI (ODBC)** | Intermédiaire NoSQL → SQL pour connecter MongoDB à Power BI |
| **Power BI** | Outil de Business Intelligence / Dashboard |
| **mongoimport** | Import en masse des fichiers CSV dans MongoDB |

---

## 📁 Données utilisées

| Fichier | Source | Volume |
|---|---|---|
| `listings_Paris.csv` | Scraping Airbnb — juin 2024 | **95 885 annonces** |
| `listings_Lyon.csv` | Scraping Airbnb — juin 2024 | **9 973 annonces** |

> Les deux fichiers ont été importés dans la base `noscites`, collection `listings_paris`, avec un champ `city` pour distinguer les deux villes.

---

## 🗂️ Structure d'un document MongoDB

Chaque annonce est stockée sous forme de document JSON avec les catégories de champs suivantes :

| Catégorie | Exemples de champs | Type MongoDB |
|---|---|---|
| Identifiants | `_id`, `id`, `scrape_id`, `license` | ObjectId, Integer, NumberLong |
| Informations générales | `listing_url`, `source`, `name`, `picture_url` | String |
| Informations hôte | `host_id`, `host_name`, `host_since`, `host_is_superhost` | Integer, String, Date, Boolean |
| Localisation | `host_location`, `neighbourhood_cleansed`, `latitude`, `longitude` | String, Float |
| Logement | `property_type`, `room_type`, `accommodates`, `bedrooms` | String, Integer |
| Équipements | `amenities` | Array |
| Règles de séjour | `minimum_nights`, `maximum_nights` | Integer |
| Disponibilités | `has_availability`, `availability_30`, `availability_365` | Boolean, Integer |
| Avis | `number_of_reviews`, `first_review`, `review_scores_rating` | Integer, Date, Float |
| Indicateurs calculés | `reviews_per_month`, `calculated_host_listings_count` | Float, Integer |

---

## ✅ Pourquoi MongoDB (NoSQL) plutôt que SQL ?

| Critère | MongoDB ✅ | SQL ❌ |
|---|---|---|
| **Schéma** | Flexible — les champs optionnels n'impactent pas la structure | Rigide — colonnes vides en masse |
| **Données imbriquées** | `amenities` stocké en `Array` JSON nativement | Jointures multiples nécessaires |
| **Scalabilité** | Horizontale — 95 885 documents sans dégradation | Verticale — limite matérielle |
| **Hétérogénéité** | Chaque document peut avoir sa propre structure | Schéma figé pour tous les enregistrements |

---

## 🔍 Partie 1 — Restaurer & comprendre les données

### Import des données

```bash
# Import via MongoDB Compass
# Base : noscites | Collection : listings_paris
# Total importé : 95 885 documents Paris
```

### Premières vérifications

```javascript
// Nombre total de documents
db.listings_paris.countDocuments()
// → 95 885

// Logements avec disponibilités (has_availability: true)
db.listings_paris.countDocuments({ has_availability: true })
// → 90 173
```

---

## 🔎 Partie 2 — Analyser les données

### Requêtes MongoDB (NoSQL)

#### Requête 1 — Répartition par type de location

```javascript
db.listings_paris.aggregate([
  { $group: { _id: "$room_type", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
])
```

| Type de location | Nb annonces | % |
|---|---|---|
| Entire home/apt | 85 733 | 89,4% |
| Private room | 8 975 | 9,4% |
| Hotel room | 776 | 0,8% |
| Shared room | 401 | 0,4% |

> 📌 Paris est dominée à **89,4%** par des logements entiers — c'est le cœur de la problématique de NosCités : ces appartements sont retirés du marché locatif classique.

---

#### Requête 2 — Top 5 annonces avec le plus d'évaluations

```javascript
db.listings_paris.find(
  {},
  { name: 1, number_of_reviews: 1, _id: 0 }
).sort({ number_of_reviews: -1 }).limit(5)
```

| # | Nom de l'annonce | Nb évaluations |
|---|---|---|
| 1 | Sweet & cosy room next to Canal Saint Martin ❤️ | 3 067 |
| 2 | Double/Twin Room, close to Opera and the Louvre with breakfast included | 2 620 |
| 3 | Bed in Dorm of 8 Beds "The Big One" in Paris | 2 294 |
| 4 | Comfortable bed in shared rooms of 8 in Paris 12e | 2 105 |
| 5 | Nice Room for 2 people | 2 048 |

---

#### Requête 3 — Nombre d'hôtes uniques

```javascript
db.listings_paris.distinct("host_id").length
// → 71 979 hôtes uniques | Ratio : ~1,33 annonce/hôte
```

---

#### Requête 4 — Locations réservables instantanément

```javascript
// Étape 1 — comptage
db.listings_paris.countDocuments({ instant_bookable: true })
// → 22 094

// Étape 2 — proportion
(22094 / 95885 * 100).toFixed(2) + " %"
// → 23,04%
```

> 📌 Seulement **23,04%** des annonces sont en réservation instantanée. La majorité des hôtes parisiens préfèrent valider manuellement chaque réservation.

---

#### Requête 5 — Hôtes avec plus de 100 annonces

```javascript
// Étape 1 — identifier les hôtes avec +100 annonces
db.listings_paris.aggregate([
  { $group: { _id: "$host_id", host_name: { $first: "$host_name" }, nb_annonces: { $sum: 1 } } },
  { $match: { nb_annonces: { $gt: 100 } } },
  { $sort: { nb_annonces: -1 } }
])
// Top : Blueground (730), Veeve (497), Pierre De WeHost (426)...

// Étape 2 — compter le nombre de ces hôtes
db.listings_paris.aggregate([
  { $group: { _id: "$host_id", nb_annonces: { $sum: 1 } } },
  { $match: { nb_annonces: { $gt: 100 } } },
  { $count: "nb_hotes_plus_100" }
])
// → 24 hôtes

// Étape 3 — proportion
(24 / 71979 * 100).toFixed(2) + " %"
// → 0,03%
```

> 📌 **24 hôtes** sur 71 979 possèdent plus de 100 annonces — une infime minorité (0,03%) mais très impactante sur le marché immobilier. Ce sont souvent des sociétés de gestion locative.

---

#### Requête 6 — Super hôtes

```javascript
// Étape 1 — nombre de super hôtes uniques
db.listings_paris.distinct("host_id", { host_is_superhost: true }).length
// → 10 027

// Étape 2 — proportion
(10027 / 71979 * 100).toFixed(2) + " %"
// → 13,93%
```

> 📌 Seulement **13,93%** des hôtes ont le label "super hôte" — il reste sélectif et difficile à obtenir.

---

### Requêtes Polars (Python — moteur Rust)

Les 5 requêtes suivantes ont été réalisées avec **Polars** plutôt que MongoDB pour bénéficier de sa rapidité de calcul analytique. Polars est un DataFrame Python construit en Rust, ce qui le rend nettement plus rapide que Pandas pour les agrégations sur de grands volumes de données.

#### Requête 7 — Taux de réservation moyen par mois et type de logement

```python
req1 = (
    df.with_columns([
        ((365 - pl.col("availability_365")) / 365 * 100).alias("taux_reservation"),
        pl.col("last_scraped").dt.month().alias("mois")
    ])
    .group_by(["mois", "room_type"])
    .agg(pl.col("taux_reservation").mean().round(2).alias("taux_moyen"))
    .sort(["mois", "room_type"])
)
```

| Mois | Type de logement | Taux de réservation moyen |
|---|---|---|
| Juin | Private room | 68,80% |
| Juin | Entire home/apt | 64,90% |
| Juin | Shared room | 63,33% |
| Juin | Hotel room | 52,38% |

---

#### Requête 8 — Médiane des avis pour tous les logements

```python
req2 = df.select(
    pl.col("number_of_reviews").median().alias("mediane_avis")
)
# → Médiane : 3 avis
```

> 📌 La médiane de **3 avis** révèle une distribution très asymétrique : la majorité des annonces sont peu actives, tandis qu'une minorité concentre des centaines d'avis.

---

#### Requête 9 — Médiane des avis par catégorie d'hôte

```python
req3 = (
    df.group_by("host_is_superhost")
    .agg(pl.col("number_of_reviews").median().alias("mediane_avis"))
    .sort("host_is_superhost")
)
```

| Catégorie d'hôte | Médiane des avis |
|---|---|
| Super hôte ✅ | 24 avis |
| Non super hôte ❌ | 2 avis |

> 📌 Les super hôtes ont **12 fois plus** d'avis en médiane — le label est directement corrélé à une activité intense.

---

#### Requête 10 — Densité de logements par quartier

```python
req4 = (
    df.group_by("neighbourhood_cleansed")
    .agg(pl.len().alias("nb_logements"))
    .sort("nb_logements", descending=True)
)
```

| # | Quartier | Nb logements |
|---|---|---|
| 1 | Buttes-Montmartre | 10 555 |
| 2 | Popincourt | 8 430 |
| 3 | Vaugirard | 7 802 |
| ... | ... | ... |
| 20 | Louvre | 2 026 |

---

#### Requête 11 — Quartiers avec le plus fort taux de réservation

```python
req5 = (
    df.with_columns([
        ((365 - pl.col("availability_365")) / 365 * 100).alias("taux_reservation")
    ])
    .group_by("neighbourhood_cleansed")
    .agg(pl.col("taux_reservation").mean().round(2).alias("taux_moyen"))
    .sort("taux_moyen", descending=True)
)
```

| # | Quartier | Taux de réservation |
|---|---|---|
| 1 | Ménilmontant | 71,08% |
| 2 | Buttes-Chaumont | 69,73% |
| 3 | Buttes-Montmartre | 69,25% |
| ... | ... | ... |
| 20 | Élysée | 53,68% |

---

### Connexion MongoDB → Power BI (via ODBC)

Power BI n'accepte nativement que le moteur SQL. Pour connecter MongoDB (NoSQL), un intermédiaire a été installé : **MongoDB Connector for BI (ODBC)**. Ce connecteur traduit les requêtes SQL de Power BI en requêtes MongoDB à la volée, tout en conservant le modèle NoSQL côté base de données.

**Étapes de configuration :**

1. Télécharger et installer **MongoDB Connector for BI**
2. Ouvrir les **Sources de données ODBC** (Windows) → Ajouter → choisir **Unicode**
3. Configurer la source : nom `Projet 7`, hôte `localhost`, port `3307`
4. Lancer **mongosqld.exe** en local (traduit SQL → MongoDB)
5. Dans Power BI → **Obtenir des données** → **ODBC**
6. Sélectionner la source `Projet 7`
7. Naviguer vers la base `noscites` → sélectionner la table `listings_paris`
8. Charger les données → créer le dashboard

---

## 🔒 Partie 3 — Pérenniser la base de données

### Étape 1 — Import Paris + Lyon dans une seule collection

Les données Lyon ont été taguées avec un champ `city: "Lyon"` via un script Python avant l'import. Les données Paris ont été taguées via `updateMany`.

```python
# Tagging des données Lyon
df = pd.read_csv("listings_Lyon.csv", low_memory=False)
df["city"] = "Lyon"
df.to_csv("listings_lyon_tagged.csv", index=False, encoding="utf-8")
```

```javascript
// Tagging des données Paris existantes
db.listings_paris.updateMany(
  { city: { $exists: false } },
  { $set: { city: "Paris" } }
)
```

```bash
# Vérification de la répartition
db.listings_paris.aggregate([
  { $group: { _id: "$city", count: { $sum: 1 } } }
])
# → [{ _id: 'Lyon', count: 9973 }, { _id: 'Paris', count: 95885 }]
```

---

### Étape 2 — Réplication des données avec ReplicaSet

**Objectif :** Protéger les données contre les pannes matérielles. Si le PRIMARY tombe, le SECONDARY prend automatiquement le relais grâce au vote de l'ARBITRE.

```bash
# Lancement des 3 instances en local
mongod --replSet rs0 --port 27020 --dbpath C:\data\rs0
mongod --replSet rs0 --port 27021 --dbpath C:\data\rs1
mongod --replSet rs0 --port 27022 --dbpath C:\data\rs2
```

```javascript
// Initialisation du ReplicaSet
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27020" },
    { _id: 1, host: "localhost:27021" },
    { _id: 2, host: "localhost:27022", arbiterOnly: true }
  ]
})
```

| Nœud | Rôle | Port |
|---|---|---|
| **PRIMARY** | Reçoit toutes les écritures | 27020 |
| **SECONDARY** | Réplique les données en temps réel | 27021 |
| **ARBITRE** | Vote d'élection en cas de panne (ne stocke pas de données) | 27022 |

**Vérification de la réplication :**

```javascript
// Insertion sur le PRIMARY
db.test_replication.insertOne({ message: "test replication", city: "Paris" })

// Vérification sur le SECONDARY (port 27021)
db.test_replication.find()
// → Document bien présent ✅ — réplication fonctionnelle
```

---

### Étape 3 — Distribution des données avec le Sharding

**Objectif :** Distribuer les données Paris et Lyon sur des serveurs séparés. Chaque requête est automatiquement routée vers le bon shard par le Mongos, sans scanner les données de l'autre ville.

**Architecture du cluster :**

| Composant | Rôle | Port |
|---|---|---|
| **Config Server** | Stocke la carte du cluster (métadonnées) | 27030 |
| **Mongos** | Routeur des requêtes (point d'entrée unique) | 27050 |
| **shardRS1** | Données Paris | 27040 |
| **shardRS2** | Données Lyon | 27041 |

```bash
# Config Server
mongod --configsvr --replSet configRS --port 27030 --dbpath C:\data\configdb

# Shards
mongod --shardsvr --replSet shardRS1 --port 27040 --dbpath C:\data\shard1
mongod --shardsvr --replSet shardRS2 --port 27041 --dbpath C:\data\shard2

# Routeur Mongos
mongos --configdb configRS/localhost:27030 --port 27050
```

```javascript
// Ajout des shards au cluster
sh.addShard("shardRS1/localhost:27040")
sh.addShard("shardRS2/localhost:27041")

// Activation du sharding sur la base
sh.enableSharding("noscites")

// Sharding de la collection par ville
sh.shardCollection("noscites.listings_paris", { "city": 1 })
```

**Clé de sharding choisie : `city`**

Le champ `city` est la clé de sharding naturelle car les données sont partitionnées géographiquement : une requête sur Lyon est routée directement vers `shardRS2` sans scanner les 95 885 documents parisiens, et inversement.

---

### Schéma d'architecture complet

```
┌─────────────────────────────────┐    ┌──────────────────────────────────────────┐
│     ReplicaSet rs0              │    │     Cluster Sharding                     │
│     (Réplication)               │    │     (Distribution)                       │
│                                 │    │                                          │
│  PRIMARY      ──réplication──►  │    │  Config Server    ──carte──►  Mongos     │
│  Port 27020                     │    │  Port 27030                   Port 27050 │
│                                 │    │                               │          │
│  SECONDARY                      │    │                     ┌─────────┴──────┐   │
│  Port 27021                     │    │                     ▼                ▼   │
│                                 │    │               shardRS1         shardRS2  │
│  ARBITRE (vote)                 │    │               Port 27040       Port 27041│
│  Port 27022                     │    │               Données Paris   Données Lyon│
└─────────────────────────────────┘    └──────────────────────────────────────────┘
         │                                          │
         └──── Source de données ──────────────────►│
                                                    │
                                              Mongos (27050)
                                                    │
                                              ODBC Connector
                                                    │
                                               Power BI 📊
```

---

## 📊 Tableau récapitulatif — Processus complet

| # | Étape | Objectif | Commande principale | Résultat |
|---|---|---|---|---|
| 1 | Import Paris + Lyon | Centraliser les données avec distinction par ville | `mongoimport` + `updateMany` | 95 885 Paris + 9 973 Lyon ✅ |
| 2 | Création dossiers ReplicaSet | Préparer l'espace de stockage | `mkdir C:\data\rs0/rs1/rs2` | 3 dossiers créés ✅ |
| 3 | Lancement 3 instances | Simuler 3 serveurs en local | `mongod --replSet rs0 --port 27020/27021/27022` | 3 instances actives ✅ |
| 4 | Init ReplicaSet | Définir les rôles PRIMARY/SECONDARY/ARBITRE | `rs.initiate({...})` | ReplicaSet rs0 opérationnel ✅ |
| 5 | Vérification réplication | Confirmer la réplication | `insertOne` Primary → `find` Secondary | Document repliqué ✅ |
| 6 | Création dossiers Sharding | Préparer le cluster | `mkdir C:\data\configdb/shard1/shard2` | 3 dossiers créés ✅ |
| 7 | Lancement Config Server | Stocker la carte du cluster | `mongod --configsvr --port 27030` | Config Server actif ✅ |
| 8 | Init Config Server | Rendre le Config Server opérationnel | `rs.initiate()` sur 27030 | ok: 1 ✅ |
| 9 | Lancement 2 Shards | Simuler 2 serveurs de stockage | `mongod --shardsvr --port 27040/27041` | 2 shards actifs ✅ |
| 10 | Init Shards | Rendre les shards opérationnels | `rs.initiate()` sur 27040 et 27041 | ok: 1 ✅ |
| 11 | Lancement Mongos | Créer le point d'entrée unique | `mongos --configdb configRS/localhost:27030 --port 27050` | Routeur actif ✅ |
| 12 | Ajout Shards au cluster | Enregistrer les shards | `sh.addShard(...)` | shardAdded ✅ |
| 13 | Activation Sharding BDD | Autoriser la distribution | `sh.enableSharding("noscites")` | ok: 1 ✅ |
| 14 | Sharding collection | Distribuer par ville | `sh.shardCollection(..., { city: 1 })` | Collection shardée ✅ |
| 15 | Vérification finale | Confirmer la distribution | `sh.status()` + `getShardDistribution()` | 2 shards actifs, balancer ON ✅ |

---

## 📦 Livrable

Le livrable du projet est un support de présentation PowerPoint nommé selon la convention :

```
Nom_Prenom_support_mmaaaa.pptx
```

Déposé dans un dossier ZIP nommé :

```
Concevez_et_analysez_une_base_de_donnees_NoSQL_nom_prenom.zip
```

---

## 👤 Auteur

Projet réalisé dans le cadre de la formation **Data Analyst** — OpenClassrooms  
Parcours : *Concevez et analysez une base de données NoSQL*
