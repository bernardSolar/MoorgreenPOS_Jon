from dash import dcc, html
import dash_bootstrap_components as dbc

def create_product_button_content(name, price, sku, stock, event_pricing_active=False):
    """Create the content for a product button."""
    display_price = price * 1.1 if event_pricing_active else price
    return [
        f"{name} - £{display_price:.2f}",
        html.Br(),
        html.Small(f"SKU: {sku} | Stock: {stock}")
    ]

def product_button(name, price, sku, stock, prod_id, category):
    """Create a single product button with consistent sizing."""
    button_id = {"type": "product-button", "category": category, "name": name.replace('.', '_')}
    return html.Div([
        dbc.Button(
            children=create_product_button_content(name, price, sku, stock),
            id=button_id,
            color="primary",
            outline=True,
            className="w-100 h-100",
            style={
                "minHeight": "80px",
                "margin": "5px",
                "textAlign": "left",
                "whiteSpace": "normal",
                "padding": "10px"
            },
            n_clicks=0,
        )
    ], id={"type": "button-wrapper", "category": category, "name": name.replace('.', '_')})

def product_buttons(products, category):
    """Return a grid of product buttons for the given category."""
    buttons = []
    row = []

    for name, price, sku, stock, prod_id in products[category]:
        col = dbc.Col(
            product_button(name, price, sku, stock, prod_id, category),
            width=4,
            className="mb-3"
        )
        row.append(col)

        if len(row) == 3:
            buttons.append(dbc.Row(row, className="g-2"))
            row = []

    if row:
        buttons.append(dbc.Row(row, className="g-2"))

    return html.Div(buttons)

def all_product_buttons(products):
    """Return a grid of buttons for all products."""
    buttons = []
    row = []

    for name, price, sku, stock, prod_id in products["Home"]:
        col = dbc.Col(
            product_button(name, price, sku, stock, prod_id, "Home"),
            width=4,
            className="mb-3"
        )
        row.append(col)

        if len(row) == 3:
            buttons.append(dbc.Row(row, className="g-2"))
            row = []

    if row:
        buttons.append(dbc.Row(row, className="g-2"))

    return buttons

def get_layout(products):
    """Return the complete Dash layout using the products data."""
    tabs = []
    for category in products.keys():
        if category == "Home":
            tab_content = html.Div(
                all_product_buttons(products),
                style={
                    "padding": "20px",
                    "overflowY": "auto",
                    "maxHeight": "800px"
                }
            )
        else:
            tab_content = html.Div(
                product_buttons(products, category),
                style={
                    "padding": "20px",
                    "overflowY": "auto",
                    "maxHeight": "800px"
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
                                        "height": "600px",
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
                    ),
                ],
                align="start",
                style={"marginTop": "20px"}
            ),
        ],
        fluid=True
    )
    return layout