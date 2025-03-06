from dash import Input, Output, State, html, callback_context, ALL, MATCH, no_update
import dash_bootstrap_components as dbc
import json
from dash.exceptions import PreventUpdate
from db import (get_categories, get_products, add_category, delete_category,
               add_product, edit_product, delete_product)

def register_settings_callbacks(app):
    # Category Management Callback
    @app.callback(
        [Output("category-table-body", "children"),
         Output("new-category-name", "value")],
        [Input("add-category-button", "n_clicks"),
         Input("settings-tabs", "active_tab"),
         Input("modal-yes", "n_clicks")],
        [State("new-category-name", "value"),
         State("delete-confirm", "data")],
        prevent_initial_call=False
    )
    def update_category_table(add_clicks, active_tab, yes_clicks, new_category, delete_target):
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"] if ctx.triggered else None
        
        # Handle adding new category
        if triggered_id == "add-category-button.n_clicks" and new_category:
            add_category(new_category)
            new_category = ""  # Clear input
        
        # Handle deletion (no need to check yes_clicks as the execute_deletion callback handles that)
        if triggered_id == "modal-yes.n_clicks" and delete_target and delete_target["type"] == "category":
            delete_category(delete_target["id"])
        
        # Get updated category list
        categories = get_categories()
        rows = []
        for cat_id, name, is_custom, created_at, product_count in categories:
            delete_button = dbc.Button(
                "Delete",
                id={"type": "delete-category", "index": cat_id},
                color="danger",
                size="sm",
                disabled=not is_custom or product_count > 0
            ) if is_custom else html.Span("-")
            
            rows.append(html.Tr([
                html.Td(name),
                html.Td(product_count),
                html.Td(created_at if is_custom else "built-in"),
                html.Td(delete_button)
            ]))
            
        return rows, new_category or ""

    # Modal Control Callback
    @app.callback(
        Output("confirm-modal", "is_open"),
        [Input({"type": "delete-category", "index": ALL}, "n_clicks"),
         Input("modal-yes", "n_clicks"),
         Input("modal-no", "n_clicks")],
        [State("confirm-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_modal(delete_clicks, yes_clicks, no_clicks, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return False
            
        trigger_id = ctx.triggered[0]["prop_id"]
        
        # Only open modal if a delete button was explicitly clicked
        if '"type":"delete-category"' in trigger_id:
            # Check if any delete button was actually clicked
            if any(click for click in delete_clicks if click):
                return True
            return False
            
        # Close modal when Yes/No is clicked
        if trigger_id in ["modal-yes.n_clicks", "modal-no.n_clicks"]:
            return False
            
        return is_open

    # Deletion Handling Callback
    @app.callback(
        Output("delete-confirm", "data"),
        [Input({"type": "delete-category", "index": ALL}, "n_clicks")],
        prevent_initial_call=True
    )
    def store_delete_target(delete_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return None
            
        trigger_id = ctx.triggered[0]["prop_id"]
        try:
            if '"type":"delete-category"' in trigger_id:
                cat_id = json.loads(trigger_id.split(".")[0])["index"]
                return {"type": "category", "id": cat_id}
        except:
            pass
        return None

    # Execute Deletion Callback
    @app.callback(
        Output("dummy-output", "children"),
        [Input("modal-yes", "n_clicks")],
        [State("delete-confirm", "data")],
        prevent_initial_call=True
    )
    def execute_deletion(yes_clicks, target):
        if not yes_clicks or not target:
            raise PreventUpdate
            
        if target["type"] == "category":
            delete_category(target["id"])
            
        return ""

    # Combined Product Management Callback
    @app.callback(
        [Output("product-table-body", "children"),
         Output("product-name-input", "value"),
         Output("product-category-select", "value"),
         Output("product-price-input", "value"),
         Output("product-sku-input", "value"),
         Output("product-stock-input", "value")],
        [Input("add-product-button", "n_clicks"),
         Input("clear-product-form-button", "n_clicks"),
         Input("settings-tabs", "active_tab")],
        [State("product-name-input", "value"),
         State("product-category-select", "value"),
         State("product-price-input", "value"),
         State("product-sku-input", "value"),
         State("product-stock-input", "value")],
        prevent_initial_call=False
    )
    def handle_product_operations(add_clicks, clear_clicks, active_tab, 
                                name, category, price, sku, stock):
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"] if ctx.triggered else None

        # Initialize form values
        form_values = [name, category, price, sku, stock]

        # Clear form
        if triggered_id == "clear-product-form-button.n_clicks":
            form_values = ["", None, "", "", ""]

        # Add product
        if triggered_id == "add-product-button.n_clicks":
            if all([name, category, price, sku, stock]):  # Ensure all fields are filled
                try:
                    # Convert price and stock to appropriate types
                    price_float = float(price)
                    stock_int = int(stock)
                    
                    # Add product to database - ensure correct parameter order
                    success = add_product(category, name, price_float, sku, stock_int)
                    
                    if success:
                        # Clear form after successful addition
                        form_values = ["", None, "", "", ""]
                except ValueError:
                    pass

        # Get updated product list
        products = get_products()
        rows = []
        for category in products:
            if category != "Home":
                for name, price, sku, stock, prod_id in products[category]:
                    rows.append(html.Tr([
                        html.Td(name),
                        html.Td(category),
                        html.Td(f"£{price:.2f}"),
                        html.Td(sku),
                        html.Td(stock),
                        html.Td([
                            dbc.Button(
                                "Edit",
                                id={"type": "edit-product", "index": prod_id},
                                color="primary",
                                size="sm",
                                className="me-2"
                            ),
                            dbc.Button(
                                "Delete",
                                id={"type": "delete-product", "index": prod_id},
                                color="danger",
                                size="sm"
                            )
                        ])
                    ]))

        # Return table and form values
        return [rows] + form_values

    # Category Dropdown Callback
    @app.callback(
        Output("product-category-select", "options"),
        [Input("settings-tabs", "active_tab")],
        prevent_initial_call=False
    )
    def update_category_dropdown(active_tab):
        categories = get_categories()
        return [{"label": name, "value": cat_id} 
                for cat_id, name, _, _, _ in categories] 