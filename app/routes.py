
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Flask, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from datetime import datetime
from functools import wraps

main = Blueprint('main', __name__)

#To check whether user is logged in or not
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "warning")
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@main.route('/about')
# @login_required
def about():
    db=get_db()
    product_count=db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    return render_template('about.html', product_count=product_count)

# @main.route('/about')
# def about():
#     db = get_db()  # Call the function to get the database connection
#     product_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
#     return render_template('about.html', product_count=product_count)

@main.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    db = get_db()
    search = request.args.get('search', '')
    if search:
        products=db.execute("SELECT * FROM products WHERE name=? COLLATE NOCASE OR brand=? COLLATE NOCASE", (search,search)).fetchall() 
    else:
        products=db.execute("SELECT * FROM products").fetchall()
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

    #products = db.execute('SELECT * FROM products').fetchall()
    return render_template('products.html', products=products, search=search)

#To delete the product from product table
@main.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()
    flash('Product deleted successfully','danger')
    return redirect(url_for('main.products'))

@main.route('/purchase', methods=['GET'])
@login_required
def purchase():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    suppliers = db.execute('SELECT * FROM suppliers').fetchall()
    today = datetime.now().strftime('%Y-%m-%d')

    # JOIN purchases with products and suppliers to get product name and supplier details with the search conditions
    search = request.args.get('search', '')
    if search:
         purchases = db.execute('''
            SELECT 
                purchases.*, 
                products.name AS product_name, 
                products.brand AS product_brand, 
                products.item_size AS product_size, 
                suppliers.name AS supplier_name
            FROM purchases         
            JOIN products ON purchases.product_id = products.id
            JOIN suppliers ON purchases.supplier_id = suppliers.id
            WHERE   purchases.invoice_number=? COLLATE NOCASE OR  product_brand=? COLLATE NOCASE           
            ORDER BY purchases.id DESC
        ''', (search,search)).fetchall()
    else :
        purchases = db.execute('''
        SELECT 
            purchases.id, 
            products.name AS product_name, 
            products.brand AS product_brand, 
            products.item_size AS product_size, 
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
@login_required
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

@main.route('/get_brands_sizes', methods=['POST'])
def get_brands_sizes():
    db = get_db()
    data = request.get_json()
    item_name = data.get('item_name')

    if not item_name:
        return jsonify({}), 400

    # 🔍 Get all brand/size combinations for the selected item
    rows = db.execute(
        "SELECT brand, item_size FROM products WHERE name = ?", (item_name,)
    ).fetchall()

    brand_size_map = {}
    for row in rows:
        brand = row['brand']
        size = row['item_size']

        if brand not in brand_size_map:
            brand_size_map[brand] = []

        if size not in brand_size_map[brand]:
            brand_size_map[brand].append(size)

    return jsonify(brand_size_map)

# 📄 GET & POST: /sales
@main.route('/sales', methods=['GET', 'POST'])
@login_required
def sales():
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            # Extract common fields (not item-specific)
            customer_name = request.form['customer_name']
            invoice_number = request.form['invoice_number']
            invoice_date = request.form['invoice_date']
            sale_date = request.form['sale_date']
            place_of_supply = request.form['place_of_supply']
            tax_status = request.form.get('tax_status', 'taxable')
            sale_type = request.form.get('sale_type', 'cash')

            # Process each item in the items array
            items = []
            i = 0
            while f'items[{i}][product_id]' in request.form:
                item = {
                    'product_id': request.form[f'items[{i}][product_id]'],
                    'quantity': int(request.form[f'items[{i}][quantity]']),
                    'sale_price': float(request.form[f'items[{i}][sale_price]']),
                    'discount_amount': float(request.form.get(f'items[{i}][discount_amount]', 0))
                }
                items.append(item)
                i += 1

            if not items:
                flash("No items provided for the sale.", "danger")
                return redirect(url_for('main.sales'))

            # Process each item
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                sale_price = item['sale_price']
                discount_amount = item['discount_amount']

                # Calculate taxable value
                taxable_value = quantity * sale_price - discount_amount
                if taxable_value < 0:
                    taxable_value = 0

                # Fetch product details
                product = db.execute('SELECT gst_rate FROM products WHERE id = ?', (product_id,)).fetchone()
                if not product:
                    flash(f"Product ID {product_id} not found.", "danger")
                    return redirect(url_for('main.sales'))

                # Calculate taxes
                gst_rate = product['gst_rate']
                cgst_rate = sgst_rate = gst_rate / 2
                cgst_amount = sgst_amount = taxable_value * (cgst_rate / 100)
                igst_rate = igst_amount = 0  # Adjust based on your tax logic if needed

                # Insert sale record
                db.execute('''
                    INSERT INTO sales (
                        product_id, customer_name, quantity, sale_price, taxable_value,
                        cgst_rate, cgst_amount, sgst_rate, sgst_amount,
                        igst_rate, igst_amount, discount_amount,
                        invoice_number, invoice_date, sale_date,
                        place_of_supply, tax_status, sale_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_id, customer_name, quantity, sale_price, taxable_value,
                    cgst_rate, cgst_amount, sgst_rate, sgst_amount,
                    igst_rate, igst_amount, discount_amount,
                    invoice_number, invoice_date, sale_date,
                    place_of_supply, tax_status, sale_type
                ))

                # Update stock
                db.execute('UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?', (quantity, product_id))

            # Commit transaction
            db.commit()
            flash("Sale recorded successfully!", "success")
            # return redirect(url_for('main.sales'))
            return redirect(url_for('main.invoice_view', invoice_number=invoice_number))

        except Exception as e:
            db.rollback()
            flash(f"Error recording sale: {str(e)}", "danger")
            return redirect(url_for('main.sales'))

    # GET: Fetch products and ensure valid names
    products_raw = db.execute(
        "SELECT id, name, brand, item_size, hsn_code FROM products WHERE name IS NOT NULL AND name != ''"
    ).fetchall()
    products = [dict(row) for row in products_raw]

    def sanitize(data_list):
        for d in data_list:
            for key, value in d.items():
                if value is None:
                    d[key] = ""
                if key == 'name' and value == "":
                    d[key] = "Unknown"

    sanitize(products)
    unique_names = sorted({product['name'] for product in products if product['name']})

   
    if not unique_names:
        flash("No valid product names found in the database. Please add products.", "warning")

    return render_template('sales.html', products=products, product_names=unique_names, today=today)

#Invoice routes
from jinja2 import Environment, FileSystemLoader
import os
from flask import current_app


# @main.route('/test')
# def test_page():
#     return render_template('home.html', product_names=['One', 'Two', 'Three'], products=[])

@main.route('/invoice/<invoice_number>')
@login_required
def invoice_view(invoice_number):
    db = get_db()
    
    sales = db.execute(
        '''SELECT s.*, p.name, p.brand, p.item_size
           FROM sales s
           JOIN products p ON s.product_id = p.id
           WHERE s.invoice_number = ?''', (invoice_number,)
    ).fetchall()

    if not sales:
        flash("Invoice not found.", "danger")
        return redirect(url_for('main.sales'))

    info = dict(sales[0])
    items = [dict(row) for row in sales]

    total_qty = sum(item['quantity'] for item in items)
    total_discount = sum(item['discount_amount'] for item in items)
    total_taxable = sum(item['taxable_value'] for item in items)
    total_cgst = sum(item['cgst_amount'] for item in items)
    total_sgst = sum(item['sgst_amount'] for item in items)
    total_igst = sum(item['igst_amount'] for item in items)
    grand_total = total_taxable + total_cgst + total_sgst

    return render_template("invoice.html", info=info, items=items,
                           total_qty=total_qty,
                           total_discount=total_discount,
                           total_taxable=total_taxable,
                           total_cgst=total_cgst,
                           total_sgst=total_sgst,
                           total_igst=total_igst,
                           grand_total=grand_total)

@main.route('/salesreport')
@login_required
def salesreport():
    db = get_db()
    sales_rpt = db.execute(
        '''SELECT s.*, p.name as product_name, p.brand, p.item_size
           FROM sales s
           JOIN products p ON s.product_id = p.id
           order by s.invoice_date desc, invoice_number
        '''   
    ).fetchall()
    if not sales:
        flash("Sales not found.", "danger")
        return redirect(url_for('main.sales'))
    sales_count=db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    return render_template("salesreport.html",  sales_rpt=sales_rpt, sales_count=sales_count)

# New dashboard
@main.route('/')
@login_required
def dashboard():
    db=get_db()
    product_count=db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    supplier_count=db.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    total_stock_value=db.execute("SELECT SUM(purchase_price*quantity) FROM purchases").fetchone()[0]
    recent_purchases = db.execute('''
                                  SELECT pur.*, pr.name as product_name, sup.name as supplier_name
                                   FROM purchases pur
                                   join products pr on pr.id = pur.product_id
                                   join suppliers sup on sup.id=pur.supplier_id
                                   order by pur.purchase_date desc LIMIT 5
                                  ''')
    recent_sales = db.execute('''
                              SELECT s.*, pr.name as product_name 
                              FROM sales s
                              join products pr on pr.id=s.product_id
                              order by sale_date desc LIMIT 5
                              ''')
    return render_template('home.html', 
        total_products=product_count,
        total_suppliers=supplier_count,
        total_stock_value=total_stock_value,
        recent_purchases=recent_purchases,
        recent_sales=recent_sales)

#New purchase record
@main.route('/purchase/add_purchase', methods=['GET', 'POST'])
@login_required
def add_purchase():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    suppliers = db.execute('SELECT * FROM suppliers').fetchall()
    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            supplier_id = request.form['supplier_id']
            quantity = int(request.form['quantity'])
            place_of_supply = request.form['place_of_supply']
            purchase_price = float(request.form['purchase_price'])
            taxable_value = quantity * purchase_price
            gst_rate = float(request.form.get('gst_rate', 0))
            cgst_rate = gst_rate / 2
            cgst_amount = (taxable_value * cgst_rate) / 100

            if place_of_supply == "BR":
                sgst_rate = gst_rate / 2
                sgst_amount = (taxable_value * sgst_rate) / 100
                igst_rate = 0
                igst_amount = 0
            else:
                sgst_rate = 0
                sgst_amount = 0
                igst_rate = gst_rate
                igst_amount = (taxable_value * igst_rate) / 100

            invoice_number = request.form['invoice_number']
            invoice_date = request.form['invoice_date']
            purchase_date = request.form['purchase_date']
            is_reverse_charge = request.form.get('is_reverse_charge', '0') == '1'
            tax_status = request.form['tax_status']

            print("Inserting purchase:", product_id, supplier_id, quantity, purchase_price)

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
            print("Insert executed")
            # Update stock
            db.execute('UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?', (quantity, product_id))
            db.commit()
            print("Commit executed")
            flash('Purchase added successfully!', 'success')
            return redirect(url_for('main.purchase'))

        except Exception as e:
            print("Error inserting purchase:", e)
            flash('Error adding purchase: ' + str(e), 'danger')

    return render_template('add_purchase.html', products=products, suppliers=suppliers, today=today)



# To delete the purchase record
@main.route('/delete-purchase/<int:purchase_id>', methods=['POST']) 
@login_required
def delete_purchase(purchase_id): 
    db = get_db()

    # Step 1: Get the purchase details before deleting
    purchase = db.execute(
        'SELECT product_id, quantity FROM purchases WHERE id = ?', 
        (purchase_id,)
    ).fetchone()

    product_id = purchase['product_id']
    quantity = purchase['quantity']

    # Step 2: Update the stock (subtracting the purchase quantity)
    db.execute(
        'UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?', 
        (quantity, product_id)
    )

    # Step 3: Delete the purchase
    db.execute('DELETE FROM purchases WHERE product_id = ?', (product_id,)) 
    db.commit()

    flash('Purchase deleted and stock updated successfully.', 'danger') 
    return redirect(url_for('main.purchase'))

# @main.route('/about')


@main.route('/register', methods=['GET', 'POST'])
# @login_required
def register():
    db = get_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email=request.form['email']

        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match!", 400


        existing_user=db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        # existing_user = db.fetchone()
        if existing_user:
            db.close()
            return "Username already exists!", 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hashed_password, email))
        db.commit()
        flash("Sale recorded successfully!", "success")

        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('register.html')  # Render the registration form

#Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        # Fetch user from database
        user = db.execute("SELECT * FROM users WHERE LOWER( username) = ?", (username,)).fetchone()

        if user is None:
            db.close()
            flash("Username does not exist!", "warning")
            return render_template('login.html')

        # Check hashed password
        if not check_password_hash(user['password'], password):
            db.close()
            flash("Incorrect password!", "danger")
            return render_template('login.html')

        # Successful login
        session['user_id'] = user['id']
        session['username'] = user['username']
        db.close()
        flash("Logged in successfully!", "success")
        return redirect(url_for('main.dashboard')) 

    return render_template('login.html')  # Render the login form

#Logout route
@main.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('main.login'))