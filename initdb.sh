#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<- EOSQL

      CREATE TABLE expenses(
         id BIGINT PRIMARY KEY,
         date DATE,
         who BIGINT,
         category INT,
         amount REAL,
         store BIGINT,
         gid BIGINT,
         deleted BOOLEAN DEFAULT FALSE,
         notes VARCHAR (140),
         mod_timestamp TIMESTAMP,
         mod_user BIGINT,
         root_id BIGINT
      );
      CREATE SEQUENCE expenses_id_seq MINVALUE 1;
      ALTER TABLE expenses ALTER id SET DEFAULT nextval('expenses_id_seq');
      ALTER SEQUENCE expenses_id_seq OWNED BY expenses.id;



      CREATE TABLE exp_group (
          id BIGINT PRIMARY KEY,
          name VARCHAR (50) DEFAULT 'My first group'::text,
          deleted BOOLEAN DEFAULT FALSE,
          tier INT DEFAULT 1
      );
      CREATE SEQUENCE exp_group_id_seq MINVALUE 1;
      ALTER TABLE exp_group ALTER id SET DEFAULT nextval('exp_group_id_seq');
      ALTER SEQUENCE exp_group_id_seq OWNED BY exp_group.id;



      CREATE TABLE categories (
          id BIGINT PRIMARY KEY,
          name VARCHAR (50),
          parent VARCHAR (50)
      );
      CREATE SEQUENCE categories_id_seq MINVALUE 1;
      ALTER TABLE categories ALTER id SET DEFAULT nextval('categories_id_seq');
      ALTER SEQUENCE categories_id_seq OWNED BY categories.id;



      CREATE TABLE people (
          id BIGINT PRIMARY KEY,
          first VARCHAR (50) DEFAULT ''::text,
          last VARCHAR (50) DEFAULT ''::text,
          email VARCHAR (50),
          deleted BOOLEAN DEFAULT FALSE
      );
      CREATE SEQUENCE people_id_seq MINVALUE 1;
      ALTER TABLE people ALTER id SET DEFAULT nextval('people_id_seq');
      ALTER SEQUENCE people_id_seq OWNED BY people.id;



      CREATE TABLE stores (
          id BIGINT PRIMARY KEY,
          name VARCHAR (50),
          entity VARCHAR (50),
          city VARCHAR (50),
          deleted BOOLEAN DEFAULT FALSE
      );
      CREATE SEQUENCE stores_id_seq MINVALUE 1;
      ALTER TABLE stores ALTER id SET DEFAULT nextval('stores_id_seq');
      ALTER SEQUENCE stores_id_seq OWNED BY stores.id;



      CREATE TABLE user_group (
          id BIGINT PRIMARY KEY,
          uid BIGINT,
          gid BIGINT,
          admin BOOLEAN DEFAULT FALSE
      );
      CREATE SEQUENCE user_group_id_seq MINVALUE 1;
      ALTER TABLE user_group ALTER id SET DEFAULT nextval('user_group_id_seq');
      ALTER SEQUENCE user_group_id_seq OWNED BY user_group.id;

EOSQL
