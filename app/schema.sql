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
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each purchase
    product_id INTEGER NOT NULL, -- References the products table
    supplier_id INTEGER NOT NULL, -- References the suppliers table for supplier details (e.g., GSTIN)
    quantity INTEGER NOT NULL, -- Number of units purchased
    purchase_price REAL NOT NULL, -- Price per unit before tax
    taxable_value REAL NOT NULL, -- Total taxable value (quantity * purchase_price)
    cgst_rate REAL DEFAULT 0, -- CGST rate (e.g., 9% as 9.0)
    cgst_amount REAL DEFAULT 0, -- CGST amount for the purchase
    sgst_rate REAL DEFAULT 0, -- SGST rate (e.g., 9% as 9.0)
    sgst_amount REAL DEFAULT 0, -- SGST amount for the purchase
    igst_rate REAL DEFAULT 0, -- IGST rate (e.g., 18% as 18.0)
    igst_amount REAL DEFAULT 0, -- IGST amount for the purchase
    invoice_number TEXT NOT NULL, -- Supplier's invoice number
    invoice_date TEXT NOT NULL, -- Date of supplier's invoice
    purchase_date TEXT NOT NULL, -- Date of purchase
    place_of_supply TEXT NOT NULL, -- State code for place of supply (e.g., 'MH' for Maharashtra)
    is_reverse_charge BOOLEAN DEFAULT FALSE, -- Flag for reverse charge mechanism
    tax_status TEXT DEFAULT 'taxable', -- Tax status: 'taxable', 'exempt', 'zero-rated'
    entry_date DATE DEFAULT (DATE('now')), -- Date the record was entered
    FOREIGN KEY (product_id) REFERENCES products(id), -- Ensures valid product
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) -- Ensures valid supplier
);


CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_price REAL NOT NULL,
    sale_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gstin TEXT NOT NULL, -- Supplier's GSTIN
    name TEXT NOT NULL, -- Supplier name
    address TEXT, -- Supplier address
    state_code TEXT NOT NULL -- State code for GST (e.g., 'MH')
);

