from openai import OpenAI
import pandas as pd
import re

client = OpenAI()

# =========================================================
# LOAD DATA
# =========================================================

sales_df = pd.read_csv("data/superstore.csv")
customer_df = pd.read_csv("data/customer_registry.csv")

with open("audit_rules.txt", "r", encoding="utf-8") as file:
    rules = file.read()


# =========================================================
# ASK USER
# =========================================================

question = input("\nAsk VERITAS: ")


# =========================================================
# AI CODE GENERATION
# =========================================================

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

7. IMPORTANT:
   Do NOT apply the High-risk customer exclusion to ordinary
   "total sales" questions.

   The High-risk exclusion applies specifically to:
   "corporate financial liability summaries"

8. For:
   "What is the total sales?"

   Calculate total Sales from the sales transaction data.

   Apply relevant transaction-level data-quality rules such as:
   - identify/remove exact duplicate records
   - exclude missing Sales
   - flag/exclude negative Quantity records

   Do NOT join customer_df unless the question requires
   customer-level information.

9. If the question asks about high-risk customers,
   customer-level information, or corporate financial liability,
   then join sales_df with customer_df using Customer ID.

10. If the question is ambiguous, do NOT guess.

    Set:
    answer = None
    reason = "CLARIFICATION_REQUIRED"

11. If the available data cannot answer the question reliably:

    Set:
    answer = None
    reason = "INSUFFICIENT_DATA"

12. If the user asks which region has the highest sales,
    calculate Sales grouped by Region and return the region
    with the highest sales.

13. Store the final result in:

    answer

14. Print the answer.

15. If clarification or refusal is required, print the reason.

16. Return ONLY executable Python code.

Do not return markdown.
Do not explain the code.
"""


response = client.responses.create(
    model="gpt-6-luna",
    input=prompt
)

generated_code = response.output_text


# =========================================================
# CLEAN AI RESPONSE
# =========================================================

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


print("\n========== AI GENERATED CODE ==========\n")
print(generated_code)


# =========================================================
# BASIC CODE SAFETY CHECK
# =========================================================

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

for item in blocked:

    if item in generated_code:

        print("\n❌ CODE REJECTED")
        print("Blocked operation detected:", item)

        exit()


# =========================================================
# EXECUTE AI GENERATED PROOF
# =========================================================

print("\n========== EXECUTING PROOF ==========\n")

execution_namespace = {
    "sales_df": sales_df,
    "customer_df": customer_df
}


# Safe built-in functions
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


try:

    exec(
        generated_code,
        {
            "__builtins__": safe_builtins
        },
        execution_namespace
    )

    answer = execution_namespace.get("answer")
    reason = execution_namespace.get("reason")

except Exception as e:

    print("❌ Execution failed:")
    print(e)

    exit()


# =========================================================
# VERITAS RESULT
# =========================================================

print("\n========== VERITAS RESULT ==========")

if answer is None:

    print("Status: NEEDS ATTENTION")

    if reason:
        print("Reason:", reason)
    else:
        print("Reason: No reliable answer was produced.")

else:

    print("Answer:", answer)
    print("Proof executed successfully.")
# =========================================================
# SAVE RESULT FOR VERIFIER
# =========================================================

with open("verification_input.txt", "w", encoding="utf-8") as file:
    file.write(str(answer))

print("\nVerification input saved.")