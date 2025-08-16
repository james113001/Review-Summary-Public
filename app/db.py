import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def insert_user(conn, email, password_hash, role='user'):
    """Insert a new user and return the user ID."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (email, password_hash, role, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id
        """, (email, password_hash, role))
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id

def insert_product(conn, name):
    """Insert a new product and return the product ID."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO product (name, created_at)
            VALUES (%s, NOW())
            RETURNING id
        """, (name,))
        product_id = cur.fetchone()[0]
        conn.commit()
        return product_id

def insert_review(conn, user_id, product_id, overall_rating, would_recommend, free_text=None, status='pending'):
    """Insert a review for a product."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO reviews (user_id, id, overall_rating, would_recommend, free_text, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (user_id, product_id, overall_rating, would_recommend, free_text, status))
        review_id = cur.fetchone()[0]
        conn.commit()
        return review_id

def insert_tag(conn, name):
    """Insert a tag, ignoring duplicates, and return its ID."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO tags (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """, (name,))
        result = cur.fetchone()
        if result:
            tag_id = result[0]
        else:
            cur.execute("SELECT id FROM tags WHERE name = %s", (name,))
            tag_id = cur.fetchone()[0]
        conn.commit()
        return tag_id

def insert_review_tags(conn, review_id, tag_ids):
    """Associate multiple tags with a review."""
    with conn.cursor() as cur:
        values = [(review_id, tag_id) for tag_id in tag_ids]
        execute_values(
            cur,
            "INSERT INTO review_tags (review_id, tag_id) VALUES %s ON CONFLICT DO NOTHING",
            values
        )
        conn.commit()
