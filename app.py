from flask import Flask, render_template, redirect, url_for, request
import flask
import sqlite3
from pathlib import Path

# Importē Flask klasi no flask bibliotēkas
import sqlite3

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Definē maršrutu: kad lietotājs apmeklē mājaslapas sākumlapu ("/"), tiek izsaukta funkcija home()


def get_db_connection():
    # izveido un atgriež savienojumu ar SQLite datubāzi
    # atros celu uz datu bāzes failu (tas atrodas taja pašā mapē, kur šis fails)
    db = Path(__file__).parent / "miniveikals.db"
    # izveido savienojumuar SQLite datubāzi
    conn = sqlite3.connect(db)
    # Nodrošina, ka rezultāti būs pieejami kā vārdnīcas (piemēram "product["name"]")
    conn.row_factory = sqlite3.Row
    # atgriež savienojumu
    return conn

@app.route("/produkti/jauns", methods=["GET", "POST"])
def products_new():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        producer_id = request.form["producer_id"]
        composition_id = request.form["composition_id"]
        description_id = request.form["description_id"]
        image = request.form["image"]

        conn.execute("""
            INSERT INTO products (name, price, producer_id, composition_id, description_id, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, price, producer_id, composition_id, description_id, image))
        conn.commit()
        conn.close()

        return redirect(url_for("products"))

    # Ja metode ir GET – iegūst sarakstus veidlapai
    producers = conn.execute("SELECT * FROM producers").fetchall()
    compositions = conn.execute("SELECT * FROM compositions").fetchall()
    descriptions = conn.execute("SELECT * FROM descriptions").fetchall()
    conn.close()

    return render_template("products_new.html", 
                            producers=producers, 
                            compositions=compositions, 
                            descriptions=descriptions)
# Maršruts, kas atbild uz pieprasījumu, piemēram: /produkti/3
# Šeit <int:product_id> nozīmē, ka URL daļā gaidāms produkta ID kā skaitlis


@app.route("/produkti/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    producers = conn.execute("SELECT * FROM producers").fetchall()
    compositions = conn.execute("SELECT * FROM compositions").fetchall()
    descriptions = conn.execute("SELECT * FROM descriptions").fetchall()

    if product is None:
        conn.close()
        return "Produkts nav atrasts", 404

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/")
def home():
    # Atgriež tekstu, kas tiks parādīts pārlūkā
    # Šis bloks tiek izpildīts tikai tad, ja fails tiek palaists tieši (nevis importēts)
    return render_template("index.html")


# Flask produktu maršruts


@app.route("/produkti")
def products():
    conn = get_db_connection()  # pieslēdzas datubāzei
    products = conn.execute("SELECT * FROM products").fetchall()
    producers = conn.execute(
        "SELECT * FROM producers"
    ).fetchall()  # Iegūst ražotāju informāciju
    conn.close()  # Aizver savienojumu ar datubāzi
    return render_template(
        "products.html", products=products, producers=producers
    )  # Nodod datus veidnei


@app.route("/par-mums")
def about():
    return render_template("about.html")

@app.route("/produkti/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("products"))

if __name__ == "__main__":
    app.run(debug=True)