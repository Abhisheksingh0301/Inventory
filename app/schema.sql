-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS purchases;
-- DROP TABLE IF EXISTS sales;
-- DROP TABLE IF EXISTS suppliers;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    item_size TEXT,
    description TEXT,
    hsn_code TEXT DEFAULT "None",
    gst_rate REAL NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    entry_date DATE DEFAULT (DATE('now')),
    UNIQUE (name, brand, item_size, description)  -- ✅ Composite unique constraint
);

CREATE TABLE IF NOT EXISTS purchases (
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
    tax_status TEXT DEFAULT 'Taxable', -- Tax status: 'taxable', 'exempt', 'zero-rated'
    entry_date DATE DEFAULT (DATE('now')), -- Date the record was entered
    FOREIGN KEY (product_id) REFERENCES products(id), -- Ensures valid product
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) -- Ensures valid supplier
);


CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL, -- References customers table
    quantity INTEGER NOT NULL,
    sale_price REAL NOT NULL,
    taxable_value REAL NOT NULL, -- Total taxable value (quantity * sale_price - discount)
    cgst_rate REAL DEFAULT 0, -- CGST rate (e.g., 9% as 9.0)
    cgst_amount REAL DEFAULT 0, -- CGST amount
    sgst_rate REAL DEFAULT 0, -- SGST rate (e.g., 9% as 9.0)
    sgst_amount REAL DEFAULT 0, -- SGST amount
    igst_rate REAL DEFAULT 0, -- IGST rate (e.g., 18% as 18.0)
    igst_amount REAL DEFAULT 0, -- IGST amount
    discount_amount REAL DEFAULT 0, -- Discount applied
    invoice_number TEXT NOT NULL, -- Invoice number for the sale
    invoice_date TEXT NOT NULL, -- Date of the sales invoice
    sale_date TEXT NOT NULL, -- Date of sale in 'YYYY-MM-DD' format
    place_of_supply TEXT NOT NULL, -- State code for place of supply (e.g., 'MH')
    tax_status TEXT DEFAULT 'Taxable', -- Tax status: 'taxable', 'exempt', 'zero-rated'
    sale_type TEXT DEFAULT 'Cash', -- Type of sale: 'cash', 'credit', 'online'
    status TEXT DEFAULT 'Completed', -- Status: 'completed', 'returned', 'cancelled'
    entry_date DATE DEFAULT (DATE('now')), -- Date the record was entered
    FOREIGN KEY (product_id) REFERENCES products(id),
    CHECK (quantity > 0),
    CHECK (sale_price > 0),
    CHECK (taxable_value >= 0),
    CHECK (discount_amount >= 0)
);

-- Suggested indexes for performance
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_sales_invoice_number ON sales(invoice_number);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gstin TEXT NOT NULL, -- Supplier's GSTIN
    name TEXT NOT NULL, -- Supplier name
    address TEXT, -- Supplier address
    state_code TEXT NOT NULL -- State code for GST (e.g., 'MH')
);


--Table for user authentications
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


