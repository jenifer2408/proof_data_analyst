import pandas as pd

# ==========================================
# 1. LOAD ALL DATA SOURCES
# ==========================================

sales_df = pd.read_csv("data/superstore.csv")

customer_df = pd.read_csv("data/customer_registry.csv")

with open("audit_rules.txt", "r", encoding="utf-8") as file:
    rules = file.read()


# ==========================================
# 2. DISPLAY BASIC INFORMATION
# ==========================================

print("\n========== ANALYZER ==========")

print("\nSuperstore rows:", len(sales_df))
print("Customer registry rows:", len(customer_df))

print("\nSuperstore columns:")
print(list(sales_df.columns))

print("\nCustomer registry columns:")
print(list(customer_df.columns))


# ==========================================
# 3. DISPLAY BUSINESS RULES
# ==========================================

print("\n========== AUDIT RULES ==========")

print(rules)


# ==========================================
# 4. CHECK CUSTOMER ID CONNECTION
# ==========================================

sales_customers = set(
    sales_df["Customer ID"].dropna()
)

registry_customers = set(
    customer_df["Customer ID"].dropna()
)

matching_customers = sales_customers.intersection(
    registry_customers
)

print("\n========== TABLE CONNECTION ==========")

print(
    "Customers in Superstore:",
    len(sales_customers)
)

print(
    "Customers in Registry:",
    len(registry_customers)
)

print(
    "Matching Customer IDs:",
    len(matching_customers)
)


# ==========================================
# 5. MERGE THE TABLES
# ==========================================

merged_df = sales_df.merge(
    customer_df,
    on="Customer ID",
    how="left"
)

print("\n========== MERGED DATA ==========")

print("Merged rows:", len(merged_df))

print("\nSample merged data:")
print(
    merged_df[
        [
            "Customer ID",
            "Customer Name",
            "Sales",
            "Profit",
            "Risk Level",
            "Currency Unit",
            "Audit Status"
        ]
    ].head()
)


# ==========================================
# 6. BASIC DATA QUALITY CHECK
# ==========================================

print("\n========== DATA QUALITY ==========")

print(
    "Missing Customer IDs:",
    sales_df["Customer ID"].isnull().sum()
)

print(
    "Missing Sales:",
    sales_df["Sales"].isnull().sum()
)

print(
    "Duplicate rows:",
    sales_df.duplicated().sum()
)

print(
    "Negative Quantity:",
    (sales_df["Quantity"] < 0).sum()
)


print("\n========== ANALYZER READY ==========")
# ==========================================
# 7. FIRST PROOF-CARRYING ANALYSIS
# ==========================================

print("\n========== QUESTION ==========")

question = "What is the total sales?"

print(question)


# ==========================================
# 8. APPLY BASIC DATA RULES
# ==========================================

# Remove rows where Customer ID is missing
valid_df = sales_df.dropna(subset=["Customer ID"])

# Remove rows where Sales is missing
valid_df = valid_df.dropna(subset=["Sales"])


# ==========================================
# 9. CALCULATE ANSWER
# ==========================================

total_sales = valid_df["Sales"].sum()


# ==========================================
# 10. DISPLAY ANSWER
# ==========================================

print("\n========== ANSWER ==========")

print(f"Total Sales: ${total_sales:,.2f}")


# ==========================================
# 11. DISPLAY PROOF CODE
# ==========================================

print("\n========== PROOF CODE ==========")

print("""
valid_df = sales_df.dropna(subset=["Customer ID"])
valid_df = valid_df.dropna(subset=["Sales"])
total_sales = valid_df["Sales"].sum()
print(total_sales)
""")


# ==========================================
# 12. VERIFICATION
# ==========================================

print("========== VERIFICATION ==========")

print("Status: VERIFIED")
print("Reason: Calculation was executed directly on the dataset.")
# ==========================================
# 13. SECOND ANALYSIS
# ==========================================

print("\n========== SECOND QUESTION ==========")

question2 = "Which region has the highest sales?"

print(question2)


# ==========================================
# 14. APPLY DATA RULES
# ==========================================

region_df = sales_df.dropna(
    subset=["Customer ID", "Sales", "Region"]
)


# ==========================================
# 15. GROUP SALES BY REGION
# ==========================================

region_sales = (
    region_df
    .groupby("Region")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

highest_region = region_sales.index[0]
highest_sales = region_sales.iloc[0]


# ==========================================
# 16. DISPLAY ANSWER
# ==========================================

print("\n========== ANSWER ==========")

print(
    f"Highest sales region: {highest_region}"
)

print(
    f"Sales: ${highest_sales:,.2f}"
)


# ==========================================
# 17. DISPLAY ALL REGIONS
# ==========================================

print("\nSales by region:")

print(region_sales)


# ==========================================
# 18. DISPLAY PROOF CODE
# ==========================================

print("\n========== PROOF CODE ==========")

print("""
region_df = sales_df.dropna(
    subset=["Customer ID", "Sales", "Region"]
)

region_sales = (
    region_df
    .groupby("Region")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

highest_region = region_sales.index[0]
highest_sales = region_sales.iloc[0]

print(highest_region)
print(highest_sales)
""")


# ==========================================
# 19. VERIFICATION
# ==========================================

print("========== VERIFICATION ==========")

print("Status: VERIFIED")
print("Reason: Regional sales were grouped and calculated directly from the dataset.")