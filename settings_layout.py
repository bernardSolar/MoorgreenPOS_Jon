from dash import html, dcc
import dash_bootstrap_components as dbc


def create_category_management():
    """Create the category management section of the settings tab."""
    return html.Div([
        html.H4("Category Management", className="mb-4"),

        # Category Table with scrolling
        html.Div([
            html.Div([
                dbc.Table(
                    id="category-table",
                    children=[
                        html.Thead([
                            html.Tr([
                                html.Th("Category Name"),
                                html.Th("No. of Products"),
                                html.Th("Created Date"),
                                html.Th("Actions")
                            ])
                        ]),
                        html.Tbody(id="category-table-body")
                    ],
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="mb-4"
                )
            ], style={
                "maxHeight": "400px",
                "overflowY": "auto",
                "border": "1px solid #dee2e6",
                "borderRadius": "5px"
            })
        ]),

        # Add Category Form
        dbc.Form([
            html.H5("Add New Category"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id="new-category-name",
                        type="text",
                        placeholder="Enter category name",
                        className="mb-2"
                    ),
                    dbc.Button(
                        "Add Category",
                        id="add-category-button",
                        color="primary",
                        className="mt-2"
                    )
                ], width=6)
            ])
        ])
    ])


def create_product_management():
    """Create the product management section of the settings tab."""
    return html.Div([
        html.H4("Product Management", className="mb-4"),

        # Product Table with scrolling
        html.Div([
            dbc.Table(
                id="product-table",
                children=[
                    html.Thead([
                        html.Tr([
                            html.Th("Product Name"),
                            html.Th("Category"),
                            html.Th("Price"),
                            html.Th("SKU"),
                            html.Th("Stock"),
                            html.Th("Actions")
                        ])
                    ]),
                    html.Tbody(id="product-table-body")
                ],
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-4"
            )
        ], style={
            "maxHeight": "400px",
            "overflowY": "auto",
            "border": "1px solid #dee2e6",
            "borderRadius": "5px",
            "marginBottom": "20px"
        }),

        # Add/Edit Product Form
        dbc.Form([
            html.H5("Add/Edit Product"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Product Name"),
                    dbc.Input(id="product-name-input", type="text", className="mb-2"),

                    dbc.Label("Category"),
                    dbc.Select(id="product-category-select", className="mb-2"),

                    dbc.Label("Price"),
                    dbc.Input(id="product-price-input", type="number", step="0.01", className="mb-2"),

                    dbc.Label("SKU"),
                    dbc.Input(id="product-sku-input", type="text", className="mb-2"),

                    dbc.Label("Stock"),
                    dbc.Input(id="product-stock-input", type="number", className="mb-2"),

                    dbc.Button(
                        "Add Product",
                        id="add-product-button",
                        color="primary",
                        className="mt-2 me-2"
                    ),
                    dbc.Button(
                        "Clear Form",
                        id="clear-product-form-button",
                        color="secondary",
                        className="mt-2"
                    ),
                    # Hidden input for product ID when editing
                    dbc.Input(id="product-id-input", type="hidden")
                ], width=6)
            ])
        ])
    ])


def create_settings_layout():
    """Create the complete settings tab layout."""
    return dbc.Container([
        html.Div(id="dummy-output", style={"display": "none"}),

        dbc.Tabs([
            dbc.Tab(
                create_category_management(),
                label="Category Management",
                tab_id="category-management"
            ),
            dbc.Tab(
                create_product_management(),
                label="Product Management",
                tab_id="product-management"
            )
        ], id="settings-tabs", active_tab="category-management"),

        # Simple confirmation modal
        dbc.Modal([
            dbc.ModalHeader("Confirm Deletion"),
            dbc.ModalBody("Are you sure you want to delete this item?"),
            dbc.ModalFooter([
                dbc.Button("No", id="modal-no", className="ms-auto"),
                dbc.Button("Yes", id="modal-yes", color="danger"),
            ])
        ], id="confirm-modal", is_open=False),

        # Toast for notifications
        dbc.Toast(
            id="settings-toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350}
        ),

        # Store component to track what's being deleted
        dcc.Store(id="delete-store"),
        dcc.Store(id="delete-confirm", data=None)
    ])