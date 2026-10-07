import pandas as pd

# ==========================================
# 1. LOAD DATASET
# ==========================================

file_path = "data/superstore.csv"

df = pd.read_csv(file_path)


# ==========================================
# 2. BASIC DATASET INFORMATION
# ==========================================

print("\n========== DATASET PROFILE ==========")

print("Dataset:", file_path)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# ==========================================
# 3. COLUMN INFORMATION
# ==========================================

print("\n========== COLUMN INFORMATION ==========")

for column in df.columns:
    print(
        f"{column} | "
        f"Type: {df[column].dtype} | "
        f"Unique: {df[column].nunique()} | "
        f"Missing: {df[column].isnull().sum()}"
    )


# ==========================================
# 4. MISSING DATA
# ==========================================

print("\n========== MISSING DATA ==========")

missing = df.isnull().sum()

found_missing = False

for column in df.columns:
    if missing[column] > 0:
        found_missing = True

        percentage = (missing[column] / len(df)) * 100

        print(
            f"{column}: "
            f"{missing[column]} missing "
            f"({percentage:.2f}%)"
        )

if not found_missing:
    print("No missing values found.")


# ==========================================
# 5. DUPLICATE DATA
# ==========================================

print("\n========== DUPLICATES ==========")

duplicates = df.duplicated().sum()

print("Duplicate rows:", duplicates)


# ==========================================
# 6. NUMERICAL COLUMNS
# ==========================================

print("\n========== NUMERICAL COLUMNS ==========")

numeric_columns = df.select_dtypes(
    include="number"
).columns

for column in numeric_columns:
    print(
        f"{column}: "
        f"Min={df[column].min()}, "
        f"Max={df[column].max()}, "
        f"Mean={df[column].mean():.2f}"
    )


# ==========================================
# 7. POSSIBLE DATE COLUMNS
# ==========================================

print("\n========== DATE-LIKE COLUMNS ==========")

for column in df.columns:

    if "date" in column.lower():

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        valid_dates = converted.notna().sum()

        print(
            f"{column}: "
            f"{valid_dates}/{len(df)} "
            f"values look like dates"
        )


# ==========================================
# 8. CATEGORICAL COLUMNS
# ==========================================

print("\n========== CATEGORICAL COLUMNS ==========")

categorical_columns = df.select_dtypes(
    include="object"
).columns

for column in categorical_columns:

    unique_values = df[column].dropna().unique()

    print(
        f"{column}: "
        f"{len(unique_values)} unique values"
    )


# ==========================================
# 9. DATA QUALITY SUMMARY
# ==========================================

print("\n========== DATA QUALITY SUMMARY ==========")

total_missing = df.isnull().sum().sum()
total_duplicates = df.duplicated().sum()

print("Total missing values:", total_missing)
print("Total duplicate rows:", total_duplicates)

if total_missing > 0:
    print("WARNING: Dataset contains missing values.")

if total_duplicates > 0:
    print("WARNING: Dataset contains duplicate rows.")

print("\n========== PROFILING COMPLETE ==========")