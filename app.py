# IMPORTING ALL THE NEEDED MODULES
import hmac
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# INITIATING OBJECT CALLED USER AND ADDING PARAMS
class User(object):
    def __init__(self, id_num, username, password):
        self.id = id_num
        self.username = username
        self.password = password


# CREATING USER TABLE
def create_user_table():
    with sqlite3.connect('book_db.db') as conn:
        conn.execute('Create TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                     'first_name TEXT NOT NULL,'
                     'last_name TEXT NOT NULL,'
                     'email_address VARCHAR NOT NULL,'
                     'password VARCHAR NOT NULL)')

    print('Successfully Created User Table')


# CREATING BOOK TABLE
def create_book_table():
    with sqlite3.connect('book_db.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS book(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                     'name TEXT NOT NULL,'
                     'img_url TEXT NOT NULL,'
                     'description VARCHAR NOT NULL,'
                     'price VARCHAR NOT NULL,'
                     'category TEXT NOT NULL)')

        print('Successfully Created Book Table')


# GETTING USER ID, USERNAME AND PASSWORD FROM USER TABLE
# def fetch_users():
#     with sqlite3.connect('book_db.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM user")
#         users = cursor.fetchall()
#
#         new_data = []
#
#         for data in users:
#             # print(User(data[0], data[3], data[6]))
#             print(data)
#             new_data.append(User(data[0], data[3], data[6]))
#     return new_data


# AUTHENTICATION
# def authenticate(username, password):
#     user = username_table.get(username, None)
#     if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
#         return user

#
# def identity(payload):
#     user_id = payload['identity']
#     return userid_table.get(user_id, None)


# INITIALISING FLASK APP AND DEBUGGING
app = Flask(__name__)
app.debug = True

# USING FLASK MAIL TO SEND EMAILS
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottoarj@gmail.com'
app.config['MAIL_PASSWORD'] = 'lottoarj123!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

CORS(app)

create_user_table()
create_book_table()
# users = fetch_users()

# username_table = {u.username: u for u in users}
# userid_table = {u.id: u for u in users}


# CREATING APP ROUTE AND FUNCTION FOR USER REGISTRATION
@app.route('/user-registration/', methods=["GET", "POST", "PATCH"])
def user_registration():
    response = {}

    if request.method == "GET":
        with sqlite3.connect("book_db.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")

            users = cursor.fetchall()

            response["status_code"] = 200
            response["data"] = users
            return response

    if request.method == "PATCH":
        email_address = request.json["email_address"]
        password = request.json["password"]

        with sqlite3.connect("book_db.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email_address=? AND password=?", (email_address, password))

            users = cursor.fetchone()

        response["status_code"] = 200
        response["data"] = users
        return response

    if request.method == "POST":
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        password = request.json['password']
        email_address = request.json['email_address']

        with sqlite3.connect("book_db.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO user( first_name, last_name, password, email_address )"
                           f"VALUES('{first_name}', '{last_name}', '{password}', '{email_address}')")
            conn.commit()

            response["message"] = "register success"
            response["status_code"] = 201

            # if response["status_code"] == 201:
            #     msg = Message('Success!', sender='lottoarj@gmail.com', recipients=[email_address])
            #     msg.body = "Your Registration was Successful!"
            #     mail.send(msg)
            #     return "Message Sent"

        return response


# FUNCTION TO ADD BOOKS
@app.route('/add-book/', methods=["POST"])
def add_book():
    response = {}

    if request.method == "POST":
        name = request.json['name']
        img_url = request.json['img_url']
        description = request.json['description']
        price = request.json['price']
        category = request.json['category']

        with sqlite3.connect("book_db.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO book( name, img_url, description, price, category )"
                           f'VALUES("{name}", "{img_url}", "{description}", "{price}", "{category}")')
            conn.commit()

            response["description"] = "add success"
            response["status_code"] = 201

        return response


# FUNCTION TO DELETE BOOKS
@app.route('/delete-book/<int:post_id>/', methods=["GET"])
def delete_book(post_id):
    response = {}
    with sqlite3.connect("book_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM book WHERE id={str(post_id)}")
        conn.commit()

        response["status_code"] = 200
        response["message"] = "Product Deleted Successfully"

    return response


# FUNCTION TO SHOW BOOKS
@app.route('/show-books/', methods=["GET"])
def get_products():
    response = {}

    with sqlite3.connect("book_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book")

        products = cursor.fetchall()

    response["status_code"] = 200
    response["data"] = products

    return response


# FUNCTION TO VIEW BOOKS
@app.route('/view-book/<int:post_id>/', methods=["GET"])
def get_post(post_id):
    response = {}

    with sqlite3.connect("book_db.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM book WHERE id={str(post_id)}")

        response["status_code"] = 200
        response["description"] = "Product Retrieval Successful"
        response["data"] = cursor.fetchone()

    return jsonify(response)


# FUNCTION TO EDIT BOOK ENTRIES
@app.route('/edit-book/<int:post_id>/', methods=["PUT"])
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('book_db.db') as connection:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")

                with sqlite3.connect("book_db.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE book SET name =? WHERE id=?", (put_data["name"], post_id))
                    conn.commit()
                    response["message"] = "Name Updated Successfully"
                    response["status_code"] = 200

            if incoming_data.get("img_url") is not None:
                put_data["img_url"] = incoming_data.get("img_url")

                with sqlite3.connect("book_db.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE book SET img_url =? WHERE id=?", (put_data["img_url"], post_id))
                    conn.commit()
                    response["message"] = "img_url Updated Successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect("book_db.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE book SET description =? WHERE id=?", (put_data["description"], post_id))
                    conn.commit()

                    response["message"] = "Description Updated Successfully"
                    response["status_code"] = 200

            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect("book_db.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE book SET price =? WHERE id=?", (put_data["price"], post_id))
                    conn.commit()

                    response["message"] = "Price Updated Successfully"
                    response["status_code"] = 200

            if incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")

                with sqlite3.connect("book_db.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE book SET category =? WHERE id=?", (put_data["category"], post_id))
                    conn.commit()

                    response["message"] = "Category Updated Successfully"
                    response["status_code"] = 200
    return response


# RUNS CODE
if __name__ == "__main__":
    app.run()
