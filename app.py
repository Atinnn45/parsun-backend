from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import timedelta, datetime
from collections import defaultdict
from urllib.parse import unquote
import re

app = Flask(__name__)

# CONFIG
app.secret_key = os.environ.get('SECRET_KEY', "dev_secret")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, "database.db"))

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "static/img/produk")
app.config['CATALOG_IMAGE_FOLDER'] = os.path.join(BASE_DIR, "static/catalog_images")
app.config['PDF_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "static/catalog_pdf")  # backward compatibility
app.config['LOGO_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "static/img/logos")

print("DATABASE PATH:", DATABASE)


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def rows_to_dict(rows):
    return [dict(row) for row in rows]

def row_to_dict(row):
    return dict(row) if row else None

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            logo_url TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT,
            name TEXT,
            price INTEGER,
            stock INTEGER,
            sold INTEGER DEFAULT 0,
            description TEXT,
            image TEXT,
            category_id INTEGER,
            product_type TEXT,
            real_price INTEGER DEFAULT 0,
            admin_notes TEXT DEFAULT '',
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalog_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            pk TEXT NOT NULL,
            pdf_file TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            product TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration: tambah kolom baru jika belum ada
    existing_products = [r[1] for r in cursor.execute("PRAGMA table_info(products)").fetchall()]
    if 'real_price' not in existing_products:
        cursor.execute("ALTER TABLE products ADD COLUMN real_price INTEGER DEFAULT 0")
        print("[MIGRATION] Kolom real_price ditambahkan.")
    if 'admin_notes' not in existing_products:
        cursor.execute("ALTER TABLE products ADD COLUMN admin_notes TEXT DEFAULT ''")
        print("[MIGRATION] Kolom admin_notes ditambahkan.")

    existing_categories = [r[1] for r in cursor.execute("PRAGMA table_info(categories)").fetchall()]
    if 'logo_url' not in existing_categories:
        cursor.execute("ALTER TABLE categories ADD COLUMN logo_url TEXT DEFAULT ''")
        print("[MIGRATION] Kolom logo_url ditambahkan ke categories.")

    conn.commit()
    conn.close()

@app.route("/ai_command", methods=["POST"])
def ai_command():
    ...

# ===================== HOME ==============================
@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()
    search_query = request.args.get("q")

    cursor.execute("""
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
    """)
    categories = rows_to_dict(cursor.fetchall())

    if search_query:
        cursor.execute("""
            SELECT products.*, categories.name as category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE products.name LIKE ? OR products.product_code LIKE ?
        """, ("%" + search_query + "%", "%" + search_query + "%"))
    else:
        cursor.execute("""
            SELECT products.*, categories.name as category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            ORDER BY RANDOM()
        """)

    products = rows_to_dict(cursor.fetchall())
    conn.close()
    return render_template("home.html", products=products, categories=categories)


# ===================== CATEGORY ==============================
@app.route("/category/<int:category_id>")
def category_page(category_id):
    conn = get_connection()
    cursor = conn.cursor()

    selected_type = request.args.get("type", "").strip().lower()

    if selected_type and selected_type != "all":
        cursor.execute("""
            SELECT products.*, categories.name as category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE products.category_id = ?
            AND LOWER(products.product_type) = ?
        """, (category_id, selected_type))
    else:
        cursor.execute("""
            SELECT products.*, categories.name as category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE products.category_id = ?
        """, (category_id,))

    products = rows_to_dict(cursor.fetchall())

    cursor.execute("SELECT * FROM categories WHERE id=?", (category_id,))
    current_category = row_to_dict(cursor.fetchone())
    conn.close()

    return render_template("category.html",
                           products=products,
                           current_category=current_category,
                           selected_type=selected_type)


# ===================== CART ==============================
@app.route("/cart")
def cart():
    return render_template("cart.html")


# ===================== PRODUCT DETAIL ==============================
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.*, categories.name as category_name
        FROM products
        LEFT JOIN categories ON products.category_id = categories.id
        WHERE products.id=?
    """, (product_id,))
    product = row_to_dict(cursor.fetchone())
    conn.close()
    if not product:
        abort(404)
    return render_template("detail.html", product=product)


# ===================== CATALOG HOME ==============================
@app.route("/catalog")
def catalog_home():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT brand FROM catalog_guides")
    brands = rows_to_dict(cursor.fetchall())
    conn.close()
    return render_template("catalog_home.html", brands=brands)


# ===================== CATALOG BRAND ==============================
@app.route("/catalog/<path:brand>")
def catalog_brand(brand):
    from urllib.parse import unquote
    brand = unquote(brand.strip())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pk, pdf_file FROM catalog_guides WHERE LOWER(brand)=LOWER(?)", (brand,))
    raw_items = cursor.fetchall()
    pk_options = []
    for item in raw_items:
        item_dict = dict(item)
        item_dict['name'] = item_dict['pk']
        item_dict['file'] = item_dict['pdf_file']
        item_dict['type'] = 'pdf' if item_dict['file'].lower().endswith('.pdf') else 'image'
        pk_options.append(item_dict)
    conn.close()
    if not pk_options:
        return f"Brand '{brand}' tidak ditemukan", 404
    return render_template("catalog_brand.html", brand=brand, items=pk_options)


# ===================== CATALOG PK ==============================
@app.route("/catalog/<brand>/<pk>")
def catalog_pk(brand, pk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pdf_file FROM catalog_guides
        WHERE LOWER(brand) LIKE LOWER(?) AND LOWER(pk)=LOWER(?)
    """, ('%' + brand + '%', pk))
    data = row_to_dict(cursor.fetchone())
    conn.close()
    if not data:
        abort(404)
    return redirect(url_for('static', filename='catalog_pdf/' + data['pdf_file']))


# ===================== ADMIN ROOT ==============================
@app.route("/admin")
def admin_root():
    return redirect(url_for("admin_dashboard"))


# ===================== ADMIN DASHBOARD ==============================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM catalog_guides")
    total_catalogs = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 5")
    recent_products = rows_to_dict(cursor.fetchall())
    conn.close()
    return render_template("admin_dashboard.html",
                           total_products=total_products,
                           total_categories=total_categories,
                           total_catalogs=total_catalogs,
                           recent_products=recent_products)


# ===================== ADMIN CATEGORIES (LIST) ==============================
@app.route("/admin/categories")
def admin_categories():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
        ORDER BY c.name
    """)
    categories = rows_to_dict(cursor.fetchall())
    conn.close()

    return render_template("admin_categories.html", categories=categories)


# ===================== ADMIN CATEGORY ADD ==============================
@app.route("/admin/categories/add", methods=["POST"])
def admin_category_add():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    logo = request.files.get("logo")
    logo_url = ""

    if logo and logo.filename:
        os.makedirs(app.config['LOGO_UPLOAD_FOLDER'], exist_ok=True)
        filename = logo.filename
        logo.save(os.path.join(app.config['LOGO_UPLOAD_FOLDER'], filename))
        logo_url = url_for('static', filename='img/logos/' + filename)

    if name:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name, logo_url) VALUES (?, ?)", (name, logo_url))
        conn.commit()
        conn.close()

    return redirect(url_for("admin_categories"))


# ===================== ADMIN CATEGORY EDIT ==============================
@app.route("/admin/categories/edit/<int:category_id>", methods=["POST"])
def admin_category_edit(category_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    logo = request.files.get("logo")

    conn = get_connection()
    cursor = conn.cursor()

    if logo and logo.filename:
        os.makedirs(app.config['LOGO_UPLOAD_FOLDER'], exist_ok=True)
        filename = logo.filename
        logo.save(os.path.join(app.config['LOGO_UPLOAD_FOLDER'], filename))
        logo_url = url_for('static', filename='img/logos/' + filename)
        cursor.execute(
            "UPDATE categories SET name=?, logo_url=? WHERE id=?",
            (name, logo_url, category_id)
        )
    else:
        # Tidak upload logo baru, hanya update nama
        cursor.execute(
            "UPDATE categories SET name=? WHERE id=?",
            (name, category_id)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("admin_categories"))


# ===================== ADMIN CATEGORY DELETE ==============================
@app.route("/admin/categories/delete/<int:category_id>")
def admin_category_delete(category_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET category_id = NULL WHERE category_id=?", (category_id,))
    cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_categories"))


# ===================== ADMIN ADD ==============================
@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = rows_to_dict(cursor.fetchall())

    if request.method == "POST":
        product_code = request.form["product_code"]
        name         = request.form["name"]
        price        = request.form["price"]
        stock        = request.form["stock"]
        description  = request.form["description"]
        category     = request.form["category"]
        product_type = request.form["product_type"]
        real_price   = request.form.get("real_price", 0) or 0
        admin_notes  = request.form.get("admin_notes", "")

        file = request.files["image"]
        filename = ""
        if file and file.filename:
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cursor.execute("""
            INSERT INTO products
            (product_code, name, price, stock, description, image,
             category_id, product_type, real_price, admin_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_code, name, price, stock, description, filename,
              category, product_type, real_price, admin_notes))

        conn.commit()
        conn.close()
        return redirect(url_for("admin_list"))

    conn.close()
    return render_template("admin_add.html", categories=categories)


# ===================== ADMIN LIST ==============================
@app.route("/admin/list")
def admin_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.*, categories.name as category_name
        FROM products
        LEFT JOIN categories ON products.category_id = categories.id
    """)
    products = rows_to_dict(cursor.fetchall())
    conn.close()
    return render_template("admin_list.html", products=products)


# ===================== ADMIN EDIT ==============================
@app.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
def admin_edit(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = rows_to_dict(cursor.fetchall())

    if request.method == "POST":
        real_price  = request.form.get("real_price", 0) or 0
        admin_notes = request.form.get("admin_notes", "")

        file = request.files.get("image")
        cursor.execute("SELECT image FROM products WHERE id=?", (product_id,))
        current = row_to_dict(cursor.fetchone())
        filename = current['image'] if current else ""

        if file and file.filename:
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cursor.execute("""
            UPDATE products
            SET product_code=?, name=?, price=?, stock=?,
                description=?, category_id=?, product_type=?,
                real_price=?, admin_notes=?, image=?
            WHERE id=?
        """, (
            request.form["product_code"],
            request.form["name"],
            request.form["price"],
            request.form["stock"],
            request.form["description"],
            request.form["category"],
            request.form["product_type"],
            real_price,
            admin_notes,
            filename,
            product_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_list"))

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = row_to_dict(cursor.fetchone())
    conn.close()
    return render_template("admin_edit.html", product=product, categories=categories)


# ===================== ADMIN DELETE ==============================
@app.route("/admin/delete/<int:product_id>")
def admin_delete(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_list"))


# ===================== ADMIN UPLOAD PDF ==============================
@app.route("/admin/upload-catalog", methods=["GET", "POST"])
def admin_upload_catalog():
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        brand = request.form.get("brand")
        pk    = request.form.get("pk")
        file  = request.files.get("image_file")
        if not brand or not pk:
            conn.close()
            return "Brand dan PK wajib diisi"
        if file and file.filename:
            os.makedirs(app.config["CATALOG_IMAGE_FOLDER"], exist_ok=True)
            filename = file.filename
            file.save(os.path.join(app.config["CATALOG_IMAGE_FOLDER"], filename))
            cursor.execute("INSERT INTO catalog_guides (brand, pk, pdf_file) VALUES (?, ?, ?)",
                           (brand.strip(), pk.strip(), filename))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_catalog_list"))
        conn.close()
        return "File gambar wajib diupload"
    conn.close()
    return render_template("admin_upload_catalog.html")


# Backward compatible old route
@app.route("/admin/upload-pdf", methods=["GET", "POST"])
def admin_upload_pdf():
    return admin_upload_catalog()


# ===================== ADMIN CATALOG LIST ==============================
@app.route("/admin/catalog-list")
def admin_catalog_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, brand, pk, pdf_file FROM catalog_guides ORDER BY brand ASC")
    catalogs = rows_to_dict(cursor.fetchall())
    conn.close()
    return render_template("admin_catalog_list.html", catalogs=catalogs)


# ===================== ADMIN CATALOG DELETE ==============================
@app.route("/admin/catalog-delete/<int:id>")
def admin_delete_catalog(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_file FROM catalog_guides WHERE id=?", (id,))
    data = row_to_dict(cursor.fetchone())
    if data:
        image_path = os.path.join(app.config["CATALOG_IMAGE_FOLDER"], data["pdf_file"])
        if os.path.exists(image_path):
            os.remove(image_path)
    cursor.execute("DELETE FROM catalog_guides WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_catalog_list"))


# ===================== ADMIN EDIT CATALOG ==============================
@app.route("/admin/catalog-edit/<int:id>", methods=["GET", "POST"])
def admin_edit_catalog(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog_guides WHERE id=?", (id,))
    catalog = row_to_dict(cursor.fetchone())
    if not catalog:
        conn.close()
        abort(404)
    if request.method == "POST":
        brand = request.form["brand"].strip()
        pk = request.form["pk"].strip()
        file = request.files.get("image_file")

        if file and file.filename:
            os.makedirs(app.config["CATALOG_IMAGE_FOLDER"], exist_ok=True)
            new_filename = file.filename
            file.save(os.path.join(app.config["CATALOG_IMAGE_FOLDER"], new_filename))
            # Hapus file lama jika ada
            if catalog.get("pdf_file"):
                old_img = os.path.join(app.config["CATALOG_IMAGE_FOLDER"], catalog["pdf_file"])
                if os.path.exists(old_img):
                    os.remove(old_img)
            cursor.execute("UPDATE catalog_guides SET brand=?, pk=?, pdf_file=? WHERE id=?",
                           (brand, pk, new_filename, id))
        else:
            cursor.execute("UPDATE catalog_guides SET brand=?, pk=? WHERE id=?",
                           (brand, pk, id))

        conn.commit()
        conn.close()
        return redirect(url_for("admin_catalog_list"))
    conn.close()
    return render_template("admin_edit_catalog.html", catalog=catalog)

@app.route("/ai_command", methods=["POST"])
def ai_command():
    try:
        data = request.json
        text = data.get("text", "").strip().lower()
        print("AI INPUT:", text)
        
        import re
        
        # Stock update: "update stock nama jadi 10" or "ubah stock nama jadi 10" or "stock nama jadi 10"
        stock_match = re.search(r"(update|ubah)?\s*stock\s+(.+?)\s+(?:jadi|ke)\s+(\d+)", text)
        if stock_match:
            product_name = stock_match.group(2).strip()
            new_stock = int(stock_match.group(3))
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET stock = ? WHERE LOWER(name) LIKE LOWER(?)", (new_stock, f"%{product_name}%"))
            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_updated > 0:
                return jsonify({"status": "success", "reply": f"✅ Stock {product_name} diubah menjadi {new_stock}"})
            else:
                return jsonify({"status": "error", "reply": "❌ Produk '{product_name}' tidak ditemukan"})
        
        # Sold update: "update sold nama jadi 10"
        sold_match = re.search(r"(update|ubah)?\s*sold\s+(.+?)\s+(?:jadi|ke)\s+(\d+)", text)
        if sold_match:
            product_name = sold_match.group(2).strip()
            new_sold = int(sold_match.group(3))
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET sold = ? WHERE LOWER(name) LIKE LOWER(?)", (new_sold, f"%{product_name}%"))
            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_updated > 0:
                return jsonify({"status": "success", "reply": f"✅ Sold {product_name} diubah menjadi {new_sold}"})
            else:
                return jsonify({"status": "error", "reply": f"❌ Produk '{product_name}' tidak ditemukan"})
        
        # Default response
        return jsonify({"status": "error", "reply": "Perintah tidak dikenali. Contoh: 'update stock Oil Pump jadi 10' atau 'ubah sold Parsun F15 jadi 5'"})
    
    except Exception as e:
        print(f"AI COMMAND ERROR: {str(e)}")
        return jsonify({"status": "error", "reply": f"Server error: {str(e)}"}), 500

@app.route("/check_db")
def check_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(products)")
        products_schema = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "tables": tables,
            "product_count": product_count,
            "products_schema": products_schema[:10]  # first 10 columns
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ===================== ADMIN LOGIN ==============================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "parsun":
            session["admin"] = True
            session["last_activity"] = datetime.now().isoformat()
            session.permanent = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Username atau password salah")
    return render_template("admin_login.html")


# ===================== ADMIN LOGOUT ==============================
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# ===================== SESSION TIMEOUT ==============================
@app.before_request
def session_timeout_check():
    if "admin" in session:
        now = datetime.now()
        if "last_activity" not in session:
            session["last_activity"] = now.isoformat()
            session.permanent = True
            return
        last = datetime.fromisoformat(session["last_activity"])
        if (now - last).total_seconds() > 300:
            session.clear()
            return redirect(url_for("admin_login"))
        session["last_activity"] = now.isoformat()
        session.permanent = True


# ===================== PROTECT ADMIN ==============================
@app.before_request
def protect_admin_routes():
    if request.path.startswith("/admin") and request.path != "/admin/login":
        if "admin" not in session:
            return redirect(url_for("admin_login"))


# ===================== 404 HANDLER ==============================
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# ===================== CATALOG MENU ==============================
@app.context_processor
def inject_catalog_menu():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT brand FROM catalog_guides")
    brands = rows_to_dict(cursor.fetchall())
    catalog_data = {}
    for brand in brands:
        cursor.execute("SELECT pk FROM catalog_guides WHERE brand=?", (brand["brand"],))
        catalog_data[brand["brand"]] = rows_to_dict(cursor.fetchall())
    conn.close()
    return dict(catalog_menu=catalog_data)


# ===================== RUN ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"

    init_db()
    app.run(host="0.0.0.0", port=port, debug=debug)
