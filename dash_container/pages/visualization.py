# import dash_ag_grid as dag
# import requests
import os
from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from crate import client

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

CRATE_HOST = os.getenv("CRATE_HOST", "localhost")
# CRATE_HOST = "crate"


def get_cratedb_tables():
    query = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'mtopeniot';"""
    with client.connect(f"{CRATE_HOST}:4200", username="crate") as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # Get the list of data
        data = [table[0] for table in data]
    return data


def max_date():
    return datetime.now().date()


tables = get_cratedb_tables()

layout = html.Div(
    [
        html.P("GRAPH"),
        dcc.Dropdown(
            id="vis-type-dropdown-menu",
            placeholder="Select a type of device",
            options=tables,
        ),
        dcc.Dropdown(
            id="vis-entity-dropdown-menu",
            placeholder="Select entities",
            multi=True,
        ),
        dcc.Dropdown(
            id="vis-attr-dropdown-menu",
            placeholder="Select an attribute",
            multi=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dmc.DateRangePicker(
                            id="date-range-picker",
                            inputFormat="DD-MM-YYYY",
                            label="Date Range",
                            maxDate=max_date(),
                            value=[
                                max_date() - timedelta(days=7),
                                max_date(),
                            ],
                            style={"width": 210},
                        ),
                        html.Div(
                            [
                                html.Br(),
                                # Create a text label as header which will be centered
                                html.Label(
                                    "Frequency",
                                    style={
                                        "text-align": "center",
                                        "font-weight": "bold",
                                    },
                                ),
                                dbc.RadioItems(
                                    id="radios",
                                    className="btn-group",
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-primary",
                                    labelCheckedClassName="active",
                                    options=[
                                        {"label": "5min", "value": 1},
                                        {"label": "15min", "value": 2},
                                        {"label": "1h", "value": 3},
                                        {"label": "d", "value": 4},
                                    ],
                                    value=1,
                                ),
                            ],
                            className="radio-group",
                        ),
                    ],
                ),
                dbc.Col(
                    dbc.Button(
                        id="vis-update-button",
                        children="Update",
                        color="primary",
                        style={"width": 330},
                    ),
                ),
            ],
            align="center",
        ),
        dbc.Fade(
            is_in=False,
            id="fade",
            children=dcc.Graph(id="graph"),
        ),
    ]
)


# Callback to change is_in property of fade component when the user update graph
@callback(
    Output("fade", "is_in"),
    Input("graph", "figure"),
)
def update_fade(figure):
    if figure is None:
        raise PreventUpdate
    return True


# Callback to get the list of entities of the selected table for vis-entity-dropdown-menu
@callback(
    Output("vis-entity-dropdown-menu", "options"),
    Input("vis-type-dropdown-menu", "value"),
)
# Get the list of unique entities of the selected table
def get_cratedb_entities(table):
    if table is None:
        raise PreventUpdate
    query = f"""SELECT entity_id FROM \"mtopeniot\".\"{table}\";"""
    with client.connect(f"{CRATE_HOST}:4200", username="crate") as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # Get the list of unique entities
        data = [entity[0] for entity in data]
        data = list(set(data))
    return [{"label": entity, "value": entity} for entity in data]


@callback(
    Output("vis-attr-dropdown-menu", "options"),
    Input("vis-entity-dropdown-menu", "value"),
    Input("vis-type-dropdown-menu", "value"),
)
# Get the list of attributes of the selected table that are numeric
def get_cratedb_attributes(entity_id, table):
    if entity_id is None or table is None:
        raise PreventUpdate
    query = f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND data_type = 'real';"""
    with client.connect(f"{CRATE_HOST}:4200", username="crate") as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # Get the list of data
        data = [attr[0] for attr in data]
    return data


# Callback to update the graph data when the user selects an attribute after selecting entities and a table
@callback(
    Output("graph", "figure"),
    Input("vis-update-button", "n_clicks"),
    State("radios", "value"),
    State("date-range-picker", "value"),
    State("vis-attr-dropdown-menu", "value"),
    State("vis-entity-dropdown-menu", "value"),
    State("vis-type-dropdown-menu", "value"),
)
def update_graph(n_clicks, freq, date_range, attr, entities, table):
    # Prevent update when the page is loaded
    if (
        freq is None
        or n_clicks is None
        or date_range is None
        or attr is None
        or entities is None
        or table is None
    ):
        raise PreventUpdate

    # If the user selects more than one attribute or entity, create a graph with different lines for each attribute and entity
    # Get the data from crateDB

    # Create a figure with plotly express. Title will be the attributes selected by the user
    title = "/".join(attr)
    fig = px.line(title=title)

    for entity_id in entities:
        for a in attr:
            query = f"""SELECT time_index, {a} FROM \"mtopeniot\".\"{table}\" WHERE entity_id = '{entity_id}';"""
            with client.connect(f"{CRATE_HOST}:4200", username="crate") as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                data = cursor.fetchall()
            df = pd.DataFrame(
                data,
                columns=[
                    "time_index",
                    a,
                ],
            ).sort_values(by="time_index")
            df["time_index"] = (
                pd.to_datetime(df["time_index"], unit="ms")
                .dt.tz_localize("UTC")
                .dt.tz_convert("Europe/Madrid")
            )
            # Filter df by date_range, consider ms and time zone. Convert df["time_index"] to datetime to compare it with date_range
            df = df[
                (
                    df["time_index"].dt.tz_localize(None)
                    >= datetime.strptime(date_range[0], "%Y-%m-%d")
                )
                & (
                    df["time_index"].dt.tz_localize(None)
                    <= datetime.strptime(date_range[1], "%Y-%m-%d") + timedelta(days=1)
                )
            ]
            # Create a dataframe with a timeindex with the frequency selected by the user
            selected_freq = {1: "5min", 2: "15min", 3: "1h", 4: "1d"}
            dff = pd.DataFrame(
                index=pd.date_range(
                    start=df["time_index"].min().date(),
                    end=df["time_index"].max().date() + timedelta(days=1),
                    freq=selected_freq[freq],
                )
            )
            dff.index = dff.index.tz_localize("Europe/Madrid", ambiguous=True)
            # Resample df by the frequency selected by the user
            df = df.set_index("time_index").resample(selected_freq[freq]).mean()
            # Fill dff with df values
            dff = dff.join(df, how="left")
            # Create the graph with dff
            fig.add_scatter(x=dff.index, y=dff[a], name=f"{entity_id}_{a}")

    return fig
