import psycopg2
from ollama import chat
from ollama import ChatResponse
from dotenv import load_dotenv
import os

load_dotenv()

# ------------------------------------
# CONFIGURATION
# ------------------------------------
DB_HOST = 'localhost'
DB_PORT = 15432
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

ID = 1  # Example to summarize

# ------------------------------------
# 1. Connect to Postgres
# ------------------------------------
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# ------------------------------------
# 2. Fetch Reviews
# ------------------------------------
cur.execute("""
    SELECT free_text
    FROM reviews
    WHERE id = %s AND status = 'approved'
""", (ID,))
rows = cur.fetchall()

if not rows:
    print("No reviews found!")
    exit()

reviews = [row[0] for row in rows]

# ------------------------------------
# 3. Build Prompt
# ------------------------------------
prompt = "Summarize the following reviews from the perspective of [omitted]:\n\n"
for r in reviews:
    prompt += f"- {r}\n"

prompt += "\nReturn a clear, short, and honest summary."

print("\n--- Prompt Sent to Mistral ---")
print(prompt)

# ------------------------------------
# 4. Call Ollama
# ------------------------------------
try:
    response: ChatResponse = chat(
        model='mistral',
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
except Exception as e:
    print("Error during Ollama chat:", e)
    exit(1)

summary = response['message']['content']

print("\n--- SUMMARY ---")
print(summary)

# ------------------------------------
# 5. Optionally store back in DB
# ------------------------------------
# Example: write it to a summaries table
# (You'll need to create this table first if you want.)
#
# cur.execute("""
#     INSERT INTO summaries (id, summary_text)
#     VALUES (%s, %s)
# """, (ID, summary))
# conn.commit()

# ------------------------------------
# 6. Clean up
# ------------------------------------
cur.close()
conn.close()
