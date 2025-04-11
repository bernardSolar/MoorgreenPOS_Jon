from dash import dcc, html
import dash_bootstrap_components as dbc
from db import get_popular_products

def create_product_button_content(name, price, sku, stock, event_pricing_active=False):
    """Create the content for a product button."""
    display_price = price * 1.1 if event_pricing_active else price
    # No break between name and price - all in one div with left alignment
    return html.Div([
        html.Strong(name, style={"fontSize": "14px", "color": "black"}),
        html.Br(),
        html.Span(f"£{display_price:.2f}", style={"fontSize": "14px", "color": "black"})
    ], style={"textAlign": "left"})

def product_button(name, price, sku, stock, prod_id, category, event_pricing_active=False):
    """Create a single product button with consistent sizing."""
    # Apply event pricing to the actual price here
    display_price = price * 1.1 if event_pricing_active else price
    button_id = {"type": "product-button", "category": category, "name": name.replace('.', '_')}
    
    return dbc.Button(
        children=html.Div([
            html.Strong(name, style={"fontSize": "14px", "color": "black"}),
            html.Br(),
            html.Span(f"£{display_price:.2f}", style={"fontSize": "14px", "color": "black"})
        ], style={"textAlign": "left"}),
        id=button_id,
        color="light",
        outline=True,
        style={
            "height": "90px",  # Slightly smaller height for the 6-button layout
            "whiteSpace": "normal",
            "padding": "8px",  # Reduced padding
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "flex-start",  # Left alignment
            "width": "100%",
            "borderColor": "#ccc",
            "backgroundColor": "#f8f9fa"
        },
        n_clicks=0,
    )

def create_product_grid(products, category, event_pricing_active=False):
    """Create a grid of product buttons with 6 per row."""
    items = list(products[category])
    rows = []
    
    # Process 6 items per row (changed from 5)
    for i in range(0, len(items), 6):
        current_row = items[i:i+6]
        buttons = []
        
        # Create button for each product
        for name, price, sku, stock, prod_id in current_row:
            buttons.append(
                html.Div(
                    product_button(name, price, sku, stock, prod_id, category, event_pricing_active),
                    style={"width": "16.666%", "padding": "2px", "boxSizing": "border-box"},  # Changed from 20% to 16.666%
                    className="d-inline-block"
                )
            )
            
        # Add empty placeholders if row isn't complete
        for _ in range(6 - len(current_row)):  # Changed from 5 to 6
            buttons.append(
                html.Div(
                    style={"width": "16.666%", "padding": "2px", "boxSizing": "border-box"},  # Changed from 20% to 16.666%
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

def product_buttons(products, category, event_pricing_active=False):
    """Return a grid of product buttons for the given category."""
    return create_product_grid(products, category, event_pricing_active)

def all_product_buttons(products, event_pricing_active=False):
    """Return a grid of buttons for all products."""
    return create_product_grid(products, "Home", event_pricing_active)

def popular_product_buttons(products, refresh_trigger=None, event_pricing_active=False):
    """Return a grid of buttons for popular products."""
    # Get popular products from database
    popular_products = get_popular_products(days=90, limit=15)
    
    # If no sales data yet, use first 15 products from Home
    if not popular_products:
        popular_products = products["Home"][:15]
    
    # Create a dictionary with the popular products for the grid function
    popular_dict = {"Home": popular_products}
    
    return create_product_grid(popular_dict, "Home", event_pricing_active)

def get_home_content(products, event_pricing_active=False):
    """Get the content for the Home tab with popular products."""
    return html.Div(
        [
            html.H5("Most Popular Products", 
                   style={"marginBottom": "10px", "marginTop": "10px", "paddingLeft": "10px"}),
            html.Div(
                popular_product_buttons(products, None, event_pricing_active),
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

def get_category_content(products, category, event_pricing_active=False):
    """Get the content for a specific category tab."""
    return html.Div(
        product_buttons(products, category, event_pricing_active),
        style={
            "padding": "5px",
            "overflowY": "auto",
            "maxHeight": "600px",
            "width": "100%"
        }
    )

def get_layout(products, event_pricing_active=False):
    """Return the complete Dash layout using the products data."""
    # Create a separate function for each category's content to allow for tab refreshes
    category_contents = {
        "Home": get_home_content(products, event_pricing_active)
    }
    
    # Add content for other categories
    for category in products.keys():
        if category != "Home":
            category_contents[category] = get_category_content(products, category, event_pricing_active)
    
    # Custom tab style with smaller black font
    tab_style = {
        'padding': '8px',
        'fontWeight': 'normal',
        'fontSize': '12px',  # Smaller font size
        'color': 'black',    # Black text
        'whiteSpace': 'nowrap'  # Ensures text stays on one line
    }
    
    # Create tabs with custom styling
    tabs = []
    for category, content in category_contents.items():
        tabs.append(dcc.Tab(
            label=category,
            value=category,
            children=content,
            style=tab_style,  # Apply custom style to each tab
            selected_style={
                **tab_style,  # Keep the same base style
                'borderTop': '1px solid #d6d6d6',
                'borderBottom': '1px solid white',
                'fontWeight': 'bold'
            }
        ))

    # Create event button independently to control position
    event_button = dbc.Button(
        "Event",
        id="event-pricing-button",
        # Use magenta color when active instead of primary (blue)
        color="#e83e8c" if event_pricing_active else "secondary",
        style={
            "width": "120px",
            # Additional custom styling for the button
            "backgroundColor": "#e83e8c" if event_pricing_active else "#6c757d",
            "borderColor": "#e83e8c" if event_pricing_active else "#6c757d"
        }
    )

    # Create order placement button
    place_order_button = dbc.Button(
        "Place Order",
        id="pay-button",
        color="success",
        style={"width": "100%"}
    )

    layout = dbc.Container(
        [
            dcc.Store(id="order-store", data=[]),
            dcc.Store(id="event-pricing-active", data=event_pricing_active),  # Initialize with passed value
            dcc.Store(id="refresh-trigger", data=0),  # Added to trigger home screen refresh
            
            # Main content row - products and order summary
            dbc.Row(
                [
                    # Left side - product tabs
                    dbc.Col(
                        dcc.Tabs(
                            id="category-tabs",
                            value="Home",
                            children=tabs,
                            # Additional tab container styling
                            style={'height': '44px'},  # Control overall tab bar height
                            content_style={'padding': '0px'}  # Remove content padding
                        ),
                        width=8,
                        className="pe-1"
                    ),
                    
                    # Right side - order summary
                    dbc.Col(
                        html.Div(
                            [
                                # Order header and list
                                html.Div([
                                    # Simple header bar - all in one row
                                    dbc.Row(
                                        [
                                            # Order Summary heading
                                            dbc.Col(
                                                html.H4("Order Summary",
                                                      style={"margin": "0", "paddingTop": "5px"}),
                                                width=5,
                                            ),
                                            # Total display
                                            dbc.Col(
                                                html.H4(
                                                    id="order-total-top", 
                                                    children="Total: £0.00", 
                                                    style={"margin": "0", "paddingTop": "5px", "textAlign": "right"}
                                                ),
                                                width=7,
                                            ),
                                        ],
                                        className="py-1 align-items-center g-0",
                                        style={
                                            "backgroundColor": "#f8f9fa", 
                                            "border": "1px solid #ccc", 
                                            "borderRadius": "4px 4px 0 0",
                                            "borderBottom": "none",
                                            "margin": "0",
                                            "width": "100%",
                                            "padding": "0 5px"
                                        }
                                    ),
                                    
                                    # Order list
                                    html.Div(
                                        id="order-list",
                                        style={
                                            "height": "400px",
                                            "border": "1px solid #ccc",
                                            "borderRadius": "0 0 4px 4px",
                                            "padding": "10px",
                                            "overflowY": "auto"
                                        }
                                    )
                                ], style={"width": "100%"}),
                                
                                # Order total
                                html.H4(id="order-total", children="Total: £0.00", style={"marginTop": "10px"}),
                                
                                # Place order button
                                dbc.Row(
                                    [
                                        dbc.Col(place_order_button, width=12)
                                    ],
                                    className="mt-2"
                                ),
                            ]
                        ),
                        width=4,
                        className="ps-1"
                    ),
                ],
                align="start",
                style={"marginTop": "5px"}
            ),
            
            # Separate row for event button - positioned at very bottom
            dbc.Row(
                [
                    # Event button on left
                    dbc.Col(
                        event_button,
                        width={"size": 1, "offset": 0},
                        className="mt-2"
                    ),
                    # Empty space
                    dbc.Col(width=11)
                ],
                className="mt-2"
            ),
        ],
        fluid=True
    )
    return layout