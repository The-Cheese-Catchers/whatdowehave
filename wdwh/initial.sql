DROP TABLE IF EXISTS tbl_users;
CREATE TABLE tbl_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username VARCHAR(255) NOT NULL, 
                password VARCHAR(255) NOT NULL
            );
INSERT INTO tbl_users (id, username, password) VALUES (1, 'admin', 'admin');

DROP TABLE IF EXISTS tbl_ingredients;
CREATE TABLE tbl_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                ing_name VARCHAR(255) NOT NULL, 
                quantity INTEGER NOT NULL, 
                expr_date DATE
            );

DROP TABLE IF EXISTS tbl_recipes;
CREATE TABLE tbl_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                rec_name VARCHAR(255) NOT NULL, 
                instructions VARCHAR(255) NOT NULL, 
            );

DROP TABLE IF EXISTS tbl_pantry;
CREATE TABLE tbl_pantry (
                id INTEGER, 
                user_id INTEGER REFERENCES tbl_users(id), 
                ingredient_id INTEGER NOT NULL REFERENCES tbl_ingredients(id),
                PRIMARY KEY (id, user_id)
            );

DROP TABLE IF EXISTS tbl_ingredient_list;
CREATE TABLE tbl_ingredient_list (
                id INTEGER, 
                rec_id INTEGER NOT NULL REFERENCES tbl_recipes(id), 
                ingredient_id INTEGER NOT NULL REFERENCES tbl_ingredients(id),
                PRIMARY KEY (id, rec_id)
            );

DROP TABLE IF EXISTS tbl_cookbook;
CREATE TABLE tbl_cookbook (
                id INTEGER, 
                rec_id INTEGER NOT NULL REFERENCES tbl_recipes(id), 
                user_id INTEGER NOT NULL REFERENCES tbl_users(id),
                PRIMARY KEY (id, user_id)
            );

