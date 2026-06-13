import pandas as pd

df = pd.read_csv("listings_Lyon+.csv", low_memory=False)
df["city"] = "Lyon"
df.to_csv("listings_lyon_tagged.csv", index=False, encoding="utf-8")

print(f"✅ {len(df)} documents taggés avec city=Lyon")
print("✅ Fichier sauvegardé : listings_lyon_tagged.csv")