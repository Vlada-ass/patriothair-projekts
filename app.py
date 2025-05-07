from flask import Flask, render_template, redirect, url_for, request
import flask
import sqlite3
from pathlib import Path

# Izveido Flask lietojumprogrammu
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Nodrošina, ka veidnes tiek automātiski atjauninātas

# Funkcija, kas izveido savienojumu ar SQLite datubāzi
def get_db_connection():
    # Atrod ceļu uz datubāzes failu (miniveikals.db)
    db = Path(__file__).parent / "miniveikals.db"
    # Izveido savienojumu ar datubāzi
    conn = sqlite3.connect(db)
    # Nodrošina, ka rezultāti būs pieejami kā vārdnīcas (piemēram, "product['name']")
    conn.row_factory = sqlite3.Row
    # Atgriež savienojumu
    return conn

# Maršruts, kas ļauj pievienot jaunu produktu
@app.route("/produkti/jauns", methods=["GET", "POST"])
def products_new():
    conn = get_db_connection()

    # Ja ir POST pieprasījums (forma ir aizpildīta un nosūtīta)
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        producer_id = request.form["producer_id"]
        composition_id = request.form["composition_id"]
        description_id = request.form["description_id"]
        image = request.form["image"]

        # Pievieno jaunu produktu datubāzē
        conn.execute("""
            INSERT INTO products (name, price, producer_id, composition_id, description_id, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, price, producer_id, composition_id, description_id, image))
        conn.commit()
        conn.close()

        # Novirza uz produktu sarakstu
        return redirect(url_for("products"))

    # Ja ir GET pieprasījums (parāda veidlapu ar pieejamiem datiem)
    producers = conn.execute("SELECT * FROM producers").fetchall()
    compositions = conn.execute("SELECT * FROM compositions").fetchall()
    descriptions = conn.execute("SELECT * FROM descriptions").fetchall()
    conn.close()

    return render_template("products_new.html", 
                            producers=producers, 
                            compositions=compositions, 
                            descriptions=descriptions)

# Maršruts, kas ļauj rediģēt esošu produktu
@app.route("/produkti/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    producers = conn.execute("SELECT * FROM producers").fetchall()
    compositions = conn.execute("SELECT * FROM compositions").fetchall()
    descriptions = conn.execute("SELECT * FROM descriptions").fetchall()

    # Ja produkts nav atrasts, atgriež 404 kļūdu
    if product is None:
        conn.close()
        return "Produkts nav atrasts", 404

    # Ja ir POST pieprasījums, atjaunina produkta datus datubāzē
    if flask.request.method == "POST":
        name = flask.request.form["name"]
        price = flask.request.form["price"]
        producer_id = flask.request.form["producer_id"]
        composition_id = flask.request.form["composition_id"]
        description_id = flask.request.form["description_id"]
        
        conn.execute("""
            UPDATE products
            SET name = ?, price = ?, producer_id = ?, composition_id = ?, description_id = ?
            WHERE id = ?
        """, (name, price, producer_id, composition_id, description_id, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for("products_show", product_id=product_id))

    conn.close()
    return render_template("products_edit.html", product=product, producers=producers,
                            compositions=compositions, descriptions=descriptions)

# Maršruts, kas parāda produkta detalizētu informāciju
@app.route("/produkti/<int:product_id>")
def products_show(product_id):
    conn = get_db_connection()
    product = conn.execute("""
        SELECT 
            products.*, 
            producers.name AS producer_name, 
            producers.country AS producer_country,
            compositions.composition AS composition,
            descriptions.description AS description
        FROM products
        JOIN producers ON products.producer_id = producers.id
        JOIN compositions ON products.composition_id = compositions.id
        JOIN descriptions ON products.description_id = descriptions.id
        WHERE products.id = ?
    """, (product_id,)).fetchone()
    conn.close()
    return render_template("products_show.html", product=product)

# Maršruts, kas parāda visu produktu sarakstu
@app.route("/produkti")
def products():
    conn = get_db_connection()  # Pieslēdzas datubāzei
    products = conn.execute("SELECT * FROM products").fetchall()  # Iegūst visus produktus
    producers = conn.execute("SELECT * FROM producers").fetchall()  # Iegūst visus ražotājus
    conn.close()  # Aizver savienojumu ar datubāzi
    return render_template("products.html", products=products, producers=producers)  # Nodod datus veidnei

# Maršruts, kas ļauj dzēst produktu no datubāzes
@app.route("/produkti/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))  # Dzēš produktu
    conn.commit()
    conn.close()
    return redirect(url_for("products"))  # Novirza uz produktu sarakstu

# Maršruts sākumlapai
@app.route("/")
def home():
    return render_template("index.html")

# Maršruts par "Par mums" lapu
@app.route("/par-mums")
def about():
    return render_template("about.html")

# Ja šis fails tiek palaists tieši (nevis importēts), tad palaiž Flask serveri
if __name__ == "__main__":
    app.run(debug=True)
