# Dashboard.py

import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from models import Trade


def init_dashboard(flask_app):
    # Create a Dash instance that is bound to the Flask server
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/'
    )

    # Define the layout for the Dash app
    dash_app.layout = html.Div([
        html.H1("Trading Dashboard"),
        dcc.Graph(id='net-pl-graph'),
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update every 5000 milliseconds (5 seconds)
            n_intervals=0
        )
    ])

    # Define a callback to update the graph every 5 seconds
    @dash_app.callback(
        Output('net-pl-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph(n_intervals):
        # Use the Flask app context to query the database
        with flask_app.app_context():
            trades = Trade.query.order_by(Trade.trade_date).all()

        # Prepare x (trade dates) and y (net profit/loss) values for the chart
        x_values = [trade.trade_date for trade in trades]
        y_values = [trade.net_pl for trade in trades]

        # Create a Plotly scatter trace (line + markers)
        trace = go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name='Net P/L'
        )
        layout = go.Layout(
            title="Net Profit/Loss Over Time",
            xaxis={'title': 'Trade Date'},
            yaxis={'title': 'Net P/L'}
        )
        return {'data': [trace], 'layout': layout}

    return dash_app
