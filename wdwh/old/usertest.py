import sqlite3
from sqlite3 import Error
from venv import create

def create_connection(db_file):
    cnxn = None
    print("Connecting to database ...")
    try:
        cnxn = sqlite3.connect(db_file)
        print("Connected.\n")
        return cnxn
    except Error as e:
        print(e)

def execute_initial_db(file):
    f = open(file)
    cnxn = create_connection("test.db")
    cur = cnxn.cursor()
    sql = f.read()
    cur.executescript(sql)
    cnxn.commit()
    cnxn.close()

if __name__ == "__main__":
    cnxn = create_connection("test.db")
    cur = cnxn.cursor()
    
    execute_initial_db("initial.sql")
    
    print("Hello!\nEnter:\n\t'login' to log in to your account,\n\t'create' to create a new account,\n\tor 'quit' to quit.\n")
    
    while True:
        action = input("> ")
        if action == "login":
            # ENTER LOGIN CREDENTIALS
            uname = input("Username > ")
            pwd = input("Password > ")
            print()
            # CHECK IF CREDENTIALS ARE VALID
            cur.execute(f"SELECT password FROM tbl_users WHERE username = '{uname}';")
            data = cur.fetchall()
            if len(data[0]) > 0:
                if data[0][0] != pwd:
                    print("Incorrect password, try again.")
                    continue
                else:
                    break
            else:
                print("This user does not exist, try again.")
                continue
        elif action == "create":
            # CREATE LOGIN CREDENTIALS
            uname = input("Enter a username > ")
            pwd = input("Enter a password > ")
            print()
            cur.execute(f"INSERT INTO tbl_users (username, password) VALUES ('{uname}', '{pwd}');")
            cnxn.commit()
        elif action == "quit":
            print("Exiting. Thanks for visiting!")
            exit()
        else:
            print("Unknown command.")
    
    # SAVE USER ID FOR FUTURE USE
    cur.execute(f"SELECT id FROM tbl_users WHERE username = '{uname}';")
    data = cur.fetchall()
    id = data[0][0]
    print("Login successful.")
    
    # OTHERWISE, DISPLAY USER'S PANTRY
    cur.execute(f""" SELECT i.name, p.quantity FROM (tbl_pantry AS p
                    JOIN tbl_users AS u
                    ON p.user_id = u.id)
                    JOIN tbl_ingredients AS i
                    ON p.ingredient_id = i.id
                    WHERE u.id = '{id}';
                """)
    my_pantry = cur.fetchall()
    print()
    print("Your pantry:")
    for t in my_pantry:
        print(t)
    print()
    
    cur.execute(f""" WITH my_pantry AS (
                    SELECT * FROM tbl_pantry
                    WHERE user_id = {id}
                    )
                    SELECT r.name, i.name, r.quantity, mp.quantity
                    FROM (tbl_recipes AS r
                    JOIN tbl_ingredients AS i
                    ON r.ingredient_id = i.id)
                    JOIN my_pantry AS mp
                    ON (r.ingredient_id = mp.ingredient_id
                    and mp.quantity < r.quantity);
                """)
    data = cur.fetchall()
    for t in data:
        print(f"Cannot make {t[0]}, conflicting ingredient: {t[1]}, {t[2]} required, only {t[3]} in pantry.")
    
    cnxn.close()