from dash import dcc, html
import dash_bootstrap_components as dbc

def create_product_button_content(name, price, sku, stock, event_pricing_active=False):
    """Create the content for a product button."""
    display_price = price * 1.1 if event_pricing_active else price
    return [
        html.Strong(name),
        html.Br(),
        f"£{display_price:.2f}"
    ]

def product_button(name, price, sku, stock, prod_id, category):
    """Create a single product button with consistent sizing."""
    button_id = {"type": "product-button", "category": category, "name": name.replace('.', '_')}
    return dbc.Button(
        children=create_product_button_content(name, price, sku, stock),
        id=button_id,
        color="primary",
        outline=True,
        className="w-100 h-100",
        style={
            "height": "100px",      # Fixed height
            "textAlign": "center",  # Center aligned text
            "whiteSpace": "normal",
            "padding": "8px",
            "display": "flex",      # Use flexbox for centering
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center"
        },
        n_clicks=0,
    )

def product_buttons(products, category):
    """Return a grid of product buttons for the given category."""
    buttons = []
    items = list(products[category])
    
    # Process items in groups of 5 for each row
    for i in range(0, len(items), 5):
        row_items = items[i:i+5]
        row = []
        
        for name, price, sku, stock, prod_id in row_items:
            col = dbc.Col(
                product_button(name, price, sku, stock, prod_id, category),
                # Use responsive sizing that adds to 12 (Bootstrap's grid system)
                xs=12, sm=6, md=4, lg=3, xl="auto", 
                className="px-1 py-1"  # Small padding
            )
            row.append(col)
            
        # Add empty columns if row is not complete to maintain equal width
        if len(row_items) < 5:
            for _ in range(5 - len(row_items)):
                row.append(dbc.Col(xs=12, sm=6, md=4, lg=3, xl="auto", className="px-1 py-1"))
                
        buttons.append(dbc.Row(row, className="g-0 w-100"))
        
    return html.Div(buttons, className="w-100")

def all_product_buttons(products):
    """Return a grid of buttons for all products."""
    buttons = []
    items = list(products["Home"])
    
    # Process items in groups of 5 for each row
    for i in range(0, len(items), 5):
        row_items = items[i:i+5]
        row = []
        
        for name, price, sku, stock, prod_id in row_items:
            col = dbc.Col(
                product_button(name, price, sku, stock, prod_id, "Home"),
                # Use responsive sizing
                xs=12, sm=6, md=4, lg=3, xl="auto",
                className="px-1 py-1"  # Small padding
            )
            row.append(col)
            
        # Add empty columns if row is not complete to maintain equal width
        if len(row_items) < 5:
            for _ in range(5 - len(row_items)):
                row.append(dbc.Col(xs=12, sm=6, md=4, lg=3, xl="auto", className="px-1 py-1"))
                
        buttons.append(dbc.Row(row, className="g-0 w-100"))
        
    return html.Div(buttons, className="w-100")

def get_layout(products):
    """Return the complete Dash layout using the products data."""
    tabs = []
    for category in products.keys():
        if category == "Home":
            tab_content = html.Div(
                all_product_buttons(products),
                style={
                    "padding": "10px",
                    "overflowY": "auto",
                    "maxHeight": "600px",
                    "width": "100%"
                }
            )
        else:
            tab_content = html.Div(
                product_buttons(products, category),
                style={
                    "padding": "10px",
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
                                        dbc.Col(html.H4("Order Summary"), width=8),
                                        dbc.Col(
                                            dbc.Button(
                                                "Event",
                                                id="event-pricing-button",
                                                color="secondary",
                                                size="sm",
                                                className="float-end"
                                            ),
                                            width=4
                                        )
                                    ],
                                    className="mb-3"
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