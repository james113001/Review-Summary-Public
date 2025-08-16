-- 1. Enum for review status
CREATE TYPE review_status AS ENUM ('approved', 'pending', 'rejected');

-- 2. Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Product
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Reviews
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES product(id),
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    would_recommend BOOLEAN,
    free_text TEXT,
    status review_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tags
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE review_tags (
    review_id INTEGER REFERENCES reviews(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (review_id, tag_id)
);

-- 6. Most Common Tags
CREATE VIEW tag_usage_counts AS
SELECT
    t.id AS tag_id,
    t.name AS tag_name,
    COUNT(rt.review_id) AS usage_count
FROM tags t
LEFT JOIN review_tags rt ON t.id = rt.tag_id
GROUP BY t.id, t.name
ORDER BY usage_count DESC;
