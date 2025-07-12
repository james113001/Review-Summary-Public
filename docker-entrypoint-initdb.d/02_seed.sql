INSERT INTO users (email, password_hash, role) VALUES
('alice@example.com', 'hashed_password1', 'user'),
('bob@example.com', 'hashed_password2', 'user'),
('carol@example.com', 'hashed_password3', 'admin');

INSERT INTO product (name) VALUES
('A'), ('B'), ('C');

INSERT INTO tags (name) VALUES
('good');

INSERT INTO reviews (
    user_id, id, overall_rating,
    would_recommend, free_text, status
) VALUES
(1, 1, 5, TRUE, 'Amazing cant recommend enough.', 'approved'),
(2, 1, 3, FALSE, 'Very nice but hard to work with first time.', 'approved'),
(3, 2, 4, TRUE, 'Great but wish it could be softer', 'approved'),
(1, 3, 2, FALSE, 'Eh I didnt like how it fit me.', 'approved');

INSERT INTO review_tags (review_id, tag_id) VALUES
(1, 1),  -- review 1 tagged 'good'
