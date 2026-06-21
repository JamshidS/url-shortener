CREATE SEQUENCE url_shortener.public.url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE url_shortener.public.urls (
    id INT PRIMARY KEY DEFAULT nextval('url_shortener.public.url_id_seq'),
    original_url VARCHAR,
    short_code VARCHAR,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN
);