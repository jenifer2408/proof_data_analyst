import streamlit as st
import pandas as pd
from openai import OpenAI
import re


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VERITAS",
    page_icon="◈",
    layout="wide"
)


# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    font-size: 18px;
    color: #9ca3af;
    margin-bottom: 30px;
}

.verified {
    padding: 20px;
    border-radius: 12px;
    background-color: #12351f;
    border: 1px solid #2e8b57;
    font-size: 22px;
    font-weight: 700;
}

.failed {
    padding: 20px;
    border-radius: 12px;
    background-color: #3a1717;
    border: 1px solid #d9534f;
    font-size: 22px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

sales_df = pd.read_csv("data/superstore.csv")
customer_df = pd.read_csv("data/customer_registry.csv")

with open("audit_rules.txt", "r", encoding="utf-8") as file:
    rules = file.read()


# =========================================================
# OPENAI
# =========================================================

client = OpenAI()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">◈ VERITAS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Proof-Carrying AI Data Analyst — "
    "Don't just trust the answer. Verify it."
    "</div>",
    unsafe_allow_html=True
)


# =========================================================
# DATA HEALTH
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Records",
        len(sales_df)
    )

with col2:
    st.metric(
        "Duplicates",
        int(sales_df.duplicated().sum())
    )

with col3:
    st.metric(
        "Missing Values",
        int(sales_df.isna().sum().sum())
    )

with col4:
    st.metric(
        "Negative Quantity",
        int((sales_df["Quantity"] < 0).sum())
    )

st.divider()


# =========================================================
# QUESTION
# =========================================================

st.subheader("Ask VERITAS")

question = st.text_area(
    "Enter your data question",
    placeholder="Example: What is the total sales?",
    height=100
)

analyze = st.button(
    "🔍 ANALYZE",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze:

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        # =================================================
        # AI PROMPT
        # =================================================

        prompt = f"""
You are VERITAS, a Proof-Carrying AI Data Analyst.

USER QUESTION:
{question}

AVAILABLE DATAFRAMES:

DATAFRAME 1: sales_df
Columns:
{list(sales_df.columns)}

DATAFRAME 2: customer_df
Columns:
{list(customer_df.columns)}

AUDIT RULES:
{rules}

Generate Python code to answer the user's question.

IMPORTANT RULES:

1. Use only these existing DataFrames:

   sales_df
   customer_df

2. Do not import libraries.

3. Do not read files.

4. Do not access the internet.

5. Do not use:

   os
   sys
   subprocess
   eval
   exec
   open

6. Follow the audit rules.

7. ORDINARY TOTAL SALES:

   If the question asks:

   "What is the total sales?"

   or asks for total sales without another qualification,

   YOU MUST CALCULATE THE ANSWER.

   Do NOT return INSUFFICIENT_DATA.

   Do NOT ask for clarification.

   Do NOT use customer_df.

   Use:

   sales_clean = sales_df.drop_duplicates().copy()

   sales_clean = sales_clean[
       sales_clean["Sales"].notna()
   ]

   sales_clean = sales_clean[
       sales_clean["Quantity"].isna()
       | (sales_clean["Quantity"] >= 0)
   ]

   answer = sales_clean["Sales"].sum()


8. HIGH-RISK CUSTOMERS:

   Do NOT apply the High-risk exclusion to ordinary
   total-sales questions.

   Apply the High-risk rule ONLY when the question
   specifically concerns:

   - high-risk customers
   - corporate financial liability summaries


9. CUSTOMER QUESTIONS:

   If customer information is required, join:

   sales_df
   customer_df

   using:

   Customer ID


10. REGION QUESTIONS:

   If the question asks:

   "Which region has the highest sales?"

   calculate:

   sales_clean = sales_df.drop_duplicates().copy()

   sales_clean = sales_clean[
       sales_clean["Sales"].notna()
   ]

   sales_clean = sales_clean[
       sales_clean["Quantity"].isna()
       | (sales_clean["Quantity"] >= 0)
   ]

   region_sales = (
       sales_clean
       .groupby("Region")["Sales"]
       .sum()
       .sort_values(ascending=False)
   )

   answer = region_sales.index[0]


11. OTHER QUESTIONS:

   Use the available data and follow the audit rules.


12. AMBIGUOUS QUESTIONS:

   If the question genuinely cannot be interpreted reliably:

   answer = None
   reason = "CLARIFICATION_REQUIRED"


13. INSUFFICIENT DATA:

   If the available data genuinely cannot answer the question:

   answer = None
   reason = "INSUFFICIENT_DATA"


14. Do not claim insufficient data when the requested
    information exists in the available DataFrames.


15. Store the final result in:

   answer


16. Print the answer.


17. Return ONLY executable Python code.

Do not return markdown.
Do not explain the code.
"""


        # =================================================
        # AI GENERATION
        # =================================================

        with st.spinner("Generating proof code..."):

            try:

                response = client.responses.create(
                    model="gpt-6-luna",
                    input=prompt
                )

                generated_code = response.output_text

            except Exception as e:

                st.error(
                    f"AI generation failed: {e}"
                )

                st.stop()


        # =================================================
        # CLEAN AI CODE
        # =================================================

        generated_code = re.sub(
            r"```python",
            "",
            generated_code
        )

        generated_code = re.sub(
            r"```",
            "",
            generated_code
        )

        generated_code = generated_code.strip()


        # =================================================
        # SAFETY VALIDATION
        # =================================================

        blocked = [
            "import ",
            "from ",
            "os.",
            "sys.",
            "subprocess",
            "eval(",
            "exec(",
            "open(",
            "__"
        ]

        unsafe_item = None

        for item in blocked:

            if item in generated_code:

                unsafe_item = item
                break


        if unsafe_item:

            st.error(
                f"❌ Code rejected for safety: {unsafe_item}"
            )

        else:

            # =================================================
            # VERIFICATION PIPELINE
            # =================================================

            st.subheader(
                "Verification Pipeline"
            )

            progress = st.empty()

            progress.info(
                "✓ AI code generated"
            )


            # =================================================
            # EXECUTION NAMESPACE
            # =================================================

            execution_namespace = {
                "sales_df": sales_df,
                "customer_df": customer_df
            }


            # =================================================
            # SAFE BUILTINS
            # =================================================

            safe_builtins = {
                "print": print,
                "len": len,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "all": all,
                "any": any,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "range": range,
                "sorted": sorted,
                "zip": zip,
                "enumerate": enumerate,
                "isinstance": isinstance
            }


            # =================================================
            # EXECUTE PROOF
            # =================================================

            try:

                exec(
                    generated_code,
                    {
                        "__builtins__": safe_builtins
                    },
                    execution_namespace
                )

                answer = execution_namespace.get(
                    "answer"
                )

                reason = execution_namespace.get(
                    "reason"
                )

                progress.info(
                    "✓ AI code generated  →  "
                    "✓ Code executed"
                )

            except Exception as e:

                st.error(
                    f"❌ Proof execution failed: {e}"
                )

                answer = None
                reason = "EXECUTION_ERROR"


            # =================================================
            # HANDLE REFUSAL / CLARIFICATION
            # =================================================

            if answer is None:

                if reason == "CLARIFICATION_REQUIRED":

                    st.warning(
                        "⚠ VERITAS needs clarification "
                        "before calculating a reliable answer."
                    )

                elif reason == "INSUFFICIENT_DATA":

                    st.warning(
                        "⚠ VERITAS cannot reliably answer "
                        "this question from the available data."
                    )

                else:

                    st.warning(
                        f"⚠ {reason}"
                    )


            # =================================================
            # VALID ANSWER
            # =================================================

            else:

                # =================================================
                # ANSWER
                # =================================================

                st.subheader("Answer")

                if isinstance(answer, (int, float)):

                    st.metric(
                        "Candidate Result",
                        f"{float(answer):,.2f}"
                    )

                else:

                    st.metric(
                        "Candidate Result",
                        str(answer)
                    )


                # =================================================
                # INDEPENDENT VERIFICATION
                # =================================================

                progress.info(
                    "✓ Code executed  →  "
                    "🔍 Independently verifying..."
                )

                question_lower = question.lower()


                # =================================================
                # VERIFIER 1:
                # TOTAL SALES
                # =================================================

                if "total sales" in question_lower:

                    verified_df = (
                        sales_df
                        .drop_duplicates()
                        .copy()
                    )

                    verified_df = verified_df[
                        verified_df["Sales"].notna()
                    ].copy()

                    verified_df = verified_df[
                        verified_df["Quantity"].isna()
                        |
                        (verified_df["Quantity"] >= 0)
                    ].copy()

                    verified_answer = (
                        verified_df["Sales"].sum()
                    )

                    difference = abs(
                        verified_answer
                        -
                        float(answer)
                    )

                    verification_passed = (
                        difference < 0.000001
                    )

                    verification_type = "numeric"


                # =================================================
                # VERIFIER 2:
                # HIGHEST SALES REGION
                # =================================================

                elif (
                    "highest sales" in question_lower
                    and "region" in question_lower
                ):

                    verified_df = (
                        sales_df
                        .drop_duplicates()
                        .copy()
                    )

                    verified_df = verified_df[
                        verified_df["Sales"].notna()
                    ].copy()

                    verified_df = verified_df[
                        verified_df["Quantity"].isna()
                        |
                        (verified_df["Quantity"] >= 0)
                    ].copy()

                    region_sales = (
                        verified_df
                        .groupby("Region")["Sales"]
                        .sum()
                        .sort_values(
                            ascending=False
                        )
                    )

                    verified_answer = (
                        region_sales.index[0]
                    )

                    verification_passed = (
                        str(answer).strip().lower()
                        ==
                        str(verified_answer).strip().lower()
                    )

                    difference = None

                    verification_type = "text"


                # =================================================
                # VERIFIER 3:
                # HIGH-RISK CUSTOMER SALES
                # =================================================

                elif (
                    "high-risk" in question_lower
                    or "high risk" in question_lower
                ):

                    # ---------------------------------------------
                    # Clean transaction data
                    # ---------------------------------------------

                    verified_sales = (
                        sales_df
                        .drop_duplicates()
                        .copy()
                    )

                    verified_sales = verified_sales[
                        verified_sales["Customer ID"].notna()
                    ].copy()

                    verified_sales = verified_sales[
                        verified_sales["Sales"].notna()
                    ].copy()

                    verified_sales = verified_sales[
                        verified_sales["Quantity"].isna()
                        |
                        (verified_sales["Quantity"] >= 0)
                    ].copy()


                    # ---------------------------------------------
                    # Clean customer registry
                    # ---------------------------------------------

                    verified_registry = (
                        customer_df
                        .drop_duplicates()
                        .copy()
                    )


                    # ---------------------------------------------
                    # Customer IDs must be unique
                    # ---------------------------------------------

                    if verified_registry[
                        "Customer ID"
                    ].duplicated().any():

                        verification_passed = False
                        verification_type = "failed"
                        verified_answer = None
                        difference = None

                    else:

                        # -----------------------------------------
                        # Independent multi-table join
                        # -----------------------------------------

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


                        # -----------------------------------------
                        # Select HIGH-risk customers
                        # -----------------------------------------

                        high_risk_df = verified_joined[
                            verified_joined["Risk Level"]
                            .astype("string")
                            .str.strip()
                            .str.upper()
                            == "HIGH"
                        ].copy()


                        # -----------------------------------------
                        # Currency normalization
                        # -----------------------------------------

                        high_risk_df["Currency Unit"] = (
                            high_risk_df["Currency Unit"]
                            .astype("string")
                            .str.strip()
                            .str.upper()
                        )


                        # -----------------------------------------
                        # Operational exchange rates
                        # -----------------------------------------

                        exchange_rates = {
                            "USD": 1.0,
                            "EUR": 1.12
                        }


                        high_risk_df["Exchange Rate"] = (
                            high_risk_df["Currency Unit"]
                            .map(exchange_rates)
                        )


                        # -----------------------------------------
                        # Check currency validity
                        # -----------------------------------------

                        if high_risk_df[
                            "Exchange Rate"
                        ].isna().any():

                            verification_passed = False
                            verification_type = "failed"
                            verified_answer = None
                            difference = None

                        else:

                            # -------------------------------------
                            # Independent calculation
                            # -------------------------------------

                            verified_answer = (
                                high_risk_df["Sales"]
                                *
                                high_risk_df["Exchange Rate"]
                            ).sum()

                            difference = abs(
                                verified_answer
                                -
                                float(answer)
                            )

                            verification_passed = (
                                difference < 0.000001
                            )

                            verification_type = "numeric"


                # =================================================
                # UNSUPPORTED QUESTION
                # =================================================

                else:

                    verification_passed = False
                    verified_answer = None
                    difference = None
                    verification_type = "unsupported"


                # =================================================
                # DISPLAY VERIFICATION RESULT
                # =================================================

                if verification_passed:

                    progress.success(
                        "✓ AI proof executed  →  "
                        "✓ Independent verification passed"
                    )

                    st.markdown(
                        '<div class="verified">'
                        "🟢 VERIFIED"
                        "</div>",
                        unsafe_allow_html=True
                    )


                    # -------------------------------------------------
                    # NUMERIC RESULT
                    # -------------------------------------------------

                    if verification_type == "numeric":

                        col_a, col_b = st.columns(2)

                        with col_a:

                            st.metric(
                                "AI Proof Result",
                                f"{float(answer):,.2f}"
                            )

                        with col_b:

                            st.metric(
                                "Independent Result",
                                f"{float(verified_answer):,.2f}"
                            )

                        st.write(
                            "Difference:",
                            f"{difference:.10f}"
                        )


                    # -------------------------------------------------
                    # TEXT RESULT
                    # -------------------------------------------------

                    elif verification_type == "text":

                        col_a, col_b = st.columns(2)

                        with col_a:

                            st.metric(
                                "AI Proof Result",
                                str(answer)
                            )

                        with col_b:

                            st.metric(
                                "Independent Result",
                                str(verified_answer)
                            )

                        st.write(
                            "Match:",
                            "Exact"
                        )


                # =================================================
                # UNSUPPORTED VERIFICATION
                # =================================================

                elif verification_type == "unsupported":

                    progress.warning(
                        "⚠ Answer generated, but an independent "
                        "verifier for this question type is "
                        "not available yet."
                    )

                    st.warning(
                        "⚠ NOT VERIFIED — "
                        "No suitable independent verification "
                        "rule exists for this question yet."
                    )


                # =================================================
                # VERIFICATION FAILURE
                # =================================================

                else:

                    progress.error(
                        "✗ Independent verification failed"
                    )

                    st.markdown(
                        '<div class="failed">'
                        "🔴 VERIFICATION FAILED"
                        "</div>",
                        unsafe_allow_html=True
                    )

                    st.write(
                        "AI result:",
                        answer
                    )

                    if verified_answer is not None:

                        st.write(
                            "Independent result:",
                            verified_answer
                        )

                    if difference is not None:

                        st.write(
                            "Difference:",
                            difference
                        )


                # =================================================
                # PROOF CODE
                # =================================================

                with st.expander(
                    "🐍 View Executable Proof"
                ):

                    st.code(
                        generated_code,
                        language="python"
                    )


                # =================================================
                # DATA EVIDENCE
                # =================================================

                with st.expander(
                    "🔍 View Data Evidence"
                ):

                    st.write(
                        "Source dataset:",
                        "superstore.csv"
                    )

                    st.write(
                        "Total records:",
                        len(sales_df)
                    )

                    st.write(
                        "Exact duplicate records:",
                        int(
                            sales_df
                            .duplicated()
                            .sum()
                        )
                    )

                    st.write(
                        "Missing Sales:",
                        int(
                            sales_df["Sales"]
                            .isna()
                            .sum()
                        )
                    )

                    st.write(
                        "Negative Quantity records:",
                        int(
                            (sales_df["Quantity"] < 0)
                            .sum()
                        )
                    )

                    st.write(
                        "Missing values overall:",
                        int(
                            sales_df
                            .isna()
                            .sum()
                            .sum()
                        )
                    )