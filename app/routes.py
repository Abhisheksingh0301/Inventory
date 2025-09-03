
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/products', methods=['GET', 'POST'])
def products():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        gst_rate = request.form.get('gst_rate')

        if not name or not gst_rate:
            flash('Please enter both product name and GST rate', 'error')
        else:
            try:
                gst_rate = float(gst_rate)
                db.execute('INSERT INTO products (name, gst_rate, stock_quantity) VALUES (?, ?, ?)',
                           (name, gst_rate, 0))
                db.commit()
                flash('Product added successfully!', 'success')
                return redirect(url_for('main.products'))
            except ValueError:
                flash('GST rate must be a number', 'error')

    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('products.html', products=products)

@main.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()
    # Optionally flash a success message here
    return redirect(url_for('main.products'))

@main.route('/purchase', methods=['GET', 'POST'])
def purchase():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        purchase_price = float(request.form['purchase_price'])
        purchase_date = request.form['purchase_date']

        # Insert purchase
        db.execute('INSERT INTO purchases (product_id, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?)',
                   (product_id, quantity, purchase_price, purchase_date))
        # Update stock
        db.execute('UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?', (quantity, product_id))
        db.commit()
        return redirect(url_for('main.purchase'))

    # JOIN purchases with products to get product name
    purchases = db.execute('''
        SELECT purchases.id, products.name AS product_name, purchases.quantity, purchases.purchase_price, purchases.purchase_date
        FROM purchases
        JOIN products ON purchases.product_id = products.id
        ORDER BY purchases.id DESC
    ''').fetchall()

    return render_template('purchase.html', products=products, purchases=purchases)



