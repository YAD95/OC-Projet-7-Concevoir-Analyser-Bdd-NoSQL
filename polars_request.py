from pymongo import MongoClient
import polars as pl

# Connexion à MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["noscites"]
collection = db["listings_paris"]

# Extraction des données
data = list(collection.find({}, {
    "_id": 0,
    "room_type": 1,
    "availability_365": 1,
    "number_of_reviews": 1,
    "neighbourhood_cleansed": 1,
    "host_is_superhost": 1,
    "last_scraped": 1
}))

# Conversion en DataFrame Polars
df = pl.DataFrame(data)

print(df.shape)
print(df.head())

# Requête 1 — Taux de réservation moyen par mois par type de logement
req1 = (
    df.with_columns([
        ((365 - pl.col("availability_365")) / 365 * 100).alias("taux_reservation"),
        pl.col("last_scraped").dt.month().alias("mois")
    ])
    .group_by(["mois", "room_type"])
    .agg(pl.col("taux_reservation").mean().round(2).alias("taux_moyen"))
    .sort(["mois", "room_type"])
)

print(req1)

# Requête 2 — Médiane des nombre d'avis pour tous les logements
req2 = df.select(
    pl.col("number_of_reviews").median().alias("mediane_avis")
)

print(req2)

# Requête 3 — Médiane des avis par catégorie d'hôte
req3 = (
    df.group_by("host_is_superhost")
    .agg(pl.col("number_of_reviews").median().alias("mediane_avis"))
    .sort("host_is_superhost")
)

print(req3)

# Requête 4 — Densité de logements par quartier
req4 = (
    df.group_by("neighbourhood_cleansed")
    .agg(pl.len().alias("nb_logements"))
    .sort("nb_logements", descending=True)
)

print(req4)

# Requête 5 — Quartiers avec le plus fort taux de réservation
req5 = (
    df.with_columns([
        ((365 - pl.col("availability_365")) / 365 * 100).alias("taux_reservation")
    ])
    .group_by("neighbourhood_cleansed")
    .agg(pl.col("taux_reservation").mean().round(2).alias("taux_moyen"))
    .sort("taux_moyen", descending=True)
)

print(req5)

