#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<- EOSQL

      CREATE DATABASE housemate;

      \c housemate;

      /* Create tables */

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

      /* Create Views */

      /* cats */
      /* Formats category output as parent/name and returns with id */

      CREATE VIEW cats AS
      SELECT id AS category_id,
      CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category
      FROM categories;

      /* user_data */
      /* Confirms user is active and returns details */

      CREATE VIEW user_data AS
      SELECT id AS user_id, first, last, email
      FROM users
      WHERE deleted = 'f';

      /* user_groups */
      /* Returns groups that the user is a member of, a full list of active and
         inactive groups*/

      CREATE VIEW user_groups AS
      SELECT users.email, groups.id AS group_id, name, groups.deleted
      FROM groups
      INNER JOIN (SELECT * FROM users_groups) AS users_groups
        ON groups.id = users_groups.group_id
      INNER JOIN (SELECT id as user_id, email, deleted FROM users) AS users
        ON users_groups.user_id = users.user_id;

      /* group_users */
      /* Get a full list of members in a group, active and inactive */

      CREATE VIEW group_users AS
      SELECT users_groups.group_id, users_groups.user_id, users.first,
        users.last, users_groups.admin
      FROM users_groups
      INNER JOIN (SELECT * FROM users) AS users
        ON users_groups.user_id = users.id;

      /* group_expenses */
      /* Returns all of the group's non-deleted expenses */

      CREATE VIEW group_expenses AS
      SELECT expenses.id as id, to_char(expenses.date, 'YYYY-MM-DD') AS date,
        users.id AS user_id, expenses.amount, cat.id AS category_id, cat.category,
          stores.id AS store_id, stores.name AS store, expenses.notes, expenses.root_id,
          expenses.group_id
      FROM expenses
      LEFT JOIN (SELECT * FROM users) AS users
        ON expenses.user_id = users.id
      LEFT JOIN (SELECT id, CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category
        FROM categories) AS cat
        ON expenses.category = cat.id
      LEFT JOIN stores
        ON expenses.store = stores.id
      WHERE expenses.deleted='f'
      ORDER BY expenses.date DESC;

      /* month_user */
      /* Monthly summary of expenses per group user (need to do error control) */

      CREATE VIEW month_user AS
      SELECT expenses.group_id, to_char(expenses.date, 'YYYY-MM') AS month,
        users.first AS first, sum(expenses.amount)
      FROM expenses
      INNER JOIN (SELECT * FROM users_groups) AS users_groups
        ON expenses.group_id = users_groups.group_id
      INNER JOIN (SELECT * FROM users) AS users
        ON users_groups.user_id = users.id
      WHERE expenses.deleted ='f'
      GROUP BY expenses.group_id, month, users.first
      ORDER BY month;

      /* month_category */
      /* Return all expenses per category by month in group id (need to do error control) */

      CREATE VIEW month_category AS
      SELECT expenses.group_id, to_char(expenses.date, 'YYYY-MM') AS month,
        cat.category AS category, sum(expenses.amount)
      FROM expenses
      LEFT JOIN (SELECT id, CASE WHEN parent IS NULL THEN name ELSE CONCAT_WS('/', parent, name) END AS category FROM categories) AS cat
        ON expenses.category = cat.id
      WHERE expenses.deleted ='f'
      GROUP BY expenses.group_id, month, cat.category
      ORDER BY month

EOSQL
