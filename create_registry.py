import pandas as pd
import random
from datetime import datetime, timedelta

# ==========================================
# 1. LOAD REAL CUSTOMER IDs
# ==========================================

ids = pd.read_csv("data/customer_ids.csv")

customer_ids = ids["Customer ID"].dropna().tolist()


# ==========================================
# 2. CREATE CUSTOMER REGISTRY
# ==========================================

records = []

for customer_id in customer_ids:

    # Risk level
    risk = random.choice([
        "Low",
        "Low",
        "Low",
        "Medium",
        "Medium",
        "High"
    ])

    # Verification date
    start_date = datetime(2025, 1, 1)
    random_days = random.randint(0, 650)

    verification_date = (
        start_date + timedelta(days=random_days)
    ).strftime("%m/%d/%Y")

    # Currency
    currency = random.choice([
        "USD",
        "USD",
        "USD",
        "EUR"
    ])

    # Audit status
    audit_status = random.choice([
        "Verified",
        "Verified",
        "Pending",
        "Suspended"
    ])

    records.append({
        "Customer ID": customer_id,
        "Risk Level": risk,
        "Verification Date": verification_date,
        "Currency Unit": currency,
        "Audit Status": audit_status
    })


# ==========================================
# 3. CREATE DATAFRAME
# ==========================================

registry = pd.DataFrame(records)


# ==========================================
# 4. ADD SOME MISSING VALUES
# ==========================================

# Missing Audit Status
registry.loc[5, "Audit Status"] = None
registry.loc[15, "Audit Status"] = None

# Missing Verification Date
registry.loc[20, "Verification Date"] = None


# ==========================================
# 5. SAVE REGISTRY
# ==========================================

registry.to_csv(
    "data/customer_registry.csv",
    index=False
)

print("Customer registry created successfully!")
print("Rows:", len(registry))
print("\nFirst 10 rows:")
print(registry.head(10))

print("\nSaved to:")
print("data/customer_registry.csv")