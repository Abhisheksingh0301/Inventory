
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db
from datetime import datetime

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
        brand = request.form.get('brand')
        size = request.form.get('size')
        desc=request.form.get('desc')
        gst_rate = request.form.get('gst_rate')

        if not name or not gst_rate:
            flash('Please enter both product name and GST rate', 'error')
        else:
            try:
                gst_rate = float(gst_rate)
                db.execute('INSERT INTO products (name, brand, item_size, description, gst_rate, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)',
                           (name, brand, size, desc, gst_rate, 0))
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
    suppliers = db.execute('SELECT * FROM suppliers').fetchall()
    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        product_id = request.form['product_id']
        supplier_id = request.form['supplier_id']
        quantity = int(request.form['quantity'])
        purchase_price = float(request.form['purchase_price'])
        taxable_value = quantity * purchase_price
        cgst_rate = float(request.form.get('cgst_rate', 0))
        cgst_amount = (taxable_value * cgst_rate) / 100
        sgst_rate = float(request.form.get('sgst_rate', 0))
        sgst_amount = (taxable_value * sgst_rate) / 100
        igst_rate = float(request.form.get('igst_rate', 0))
        igst_amount = (taxable_value * igst_rate) / 100
        invoice_number = request.form['invoice_number']
        invoice_date = request.form['invoice_date']
        purchase_date = request.form['purchase_date']
        place_of_supply = request.form['place_of_supply']
        is_reverse_charge = request.form.get('is_reverse_charge', '0') == '1'
        tax_status = request.form['tax_status']

        # Insert purchase
        db.execute('''
            INSERT INTO purchases (
                product_id, supplier_id, quantity, purchase_price, taxable_value,
                cgst_rate, cgst_amount, sgst_rate, sgst_amount, igst_rate, igst_amount,
                invoice_number, invoice_date, purchase_date, place_of_supply,
                is_reverse_charge, tax_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id, supplier_id, quantity, purchase_price, taxable_value,
            cgst_rate, cgst_amount, sgst_rate, sgst_amount, igst_rate, igst_amount,
            invoice_number, invoice_date, purchase_date, place_of_supply,
            is_reverse_charge, tax_status
        ))

        # Update stock
        db.execute('UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?', (quantity, product_id))
        db.commit()
        return redirect(url_for('main.purchase'))

    # JOIN purchases with products and suppliers to get product name and supplier details
    purchases = db.execute('''
        SELECT 
            purchases.id, 
            products.name AS product_name, 
            suppliers.name AS supplier_name,
            purchases.quantity, 
            purchases.purchase_price, 
            purchases.taxable_value,
            purchases.cgst_rate, 
            purchases.cgst_amount, 
            purchases.sgst_rate, 
            purchases.sgst_amount, 
            purchases.igst_rate, 
            purchases.igst_amount, 
            purchases.invoice_number, 
            purchases.invoice_date, 
            purchases.purchase_date, 
            purchases.place_of_supply, 
            purchases.is_reverse_charge, 
            purchases.tax_status,
            purchases.entry_date
        FROM purchases
        JOIN products ON purchases.product_id = products.id
        JOIN suppliers ON purchases.supplier_id = suppliers.id
        ORDER BY purchases.id DESC
    ''').fetchall()

    return render_template('purchase.html', products=products, suppliers=suppliers, purchases=purchases, today=today)



@main.route('/suppliers', methods=['GET', 'POST'])
def suppliers():
    db = get_db()

    if request.method == 'POST':
        gstin = request.form['gstin']
        name = request.form['name']
        address = request.form.get('address', '')
        state_code = request.form['state_code']

        # Insert supplier
        db.execute('''
            INSERT INTO suppliers (gstin, name, address, state_code)
            VALUES (?, ?, ?, ?)
        ''', (gstin, name, address, state_code))
        db.commit()
        return redirect(url_for('main.suppliers'))

    # Fetch all suppliers
    suppliers = db.execute('''
        SELECT id, gstin, name, address, state_code
        FROM suppliers
        ORDER BY name ASC
    ''').fetchall()

    return render_template('suppliers.html', suppliers=suppliers)



