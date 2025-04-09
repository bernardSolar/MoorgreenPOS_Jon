from dash import Dash
import dash_bootstrap_components as dbc
from db import init_db, get_products, import_products_from_csv
import os
import flask

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
server = flask.Flask(__name__)
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    server=server,
    suppress_callback_exceptions=True
)
app.title = "POS System"

# Import these after creating app to avoid circular imports
from layout import get_layout
from callbacks import register_callbacks

# We'll use a function to generate the layout, which lets us check URL parameters
def serve_layout():
    # Check if event parameter is in URL query string
    event_pricing_active = False
    
    # Get flask's request context
    if flask.has_request_context():
        args = flask.request.args
        event_param = args.get('event')
        if event_param == '1':
            event_pricing_active = True
    
    # Get the layout with the appropriate event_pricing_active value
    return get_layout(products, event_pricing_active)

# Set the app layout using a function so we can check URL parameters
app.layout = serve_layout

# Register all callbacks with the app
register_callbacks(app, products)

if __name__ == "__main__":
    app.run_server(debug=True)