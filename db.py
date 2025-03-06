import sqlite3
import csv
import os
from datetime import datetime
from pathlib import Path

DB_FILE = "products.db"

def init_db():
    """Initialize the SQLite database with products and categories tables."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Create categories table with is_custom and created_at fields
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_custom BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            sku TEXT,
            stock INTEGER DEFAULT 0,
            UNIQUE(sku),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            UNIQUE(category_id, name)
        )
    ''')
    conn.commit()
    conn.close()

# Add new functions for category management
def add_category(name):
    """Add a new custom category."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO categories (name, is_custom) VALUES (?, TRUE)",
            (name,)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding category: {e}")
        return False
    finally:
        conn.close()

def delete_category(category_id):
    """Delete a custom category if it has no products."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        # Check if category is custom and has no products
        cur.execute("""
            SELECT c.is_custom, COUNT(p.id)
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            WHERE c.id = ?
            GROUP BY c.id
        """, (category_id,))
        result = cur.fetchone()
        
        if result and result[0] and result[1] == 0:
            cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return True
        return False
    except sqlite3.Error as e:
        print(f"Error deleting category: {e}")
        return False
    finally:
        conn.close()

# Add new functions for product management
def get_db_connection():
    """Create a connection to the SQLite database."""
    db_path = Path("products.db")
    return sqlite3.connect(db_path)

def add_product(category_id, name, price, sku, stock):
    """Add a new product to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (category_id, name, price, sku, stock)
                VALUES (?, ?, ?, ?, ?)
            """, (category_id, name, price, sku, stock))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error adding product: {e}")
        return False

def edit_product(product_id, name, category_id, price, sku, stock):
    """Edit an existing product."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE products
            SET category_id = ?, name = ?, price = ?, sku = ?, stock = ?
            WHERE id = ?
        """, (category_id, name, price, sku, stock, product_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error editing product: {e}")
        return False
    finally:
        conn.close()

def delete_product(product_id):
    """Delete a product."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting product: {e}")
        return False
    finally:
        conn.close()

def get_categories():
    """Get all categories with their product counts."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.is_custom, c.created_at, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
        ORDER BY c.name
    """)
    categories = cur.fetchall()
    conn.close()
    return categories

# Modify existing functions as needed
def get_products():
    """Load products from the database."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT c.name, p.name, p.price, p.sku, p.stock, p.id
        FROM products p 
        JOIN categories c ON p.category_id = c.id
        ORDER BY c.name, p.name
    """)
    rows = cur.fetchall()
    conn.close()

    products = {"Home": []}
    for category, name, price, sku, stock, prod_id in rows:
        if category not in products:
            products[category] = []
        product_info = (name, price, sku, stock, prod_id)
        products[category].append(product_info)
        products["Home"].append(product_info)
    
    return products

# Add this function to db.py
def import_products_from_csv(filename):
    """Import products from a CSV file."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    try:
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # First, ensure category exists
                cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)",
                          (row['category'],))
                conn.commit()
                
                # Get category_id
                cur.execute("SELECT id FROM categories WHERE name = ?",
                          (row['category'],))
                category_id = cur.fetchone()[0]
                
                # Insert product
                cur.execute("""
                    INSERT OR REPLACE INTO products 
                    (category_id, name, price, sku, stock)
                    VALUES (?, ?, ?, ?, ?)
                """, (category_id, row['name'], float(row['price']), 
                     row.get('sku', None), int(row.get('stock', 0))))
                
        conn.commit()
        return True
    except Exception as e:
        print(f"Error importing products: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
