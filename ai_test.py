from openai import OpenAI
import pandas as pd

client = OpenAI()

# Load both datasets
sales_df = pd.read_csv("data/superstore.csv")
customer_df = pd.read_csv("data/customer_registry.csv")

# Load audit rules
with open("audit_rules.txt", "r", encoding="utf-8") as file:
    rules = file.read()

# Question we want the AI to solve
question = "How much total Sales would be excluded from corporate financial liability summaries because the customers are classified as High risk?"

prompt = f"""
You are a Proof-Carrying Data Analyst.

The user asked:

{question}

You have access to TWO pandas DataFrames.

DATAFRAME 1: sales_df
This contains transaction/sales data.

Columns:
{list(sales_df.columns)}

DATAFRAME 2: customer_df
This contains customer registry information.

Columns:
{list(customer_df.columns)}

IMPORTANT AUDIT RULES:

{rules}

YOUR TASK:

Generate Python code that answers the user's question.

The code must:

1. Use only the existing DataFrames:
   - sales_df
   - customer_df

2. Follow ALL audit rules.

3. Join the datasets using:
   Customer ID

4. Handle missing values according to the audit rules.

5. Do not invent columns or data.

6. Do not import any libraries.

7. Do not access files.

8. Do not access the internet.

9. Do not use operating system commands.

10. Store the final numerical result in a variable called `answer`.

11. Print the answer.

Return ONLY executable Python code.

Do not explain the code.
"""

response = client.responses.create(
    model="gpt-6-luna",
    input=prompt
)

generated_code = response.output_text

print("\n========== AI GENERATED CODE ==========\n")
print(generated_code)