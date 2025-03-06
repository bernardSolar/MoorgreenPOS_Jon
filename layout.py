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
        style={
            "height": "100px",
            "textAlign": "center",
            "whiteSpace": "normal",
            "padding": "8px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
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

def get_layout(products):
    """Return the complete Dash layout using the products data."""
    tabs = []
    for category in products.keys():
        if category == "Home":
            tab_content = html.Div(
                all_product_buttons(products),
                style={
                    "padding": "5px",
                    "overflowY": "auto",
                    "maxHeight": "600px",
                    "width": "100%"
                }
            )
        else:
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