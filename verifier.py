import pandas as pd


print("========== VERITAS VERIFIER ==========")


# =========================================================
# LOAD DATA
# =========================================================

sales_df = pd.read_csv("data/superstore.csv")
customer_df = pd.read_csv("data/customer_registry.csv")


# =========================================================
# READ EXECUTOR RESULT
# =========================================================

with open(
    "verification_input.txt",
    "r",
    encoding="utf-8"
) as file:

    executor_answer = float(
        file.read().strip()
    )


print(
    "Executor result:",
    executor_answer
)


# =========================================================
# ASK WHICH QUESTION IS BEING VERIFIED
# =========================================================

question = input(
    "\nEnter the question being verified: "
)

question_lower = question.lower()


# =========================================================
# VERIFIER 1
# TOTAL SALES
# =========================================================

if (
    "total sales" in question_lower
    and "high-risk" not in question_lower
    and "high risk" not in question_lower
):

    print(
        "\nVerification type: TOTAL SALES"
    )


    # Remove exact duplicate records
    verified_df = (
        sales_df
        .drop_duplicates()
        .copy()
    )


    # Remove missing Sales
    verified_df = verified_df[
        verified_df["Sales"].notna()
    ].copy()


    # Remove negative Quantity
    verified_df = verified_df[
        verified_df["Quantity"].isna()
        |
        (verified_df["Quantity"] >= 0)
    ].copy()


    # Independent calculation
    verified_answer = (
        verified_df["Sales"].sum()
    )


    # Compare
    difference = abs(
        verified_answer
        -
        executor_answer
    )


# =========================================================
# VERIFIER 2
# HIGHEST SALES REGION
# =========================================================

elif (
    "highest sales" in question_lower
    and "region" in question_lower
):

    print(
        "\nVerification type: HIGHEST SALES REGION"
    )


    # Remove exact duplicate records
    verified_df = (
        sales_df
        .drop_duplicates()
        .copy()
    )


    # Remove missing Sales
    verified_df = verified_df[
        verified_df["Sales"].notna()
    ].copy()


    # Remove negative Quantity
    verified_df = verified_df[
        verified_df["Quantity"].isna()
        |
        (verified_df["Quantity"] >= 0)
    ].copy()


    # Group sales by region
    region_sales = (
        verified_df
        .groupby("Region")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    # Independent answer
    verified_answer = region_sales.index[0]


    # Executor result is normally numeric,
    # so this branch is not compatible with
    # the current verification_input format.
    #
    # We display the independent answer
    # and stop here.

    print(
        "\nIndependent calculation:",
        verified_answer
    )

    print(
        "\nFor text answers such as 'Central', "
        "the current verification_input.txt "
        "format must be changed from float to text."
    )

    print(
        "\nSTATUS: TEXT VERIFICATION READY"
    )

    exit()


# =========================================================
# VERIFIER 3
# HIGH-RISK CUSTOMER SALES
# =========================================================

elif (
    "high-risk" in question_lower
    or "high risk" in question_lower
):

    print(
        "\nVerification type: HIGH-RISK CUSTOMER SALES"
    )


    # -----------------------------------------------------
    # CLEAN SALES DATA
    # -----------------------------------------------------

    verified_sales = (
        sales_df
        .drop_duplicates()
        .copy()
    )


    # Customer ID required
    verified_sales = verified_sales[
        verified_sales["Customer ID"].notna()
    ].copy()


    # Sales required
    verified_sales = verified_sales[
        verified_sales["Sales"].notna()
    ].copy()


    # Negative quantity is treated as a data-quality issue
    verified_sales = verified_sales[
        verified_sales["Quantity"].isna()
        |
        (verified_sales["Quantity"] >= 0)
    ].copy()


    # -----------------------------------------------------
    # CLEAN CUSTOMER REGISTRY
    # -----------------------------------------------------

    verified_registry = (
        customer_df
        .drop_duplicates()
        .copy()
    )


    # Check Customer ID uniqueness
    if verified_registry[
        "Customer ID"
    ].duplicated().any():

        print(
            "\nERROR: Duplicate Customer IDs "
            "found in customer registry."
        )

        print(
            "\nSTATUS: VERIFICATION FAILED"
        )

        exit()


    # -----------------------------------------------------
    # JOIN TWO DATASETS
    # -----------------------------------------------------

    verified_joined = verified_sales.merge(
        verified_registry[
            [
                "Customer ID",
                "Risk Level",
                "Currency Unit"
            ]
        ],
        on="Customer ID",
        how="left",
        validate="many_to_one"
    )


    # -----------------------------------------------------
    # SELECT HIGH-RISK CUSTOMERS
    # -----------------------------------------------------

    high_risk_df = verified_joined[
        verified_joined["Risk Level"]
        .astype("string")
        .str.strip()
        .str.upper()
        == "HIGH"
    ].copy()


    # -----------------------------------------------------
    # NORMALIZE CURRENCY
    # -----------------------------------------------------

    high_risk_df["Currency Unit"] = (
        high_risk_df["Currency Unit"]
        .astype("string")
        .str.strip()
        .str.upper()
    )


    # -----------------------------------------------------
    # EXCHANGE RATES
    # -----------------------------------------------------

    exchange_rates = {
        "USD": 1.0,
        "EUR": 1.12
    }


    high_risk_df["Exchange Rate"] = (
        high_risk_df["Currency Unit"]
        .map(exchange_rates)
    )


    # -----------------------------------------------------
    # CHECK CURRENCY
    # -----------------------------------------------------

    if high_risk_df[
        "Exchange Rate"
    ].isna().any():

        print(
            "\nERROR: Missing or unsupported currency."
        )

        print(
            "\nSTATUS: VERIFICATION FAILED"
        )

        exit()


    # -----------------------------------------------------
    # INDEPENDENT CALCULATION
    # -----------------------------------------------------

    verified_answer = (
        high_risk_df["Sales"]
        *
        high_risk_df["Exchange Rate"]
    ).sum()


    # Compare
    difference = abs(
        verified_answer
        -
        executor_answer
    )


# =========================================================
# UNSUPPORTED QUESTION
# =========================================================

else:

    print(
        "\nSTATUS: NOT VERIFIED"
    )

    print(
        "Reason: No independent verifier "
        "exists for this question yet."
    )

    exit()


# =========================================================
# DISPLAY NUMERIC VERIFICATION
# =========================================================

print(
    "\nIndependent calculation:",
    verified_answer
)

print(
    "Difference:",
    difference
)


# =========================================================
# FINAL VERIFICATION
# =========================================================

if difference < 0.000001:

    print(
        "\n======================================"
    )

    print(
        "STATUS: VERIFIED"
    )

    print(
        "======================================"
    )

    print(
        "Reason: Independent calculation "
        "matches the AI-generated proof result."
    )

else:

    print(
        "\n======================================"
    )

    print(
        "STATUS: VERIFICATION FAILED"
    )

    print(
        "======================================"
    )

    print(
        "Reason: Independent calculation "
        "does not match the AI-generated proof result."
    )