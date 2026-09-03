/* Create tables */

CREATE TABLE IF NOT EXISTS web_sources (
   id_web_src SERIAL PRIMARY KEY,
   url TEXT UNIQUE,
   title TEXT
);

CREATE TABLE IF NOT EXISTS owner_contacts (
   id_owner_contact SERIAL PRIMARY KEY,
   profile_link TEXT UNIQUE,
   name TEXT,
   phone TEXT
);

CREATE TABLE IF NOT EXISTS raw_posts (
   id_raw_post SERIAL PRIMARY KEY,
   id_web_src INTEGER REFERENCES web_sources(id_web_src),
   id_owner_contact INTEGER REFERENCES owner_contacts(id_owner_contact),
   post_link TEXT UNIQUE,
   raw_text TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS cars (
   id_car SERIAL PRIMARY KEY,
   id_raw_post INTEGER REFERENCES raw_posts(id_raw_post),
   brand TEXT,
   model TEXT NOT NULL,
   trim TEXT,
   year INTEGER NOT NULL,
   transmission TEXT,
   km INTEGER,
   color TEXT,
   condition TEXT,
   owners INTEGER,
   price INTEGER NOT NULL,
   location TEXT
);

CREATE TABLE IF NOT EXISTS cars_images (
   id_img SERIAL PRIMARY KEY,
   id_raw_post INTEGER REFERENCES raw_posts(id_raw_post),
   img_1 BYTEA,
   img_2 BYTEA,
   img_3 BYTEA,
   img_4 BYTEA,
   img_5 BYTEA
);

-- Paginas fuente preconfiguradas
INSERT INTO web_sources (url, title) VALUES ('https://www.facebook.com/groups/2802491423342198?locale=es_LA', 'Autos en Venta Querétaro');
INSERT INTO web_sources (url, title) VALUES ('https://www.facebook.com/groups/1712927538960670?locale=es_LA', 'venta y cambio de autos Querétaro (particulares). no coyotes .');
INSERT INTO web_sources (url, title) VALUES ('https://www.facebook.com/groups/AUTOSencalientequeretaro?locale=es_LA', 'TIANGUIS DE AUTOS QUERETARO');