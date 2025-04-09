from dash import Dash
import dash_bootstrap_components as dbc
from db import init_db, get_products, import_products_from_csv
import os

# Initialize the database (creates tables if needed)
init_db()

# Import sample products if the database is empty
products = get_products()
if not products["Home"]:  # Check if no products exist
    sample_file = "products.csv"
    if os.path.exists(sample_file):
        print(f"Importing sample products from {sample_file}")
        import_products_from_csv(sample_file)
    else:
        print(f"Warning: {sample_file} not found. Please create it to import sample products.")

# Load products from the database
products = get_products()

# Create the Dash app
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "POS System"

# Import these after creating app to avoid circular imports
from layout import get_layout
from callbacks import register_callbacks

# Set the app layout using the products data
app.layout = get_layout(products)

# Register all callbacks with the app
register_callbacks(app, products)

if __name__ == "__main__":
    app.run_server(debug=True)