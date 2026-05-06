from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "vegshop"


# ---------------- DATABASE ----------------

def get_db():

    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db()
    cur = conn.cursor()

    cur.execute('''

    CREATE TABLE IF NOT EXISTS Users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )

    ''')

    cur.execute("INSERT OR IGNORE INTO Users VALUES(1,'admin','admin')")


    cur.execute('''

    CREATE TABLE IF NOT EXISTS Products(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )

    ''')


    cur.execute('''

    CREATE TABLE IF NOT EXISTS Cart(
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER
    )

    ''')


    cur.execute('''

    CREATE TABLE IF NOT EXISTS PurchaseHistory(
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item TEXT,
        price REAL
    )

    ''')


    vegetables = [

        ("Tomato",20),
        ("Potato",30),
        ("Carrot",40),
        ("Onion",25),
        ("Cabbage",28),
        ("Brinjal",35),
        ("Beans",50),
        ("Pumpkin",45),
        ("Radish",22),
        ("Beetroot",32),
        ("Spinach",18),
        ("Capsicum",55)

    ]


    for veg in vegetables:

        cur.execute(
        "INSERT OR IGNORE INTO Products(name,price) VALUES(?,?)",
        veg
        )


    conn.commit()
    conn.close()


# ---------------- SIDEBAR UI ----------------

def sidebar():

    return """

    <div style="width:230px;
    height:100vh;
    background:#c8e6c9;
    padding:20px;
    position:fixed">

    <h4>🥦 Veg Shop</h4>

    <hr>

    <a href="/dashboard">Dashboard</a><br><br>

    <a href="/products">Products</a><br><br>

    <a href="/cart">Cart</a><br><br>

    <a href="/">Logout</a>

    </div>

    """


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET","POST"])

def login():

    if request.method == "POST":

        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()

        user = conn.execute(
        "SELECT * FROM Users WHERE username=? AND password=?",
        (u,p)
        ).fetchone()

        conn.close()

        if user:

            session["user"] = user["user_id"]

            return redirect("/dashboard")


    return """

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="background:#e8f5e9;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh">

    <div class="card shadow p-4">

    <h3 class="text-success">Veggie Store Login</h3>

    <form method="POST">

    <input name="username" class="form-control mb-3">

    <input name="password" type="password"
    class="form-control mb-3">

    <button class="btn btn-success w-100">

    Login

    </button>

    </form>

    </div>

    </body>

    </html>

    """


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")

def dashboard():

    uid = session["user"]

    conn = get_db()

    product_count = conn.execute(
    "SELECT COUNT(*) FROM Products"
    ).fetchone()[0]

    cart_count = conn.execute(
    "SELECT COUNT(*) FROM Cart WHERE user_id=?",
    (uid,)
    ).fetchone()[0]

    history_count = conn.execute(
    "SELECT COUNT(*) FROM PurchaseHistory WHERE user_id=?",
    (uid,)
    ).fetchone()[0]

    conn.close()


    return f"""

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="background:#f1f8e9">

    {sidebar()}

    <div style="margin-left:260px;padding:40px">

    <h2>Dashboard</h2>

    <div class="row mt-4">


    <div class="col-md-4">

    <div class="card shadow p-4">

    <h5>Total Products</h5>

    <h2>{product_count}</h2>

    </div>

    </div>


    <div class="col-md-4">

    <div class="card shadow p-4">

    <h5>Cart Items</h5>

    <h2>{cart_count}</h2>

    </div>

    </div>


    <div class="col-md-4">

    <div class="card shadow p-4">

    <h5>Purchase History</h5>

    <h2>{history_count}</h2>

    </div>

    </div>

    </div>

    </div>

    </body>

    </html>

    """


# ---------------- PRODUCTS ----------------

@app.route("/products", methods=["GET","POST"])

def products():

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]

        conn.execute(
        "INSERT INTO Products(name,price) VALUES(?,?)",
        (name,price)
        )

        conn.commit()


    items = conn.execute(
    "SELECT * FROM Products"
    ).fetchall()

    conn.close()


    html = f"""

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="background:#fffde7">

    {sidebar()}

    <div style="margin-left:260px;padding:40px">

    <div class="d-flex justify-content-between">

    <h2>Products</h2>


    <form method="POST" class="d-flex">

    <input name="name"
    placeholder="Vegetable name"
    class="form-control me-2">

    <input name="price"
    placeholder="Price"
    class="form-control me-2">

    <button class="btn btn-success">

    Add Product

    </button>

    </form>

    </div>


    <div class="row mt-4">

    """


    for i in items:

        html += f"""

        <div class="col-md-3">

        <div class="card shadow p-3 mb-4">

        <h5>{i['name']}</h5>

        <h6>₹ {i['price']}</h6>

        <a href="/add_cart/{i['product_id']}"
        class="btn btn-success">

        Add to Cart

        </a>

        </div>

        </div>

        """


    html += """

    </div>

    </div>

    </body>

    </html>

    """

    return html


# ---------------- ADD CART ----------------

@app.route("/add_cart/<int:pid>")

def add_cart(pid):

    uid = session["user"]

    conn = get_db()

    conn.execute(
    "INSERT INTO Cart(user_id,product_id) VALUES(?,?)",
    (uid,pid)
    )

    conn.commit()

    conn.close()

    return redirect("/products")


# ---------------- CART ----------------

@app.route("/cart")

def cart():

    uid = session["user"]

    conn = get_db()

    items = conn.execute("""

    SELECT Products.name,Products.price

    FROM Cart

    JOIN Products

    ON Cart.product_id=Products.product_id

    WHERE Cart.user_id=?

    """,(uid,)).fetchall()


    history = conn.execute(
    "SELECT * FROM PurchaseHistory WHERE user_id=?",
    (uid,)
    ).fetchall()


    total = 0


    html = f"""

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="background:#fce4ec">

    {sidebar()}

    <div style="margin-left:260px;padding:40px">

    <h2>Cart</h2>

    <table class="table table-bordered">

    <tr>

    <th>Vegetable</th>

    <th>Price</th>

    </tr>

    """


    for i in items:

        total += i["price"]

        html += f"""

        <tr>

        <td>{i['name']}</td>

        <td>₹ {i['price']}</td>

        </tr>

        """


    html += f"""

    </table>

    <h4>Total Bill : ₹ {total}</h4>

    <a href="/purchase"
    class="btn btn-success">

    Purchase

    </a>


    <hr>

    <h3>Purchase History</h3>

    <table class="table table-bordered">

    <tr>

    <th>Vegetable</th>

    <th>Price</th>

    </tr>

    """


    for h in history:

        html += f"""

        <tr>

        <td>{h['item']}</td>

        <td>₹ {h['price']}</td>

        </tr>

        """


    html += """

    </table>

    </div>

    </body>

    </html>

    """

    conn.close()

    return html


# ---------------- PURCHASE ----------------

@app.route("/purchase")

def purchase():

    uid = session["user"]

    conn = get_db()

    items = conn.execute("""

    SELECT Products.name,Products.price

    FROM Cart

    JOIN Products

    ON Cart.product_id=Products.product_id

    WHERE Cart.user_id=?

    """,(uid,)).fetchall()


    for i in items:

        conn.execute(
        "INSERT INTO PurchaseHistory(user_id,item,price) VALUES(?,?,?)",
        (uid,i["name"],i["price"])
        )


    conn.execute(
    "DELETE FROM Cart WHERE user_id=?",
    (uid,)
    )


    conn.commit()

    conn.close()

    return redirect("/cart")


# ---------------- RUN ----------------

if __name__ == "__main__":

    create_tables()

    app.run(debug=True)