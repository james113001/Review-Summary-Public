from fastapi import FastAPI, HTTPException
from app.db import get_connection
from app.summarize_reviews import summarize_reviews
from pydantic import BaseModel, conint
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI()


class ReviewStatus(str, Enum):
    approved = 'approved'
    pending = 'pending'
    rejected = 'rejected'


# Models
class User(BaseModel):
    email: str
    password_hash: str
    created_at: Optional[datetime] = None


class Product(BaseModel):
    name: str
    created_at: Optional[datetime] = None


class Review(BaseModel):
    user_id: int
    product_id: int
    overall_rating: conint(ge=1, le=5)
    would_recommend: bool
    free_text: Optional[str] = None
    status: ReviewStatus = ReviewStatus.pending
    created_at: Optional[datetime] = None


class Tag(BaseModel):
    name: str


class ReviewTags(BaseModel):
    review_id: int
    tag_ids: List[int]


@app.get("/")
def root():
    return {"message": "API is working"}


#### GET Endpoints -------------------------------
@app.get("/users")
def get_users():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, created_at FROM users")
            users = cur.fetchall()
        return [{"id": u[0], "email": u[1], "created_at": u[2]} for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/products")
def get_products():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM product")
            products = cur.fetchall()
        return [{"id": p[0], "name": p[1], "created_at": p[2]} for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/reviews/{product_id}")
def get_reviews(product_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, user_id, overall_rating, would_recommend, free_text, created_at
                FROM reviews
                WHERE product_id = %s AND status = 'approved'
            """, (product_id,))
            reviews = cur.fetchall()
        return [
            {
                "id": r[0],
                "user_id": r[1],
                "overall_rating": r[2],
                "would_recommend": r[3],
                "free_text": r[4],
                "created_at": r[5]
            }
            for r in reviews
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/tags")
def get_tags():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM tags")
            tags = cur.fetchall()
        return [{"id": t[0], "name": t[1]} for t in tags]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/review-tags/{review_id}")
def get_review_tags(review_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.name
                FROM review_tags rt
                JOIN tags t ON rt.tag_id = t.id
                WHERE rt.review_id = %s
            """, (review_id,))
            tags = cur.fetchall()
        return [{"id": t[0], "name": t[1]} for t in tags]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


#### INSERT Endpoints -------------------------------
@app.post("/users/")
def create_user(user: User):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, created_at",
                (user.email, user.password_hash)
            )
            user_id, created_at = cur.fetchone()
            conn.commit()
        return {"id": user_id, "created_at": created_at}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.post("/products/")
def create_product(product: Product):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO product (name) VALUES (%s) RETURNING id",
                (product.name,)
            )
            product_id = cur.fetchone()[0]
            conn.commit()
        return {"id": product_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.post("/reviews/")
def create_review(review: Review):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reviews (
                    user_id, product_id, overall_rating, would_recommend, free_text, status
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                review.user_id, review.product_id, review.overall_rating,
                review.would_recommend, review.free_text, review.status
            ))
            review_id = cur.fetchone()[0]
            conn.commit()
        return {"id": review_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.post("/tags/")
def create_tag(tag: Tag):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tags (name) VALUES (%s) RETURNING id", (tag.name,))
            tag_id = cur.fetchone()[0]
            conn.commit()
        return {"id": tag_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.post("/review-tags/")
def create_review_tags(review_tags: ReviewTags):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for tag_id in review_tags.tag_ids:
                cur.execute(
                    "INSERT INTO review_tags (review_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (review_tags.review_id, tag_id)
                )
            conn.commit()
        return {"message": "Tags added to review"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


#### SUMMARIZE Endpoint ----------------------------
@app.get("/summarize/{product_id}")
def summarize_product(product_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1. Check if summary exists
        cur.execute("""
            SELECT summary_text, last_updated
            FROM product_summaries
            WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()

        if result:
            summary, last_updated = result
            return {"product_id": product_id, "summary": summary, "cached": True}

        # 2. Fetch reviews and generate summary
        cur.execute("""
            SELECT free_text
            FROM reviews
            WHERE product_id = %s AND status = 'approved'
        """, (product_id,))
        rows = cur.fetchall()
        reviews = [row[0] for row in rows]

        if not reviews:
            return {"product_id": product_id, "summary": "No reviews available.", "cached": False}

        summary = summarize_reviews(reviews)

        # 3. Store summary
        cur.execute("""
            INSERT INTO product_summaries (product_id, summary_text, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (product_id) DO UPDATE
            SET summary_text = EXCLUDED.summary_text,
                last_updated = EXCLUDED.last_updated
        """, (product_id, summary))
        conn.commit()
        return {"product_id": product_id, "summary": summary, "cached": False}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error summarizing product: {str(e)}")
    finally:
        conn.close()
