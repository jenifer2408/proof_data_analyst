import pandas as pd

df = pd.read_csv("data/superstore.csv")

customer_ids = (
    df["Customer ID"]
    .dropna()
    .drop_duplicates()
)

customer_ids.to_csv("data/customer_ids.csv", index=False)

print("Customer IDs extracted:", len(customer_ids))
print("\nFirst 10 IDs:")
print(customer_ids.head(10))
print("\nSaved to: data/customer_ids.csv")