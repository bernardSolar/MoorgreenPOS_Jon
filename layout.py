from dash import dcc, html
import dash_bootstrap_components as dbc
from db import get_popular_products

def create_product_button_content(name, price, sku, stock, event_pricing_active=False):
    """Create the content for a product button."""
    display_price = price * 1.1 if event_pricing_active else price
    # No break between name and price - all in one div with left alignment
    return html.Div([
        html.Strong(name),
        html.Br(),
        f"£{display_price:.2f}"
    ], style={"textAlign": "left"})

def product_button(name, price, sku, stock, prod_id, category):
    """Create a single product button with consistent sizing."""
    button_id = {"type": "product-button", "category": category, "name": name.replace('.', '_')}
    return dbc.Button(
        children=create_product_button_content(name, price, sku, stock),
        id=button_id,
        color="primary",
        outline=True,
        style={
            "height": "100px",
            "whiteSpace": "normal",
            "padding": "10px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "flex-start",  # Left alignment
            "width": "100%"
        },
        n_clicks=0,
    )

def create_product_grid(products, category):
    """Create a grid of product buttons with 5 per row."""
    items = list(products[category])
    rows = []
    
    # Process 5 items per row
    for i in range(0, len(items), 5):
        current_row = items[i:i+5]
        buttons = []
        
        # Create button for each product
        for name, price, sku, stock, prod_id in current_row:
            buttons.append(
                html.Div(
                    product_button(name, price, sku, stock, prod_id, category),
                    style={"width": "20%", "padding": "3px", "boxSizing": "border-box"},
                    className="d-inline-block"
                )
            )
            
        # Add empty placeholders if row isn't complete
        for _ in range(5 - len(current_row)):
            buttons.append(
                html.Div(
                    style={"width": "20%", "padding": "3px", "boxSizing": "border-box"},
                    className="d-inline-block"
                )
            )
        
        # Add completed row to rows list
        rows.append(
            html.Div(
                buttons,
                style={"width": "100%", "display": "flex", "flexWrap": "nowrap"}
            )
        )
    
    return html.Div(rows, style={"width": "100%"})

def product_buttons(products, category):
    """Return a grid of product buttons for the given category."""
    return create_product_grid(products, category)

def all_product_buttons(products):
    """Return a grid of buttons for all products."""
    return create_product_grid(products, "Home")

def popular_product_buttons(products, refresh_trigger=None):
    """Return a grid of buttons for popular products."""
    # Get popular products from database
    popular_products = get_popular_products(days=90, limit=15)
    
    # If no sales data yet, use first 15 products from Home
    if not popular_products:
        popular_products = products["Home"][:15]
    
    # Create a dictionary with the popular products for the grid function
    popular_dict = {"Home": popular_products}
    
    return create_product_grid(popular_dict, "Home")

def get_home_content(products, refresh_trigger=None):
    """Get the content for the Home tab with popular products."""
    return html.Div(
        [
            html.H5("Most Popular Products", 
                   style={"marginBottom": "10px", "marginTop": "10px", "paddingLeft": "10px"}),
            html.Div(
                popular_product_buttons(products),
                id="popular-products-container"
            )
        ],
        style={
            "padding": "5px",
            "overflowY": "auto",
            "maxHeight": "600px",
            "width": "100%"
        }
    )

def get_layout(products):
    """Return the complete Dash layout using the products data."""
    tabs = []
    
    # Create the Home tab with popular products
    home_tab_content = get_home_content(products)
    tabs.append(dcc.Tab(label="Home", value="Home", children=home_tab_content))
    
    # Create remaining category tabs
    for category in products.keys():
        if category != "Home":
            tab_content = html.Div(
                product_buttons(products, category),
                style={
                    "padding": "5px",
                    "overflowY": "auto",
                    "maxHeight": "600px",
                    "width": "100%"
                }
            )
            tabs.append(dcc.Tab(label=category, value=category, children=tab_content))

    layout = dbc.Container(
        [
            dcc.Store(id="order-store", data=[]),
            dcc.Store(id="event-pricing-active", data=False),
            dcc.Store(id="refresh-trigger", data=0),  # Added to trigger home screen refresh
            dbc.Row(
                dbc.Col(
                    html.Img(
                        src="/assets/logo.jpg",
                        style={
                            "height": "60px",
                            "marginBottom": "15px",
                            "marginTop": "15px"
                        }
                    ),
                    width={"size": 6, "offset": 0}
                ),
                className="mb-3"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Tabs(
                            id="category-tabs",
                            value="Home",
                            children=tabs,
                        ),
                        width=8,
                        className="pe-1"
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        # Left side - Summary title
                                        dbc.Col(
                                            html.H4("Order Summary", 
                                                   style={"margin": "0", "paddingTop": "6px"}), 
                                            width=6,
                                            className="ps-2"
                                        ),
                                        # Right side with total and event button
                                        dbc.Col(
                                            dbc.Row([
                                                # Total display
                                                dbc.Col(
                                                    html.Div(
                                                        id="order-total-top", 
                                                        children="Total: £0.00", 
                                                        style={
                                                            "fontSize": "16px", 
                                                            "fontWeight": "bold",
                                                            "paddingTop": "8px",
                                                            "paddingRight": "10px",
                                                            "textAlign": "right"
                                                        }
                                                    ),
                                                    width=7,
                                                    className="p-0"
                                                ),
                                                # Event button
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Event",
                                                        id="event-pricing-button",
                                                        color="secondary",
                                                        size="sm",
                                                        className="float-end"
                                                    ),
                                                    width=5,
                                                    className="p-0"
                                                )
                                            ], className="g-0"),
                                            width=6,
                                            className="pe-2"
                                        )
                                    ],
                                    className="mb-3 py-2",
                                    style={"backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6", "borderRadius": "4px"}
                                ),
                                html.Div(
                                    id="order-list",
                                    style={
                                        "height": "400px",
                                        "border": "1px solid #ccc",
                                        "padding": "10px",
                                        "overflowY": "auto"
                                    }
                                ),
                                html.H4(id="order-total", children="Total: £0.00"),
                                dbc.Button(
                                    "Place Order",
                                    id="pay-button",
                                    color="success",
                                    style={"marginTop": "10px", "width": "100%"}
                                ),
                            ]
                        ),
                        width=4,
                        className="ps-1"
                    ),
                ],
                align="start",
                style={"marginTop": "20px"}
            ),
        ],
        fluid=True
    )
    return layout