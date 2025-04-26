CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    keywords TEXT[] NOT NULL  # Массив ключевых слов
);
CREATE INDEX idx_keywords ON urls USING GIN(keywords)