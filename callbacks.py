import json
from dash import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash import html
from layout import create_product_button_content, popular_product_buttons
from db import record_product_sale


def register_callbacks(app, products):
    # Event pricing toggle callback
    @app.callback(
        [Output("event-pricing-active", "data"),
         Output("event-pricing-button", "color")],
        Input("event-pricing-button", "n_clicks"),
        State("event-pricing-active", "data"),
        prevent_initial_call=True
    )
    def toggle_event_pricing(n_clicks, current_state):
        if n_clicks is None:
            return current_state, "secondary"
        new_state = not current_state
        return new_state, "primary" if new_state else "secondary"

    # New callback to update all product button contents
    @app.callback(
        Output({"type": "product-button", "category": ALL, "name": ALL}, "children"),
        Input("event-pricing-active", "data"),
        prevent_initial_call=True
    )
    def update_all_button_prices(event_pricing_active):
        updated_buttons = []
        for category in products:
            for name, price, sku, stock, prod_id in products[category]:
                button_content = create_product_button_content(
                    name, price, sku, stock, event_pricing_active
                )
                updated_buttons.append(button_content)
        return updated_buttons

    # Callback to refresh the popular products display
    @app.callback(
        Output("popular-products-container", "children"),
        Input("refresh-trigger", "data"),
        prevent_initial_call=True
    )
    def refresh_popular_products(refresh_trigger):
        # This forces a re-fetch of popular products from the database
        return popular_product_buttons(products)

    def get_product_price(category, name, event_pricing_active):
        """Helper function to get product price with event pricing adjustment"""
        for prod_name, price, sku, stock, prod_id in products[category]:
            if prod_name == name:
                return price * 1.1 if event_pricing_active else price
        return None

    @app.callback(
        [Output("order-store", "data"),
         Output("refresh-trigger", "data")],
        [Input({"type": "product-button", "category": ALL, "name": ALL}, "n_clicks"),
         Input("pay-button", "n_clicks"),
         Input({"type": "remove-button", "index": ALL}, "n_clicks"),
         Input("event-pricing-active", "data")],
        [State("order-store", "data"),
         State("refresh-trigger", "data")],
        prevent_initial_call=True,
    )
    def update_order(prod_n_clicks, pay_n_clicks, remove_n_clicks, event_pricing_active, current_order, refresh_trigger):
        ctx = callback_context
        if not ctx.triggered:
            return current_order, refresh_trigger

        triggered_prop = ctx.triggered[0]["prop_id"]
        triggered_id_str = triggered_prop.split(".")[0]

        # If event pricing state changed, update all prices in current order
        if triggered_id_str == "event-pricing-active":
            if not current_order:
                return current_order, refresh_trigger
            updated_order = []
            for item in current_order:
                new_price = get_product_price(item["category"], item["name"], event_pricing_active)
                updated_item = item.copy()
                updated_item["price"] = new_price
                updated_order.append(updated_item)
            return updated_order, refresh_trigger

        if triggered_id_str == "pay-button":
            # Record sales before clearing the order
            for item in current_order:
                # Find product ID based on category and name
                for prod_name, price, sku, stock, prod_id in products[item["category"]]:
                    if prod_name == item["name"]:
                        # Record the sale with quantity
                        record_product_sale(prod_id, item.get("count", 1))
                        break
            
            # Increment refresh trigger to update popular products
            return [], refresh_trigger + 1  # Clear order and trigger refresh

        try:
            btn_id = json.loads(triggered_id_str)
        except Exception as e:
            print("Error parsing triggered id:", e)
            return current_order, refresh_trigger

        btn_type = btn_id.get("type", None)
        updated_order = current_order.copy()

        if btn_type == "product-button":
            cat = btn_id["category"]
            name = btn_id["name"].replace('_', '.')  # Convert underscores back to dots

            # Look up the product details from the database results
            product_info = None
            for prod_name, price, sku, stock, prod_id in products[cat]:
                if prod_name == name:
                    # Apply event pricing if active
                    adjusted_price = price * 1.1 if event_pricing_active else price
                    product_info = {"name": name, "price": adjusted_price, "sku": sku, "stock": stock}
                    break

            if not product_info:
                return updated_order, refresh_trigger

            # Check for duplicates and update the count
            found = False
            for item in updated_order:
                if item["name"] == name:
                    if item["count"] < product_info["stock"]:  # Check stock level
                        item["count"] += 1
                    found = True
                    break
            if not found and product_info["stock"] > 0:  # Only add if stock available
                updated_order.append({
                    "category": cat,
                    "name": name,
                    "price": product_info["price"],
                    "sku": product_info["sku"],
                    "count": 1
                })
            return updated_order, refresh_trigger

        elif btn_type == "remove-button":
            remove_index = btn_id["index"]
            if 0 <= remove_index < len(updated_order):
                if updated_order[remove_index].get("count", 1) > 1:
                    updated_order[remove_index]["count"] -= 1
                else:
                    del updated_order[remove_index]
            return updated_order, refresh_trigger

        return updated_order, refresh_trigger

    @app.callback(
        [Output("order-list", "children"),
         Output("order-total", "children")],
        [Input("order-store", "data")]
    )
    def update_order_display(order):
        if not order:
            return "No items selected.", "Total: £0.00"

        item_components = []
        for i, item in enumerate(order):
            unit_price = item["price"]
            count = item.get("count", 1)
            subtotal = unit_price * count
            item_row = dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            f"{i + 1}. {item['name']} (x{count})",
                            html.Br(),
                            html.Small(f"SKU: {item['sku']} - £{unit_price:.2f} each"),
                            html.Br(),
                            html.Small(f"Subtotal: £{subtotal:.2f}")
                        ]),
                        width=8
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Remove",
                            id={"type": "remove-button", "index": i},
                            color="danger",
                            size="sm",
                            n_clicks=0
                        ),
                        width=4,
                        style={"textAlign": "right"}
                    )
                ],
                align="center",
                style={"marginBottom": "5px"}
            )
            item_components.append(item_row)

        total = sum(item["price"] * item.get("count", 1) for item in order)
        return item_components, f"Total: £{total:.2f}"