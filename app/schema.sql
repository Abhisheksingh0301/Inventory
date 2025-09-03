DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS sales;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    item_size TEXT,
    description TEXT,
    hsn_code TEXT,
    gst_rate REAL NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    entry_date DATE DEFAULT (DATE('now')),
    UNIQUE (name, brand, item_size)  -- ✅ Composite unique constraint
);

CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    purchase_price REAL NOT NULL,
    purchase_date TEXT NOT NULL,
    entry_date DATE DEFAULT (DATE('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_price REAL NOT NULL,
    sale_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
