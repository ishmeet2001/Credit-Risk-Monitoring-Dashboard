import pandas as pd

print("Loading data...")

df = pd.read_csv("data/raw/appl_accepted_20072019Q3.csv")

print("Data loaded:", df.shape)

df = df.sample(n=100_000, random_state=42)

print("Sampled data:", df.shape)

df.to_csv("data/processed/sample_100k.csv", index=False)

print("Saved sampled file.")
