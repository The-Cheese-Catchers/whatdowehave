DROP TABLE IF EXISTS tbl_users;
CREATE TABLE tbl_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username VARCHAR(255) NOT NULL, 
                password VARCHAR(255) NOT NULL
            );
INSERT INTO tbl_users (id, username, password) VALUES (1, 'admin', 'admin');

DROP TABLE IF EXISTS tbl_pantry;
CREATE TABLE tbl_pantry (
                id INTEGER, 
                user_id INTEGER REFERENCES tbl_users(id), 
                quantity INTEGER NOT NULL, 
                ingredient_id INTEGER NOT NULL REFERENCES tbl_ingregients(id),
                PRIMARY KEY (id, ingredient_id)
            );
INSERT INTO tbl_pantry (id, user_id, quantity, ingredient_id) VALUES (1, 1, 1, 1);
INSERT INTO tbl_pantry (id, user_id, quantity, ingredient_id) VALUES (1, 1, 2, 3);
INSERT INTO tbl_pantry (id, user_id, quantity, ingredient_id) VALUES (1, 1, 5, 2);

DROP TABLE IF EXISTS tbl_recipes;
CREATE TABLE tbl_recipes (
                id INTEGER, 
                name VARCHAR(255) NOT NULL, 
                quantity INTEGER NOT NULL, 
                ingredient_id INTEGER NOT NULL REFERENCES tbl_ingregients(id),
                image VARBINARY(MAX),
                PRIMARY KEY (id, ingredient_id)
            );
INSERT INTO tbl_recipes (id, name, quantity, ingredient_id) VALUES (1, 'spanish omelette', 1, 1);
INSERT INTO tbl_recipes (id, name, quantity, ingredient_id) VALUES (1, 'spanish omelette', 1, 3);
INSERT INTO tbl_recipes (id, name, quantity, ingredient_id) VALUES (1, 'spanish omelette', 6, 2);

DROP TABLE IF EXISTS tbl_ingredients;
CREATE TABLE tbl_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                class VARCHAR(255) NOT NULL, 
                name VARCHAR(255) NOT NULL, 
                subtype VARCHAR(255) NOT NULL
            );
INSERT INTO tbl_ingredients (id, class, name, subtype) VALUES (1, 'vegetable', 'potato', 'russet');
INSERT INTO tbl_ingredients (id, class, name, subtype) VALUES (2, 'animal product', 'eggs', '');
INSERT INTO tbl_ingredients (id, class, name, subtype) VALUES (3, 'vegetable', 'onion', 'white');