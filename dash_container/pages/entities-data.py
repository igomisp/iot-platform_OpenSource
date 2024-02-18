# import dash_ag_grid as dag
# import requests
import os
from datetime import datetime, timedelta

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from crate import client

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

# Load CRATE_HOST from .env file


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
    print("actualizando date")
    return datetime.now().date()


def layout():
    tables = get_cratedb_tables()
    return html.Div(
        [
            html.P("DATA"),
            dcc.Dropdown(
                id="table-type-dropdown-menu",
                placeholder="Select a type of device",
                options=tables,
            ),
            dcc.Dropdown(
                id="table-entity-dropdown-menu",
                placeholder="Select entities",
                multi=True,
            ),
            dcc.Dropdown(
                id="table-attr-dropdown-menu",
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
                                            {"label": "raw", "value": 0},
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
                            id="table-update-button",
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
                id="data-table-fade",
                children=dag.AgGrid(
                    id="data-table",
                    className="ag-theme-balham",
                    # columnSize="sizeToFit",
                    defaultColDef={"resizable": True, "sortable": True, "filter": True},
                    dashGridOptions={"pagination": True},
                ),
            ),
        ]
    )


# Callback to change is_in property of fade component when the user update graph
@callback(
    Output("data-table-fade", "is_in"),
    Input("data-table", "rowData"),
)
def update_fade(data):
    if data is None:
        raise PreventUpdate
    return True


# Callback to get the list of entities of the selected table for table-entity-dropdown-menu
@callback(
    Output("table-entity-dropdown-menu", "options"),
    Input("table-type-dropdown-menu", "value"),
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
    Output("table-attr-dropdown-menu", "options"),
    Input("table-entity-dropdown-menu", "value"),
    Input("table-type-dropdown-menu", "value"),
)
# Get the list of attributes of the selected table that are numeric
def get_cratedb_attributes(entity_ids, table):
    if entity_ids is None or table is None:
        raise PreventUpdate
    query = f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND data_type = 'real';"""
    with client.connect(f"{CRATE_HOST}:4200", username="crate") as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        # Get the list of data
        data = [attr[0] for attr in data]
    return data


# Callback to update the data-table when the user selects an attribute after selecting entities and a table
@callback(
    Output("data-table", "columnDefs"),
    Output("data-table", "rowData"),
    Input("table-update-button", "n_clicks"),
    State("radios", "value"),
    State("date-range-picker", "value"),
    State("table-attr-dropdown-menu", "value"),
    State("table-entity-dropdown-menu", "value"),
    State("table-type-dropdown-menu", "value"),
)
def update_data_table(n_clicks, freq, date_range, attrs, entity_ids, table):
    # Prevent update when the page is loaded
    if (
        freq is None
        or n_clicks is None
        or date_range is None
        or attrs is None
        or entity_ids is None
        or table is None
    ):
        raise PreventUpdate

    def get_data(attrs, entity_ids, table, date_range, freq):
        columnDefs = [{"field": "time_index"}]
        data = []
        for attr in attrs:
            for entity_id in entity_ids:
                query = f"""SELECT time_index, {attr} FROM \"mtopeniot\".\"{table}\" WHERE entity_id = '{entity_id}';"""
                with client.connect(
                    f"{CRATE_HOST}:4200", username="crate"
                ) as connection:
                    cursor = connection.cursor()
                    cursor.execute(query)
                    attr_data = cursor.fetchall()

                print("attr_data", attr_data)
                df = pd.DataFrame(
                    attr_data,
                    columns=["time_index", f"{entity_id}_{attr}"],
                ).sort_values(by="time_index")

                print("raw df from attr_data", df)

                df["time_index"] = (
                    pd.to_datetime(df["time_index"], unit="ms")
                    .dt.tz_localize("UTC")
                    .dt.tz_convert("Europe/Madrid")
                )

                print("df after time_index conversion", df)

                # Filter df by date_range. Convert df["time_index"] to datetime to compare it with date_range
                df = df[
                    (
                        df["time_index"].dt.tz_localize(None)
                        >= datetime.strptime(date_range[0], "%Y-%m-%d")
                    )
                    & (
                        df["time_index"].dt.tz_localize(None)
                        <= datetime.strptime(date_range[1], "%Y-%m-%d")
                        + timedelta(days=1)
                    )
                ]

                print("df after date_range", df)

                selected_freq = {1: "5min", 2: "15min", 3: "1h", 4: "1d"}

                if freq != 0:
                    # Resample df by the frequency selected by the user
                    df = df.set_index("time_index").resample(selected_freq[freq]).mean()
                    df = df.reset_index()

                # Filter only register with values
                df = df[df[f"{entity_id}_{attr}"].notna()]

                print("df after filtering", df)

                # Append column definition
                columnDefs.append({"field": f"{entity_id}_{attr}"})

                # Append rowData
                data.extend(df.to_dict("records"))

                print("data after extending", data)

        # Convert rowData to a DataFrame for manipulation
        df_merged = pd.DataFrame(data)

        print("df_merged", df_merged.info())
        print("df_merged", df_merged)

        # Merge records with the same time index
        df_merged = df_merged.groupby("time_index", as_index=False).agg(
            {
                f"{entity_id}_{attr}": "last"
                for entity_id in entity_ids
                for attr in attrs
            }
        )

        print("df_merged after grouping by", df_merged)

        # Convert back to a list of dictionaries
        data = df_merged.to_dict("records")

        print("columnDefs", columnDefs)
        print("data after converting to a list of dictionaries", data)

        return columnDefs, data

    # If the user selects more than one attribute or entity, create a table with different columns for each attribute and entity
    # Get the data from crateDB
    if len(attrs) > 1 or len(entity_ids) > 1:
        columnDefs, data = get_data(attrs, entity_ids, table, date_range, freq)
    else:
        columnDefs, data = get_data(
            [attrs[0]], [entity_ids[0]], table, date_range, freq
        )

    return columnDefs, data
