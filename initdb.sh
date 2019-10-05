#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<- EOSQL

      CREATE TABLE groups (
          id SERIAL PRIMARY KEY,
          name VARCHAR (50) DEFAULT 'My first group'::text,
          deleted BOOLEAN DEFAULT FALSE,
          tier INT DEFAULT 1
      );

      CREATE TABLE categories (
          id SERIAL PRIMARY KEY,
          name VARCHAR (50),
          parent VARCHAR (50)
      );

      CREATE TABLE users (
          id SERIAL PRIMARY KEY,
          first VARCHAR (50) DEFAULT ''::text,
          last VARCHAR (50) DEFAULT ''::text,
          email VARCHAR (50),
          deleted BOOLEAN DEFAULT FALSE
      );

      CREATE TABLE stores (
          id SERIAL PRIMARY KEY,
          name VARCHAR (50),
          entity VARCHAR (50),
          city VARCHAR (50),
          deleted BOOLEAN DEFAULT FALSE
      );

      CREATE TABLE expenses(
         id SERIAL PRIMARY KEY,
         date DATE,
         user_id BIGINT,
         category BIGINT,
         amount REAL,
         store BIGINT,
         group_id BIGINT,
         deleted BOOLEAN DEFAULT FALSE,
         notes VARCHAR (140),
         mod_timestamp timestamp NOT NULL DEFAULT NOW(),
         mod_user BIGINT,
         root_id BIGINT,
         FOREIGN KEY (group_id) REFERENCES groups(id),
         FOREIGN KEY (category) REFERENCES categories(id),
         FOREIGN KEY (store) REFERENCES stores(id),
         FOREIGN KEY (root_id) REFERENCES expenses(id)
      );

      CREATE TABLE users_groups (
          user_id BIGINT NOT NULL,
          group_id BIGINT NOT NULL,
          admin BOOLEAN DEFAULT FALSE,
          PRIMARY KEY (user_id, group_id),
          FOREIGN KEY (user_id) REFERENCES users(id),
          FOREIGN KEY (group_id) REFERENCES groups(id)
      );

EOSQL
