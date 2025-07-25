from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from dash_bootstrap_templates import ThemeSwitchAIO

import dash_bootstrap_components as dbc

from datetime import datetime

from test_data import test_data 



def get_data():
    return test_data

severities = ["critical", "high", "medium", "low"]
finding_types=["audit", "secrets", "vulnerability"]

app_data = get_data()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# select the Bootstrap stylesheet2 and figure template2 for the theme toggle here
template_theme1 = "plotly"
template_theme2 = "plotly_dark"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

controls_style = {
    "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.25)",
    "display": "flex",
    "alignContent": "center",
    "justifyContent": "center",
    "textAlign": "center",
    "padding": "8px",
    }
controls = dbc.Card(
    [
        html.Div([
            html.Label(children="Report Type", htmlFor="report-type-selection", style={"textAlign":"center", "marginBottom": "1px", "marginTop": "2px", "display": "block"}),
            dcc.Dropdown(finding_types, "vulnerability", id="report-type-selection",style={"color": "#adc2dc"}),

            html.Label(children="Severity", htmlFor="severity-selection", style={"textAlign":"center","marginBottom": "1px", "marginTop": "2px", "display": "block"}),
            dcc.Dropdown(severities, "low", id="severity-selection", style={"color": "#adc2dc"}),
        ])
    ], style=controls_style)


# Requires Dash 2.17.0 or later
app.layout = html.Div([
    dcc.Store(id="test-data", storage_type="local"),  # Store data persistently
    
    ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],),
    
    html.H1(children="Dashboard of Security Reports by severity",className="text-primary text-center pt-5 pb-5"),
    
    html.Div([ # div for body
        html.Div([
                html.Div(id="prior_hour_new", style={"display": "inline-block", "width": " 185px" }),
                html.Div(id="prior_hour_fixed", style={"display": "inline-block", "width": " 185px" }),

                html.Div(id="prior_day_new", style={"display": "inline-block", "width": " 185px" }),
                html.Div(id="prior_day_fixed", style={"display": "inline-block", "width": " 185px" }),

                html.Div(id="prior_week_new", style={"display": "inline-block", "width": " 185px" }),
                html.Div(id="prior_week_fixed", style={"display": "inline-block", "width": " 185px" }),

                html.Div(id="prior_month_new", style={"display": "inline-block", "width": " 185px" }),
                html.Div(id="prior_month_fixed", style={"display": "inline-block", "width": " 185px" }),
           
        ],style={
            "overflowX": "auto", # Enables horizontal scroll
            "whiteSpace": "nowrap",
            "padding": "0px",
        }, className="scroll-container"),
        
        dbc.Container([ # control box
                dbc.Row([dbc.Col(controls, md=4)], align="center")], style={"marginTop":"30px"}, fluid=True),
        
        html.Div([
            html.Div([
                dcc.Graph(id="graph2-content"),
                dcc.Dropdown(
                    ["Linear", "Log"],
                    "Y Axis Type",
                    id="yaxis-type-g2",
                    style={"width": "60%"}
                ),
            ], style={"width": "48%", "display": "inline-block"}),
            html.Div([
                dcc.Graph(id="graph1-content"),
                dcc.Dropdown(
                    ["Linear", "Log"],
                    "Y Axis Type",
                    id="yaxis-type-g1",
                    style={"width": "60%"}
                ),
            ], style={"width": "48%", "float": "right", "display": "inline-block"}),
        ], style={"marginTop": "30px"}),
    ], style={"marginLeft": "25px", "marginRight": "25px"})

], className="dbc bg-opacity-10 bg-indigo-950", style={"minHeight": "100vh"})

def create_mini_box(boxtext, value):
    box_style = {
       "minHeight": "60px",
        "boxShadow": "0 4px 8px rgba(0,0,0,0.25)",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "0",
        "border": "none",
        "borderRadius": "8px",
    }

    if value > 13:
        box_style["background-color"] = "#dc3545"
    elif value > 6:
        box_style["background-color"] = "#ffc107"

    return html.Div([dbc.Card([html.Div(f"{boxtext} : {value}")], style=box_style)], className='p-2')

# text box data
@callback(
    [
        Output("prior_hour_new", "children"),
        Output("prior_hour_fixed", "children"),
        Output("prior_day_new", "children"),
        Output("prior_day_fixed", "children"),
        Output("prior_week_new", "children"),
        Output("prior_week_fixed", "children"),
        Output("prior_month_new", "children"),
        Output("prior_month_fixed", "children"),

    ],
    [
        Input("report-type-selection", "value"),
        Input("severity-selection", "value"),
    ],
)
def update_text_boxes(report_type, severity ):
    return (
        create_mini_box("Prior hour new" , app_data[report_type][severity]["prior_hour_new_text"]),
        create_mini_box("Prior hour fixed", app_data[report_type][severity]["prior_hour_fixed_text"]),
        create_mini_box("Prior day new", app_data[report_type][severity]["prior_day_new_text"]),
        create_mini_box("Prior day fixed", app_data[report_type][severity]["prior_day_fixed_text"]),
        create_mini_box("Prior week new", app_data[report_type][severity]["prior_week_new_text"]),
        create_mini_box("Prior week fixed", app_data[report_type][severity]["prior_week_fixed_text"]),
        create_mini_box("Prior month new", app_data[report_type][severity]["prior_month_new_text"]),
        create_mini_box("Prior month fixed", app_data[report_type][severity]["prior_month_fixed_text"]),
    )


# single-severity line chart definition
@callback(
    Output("graph1-content", "figure"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("report-type-selection", "value"),
    Input("severity-selection", "value"),
    Input("yaxis-type-g1", "value"),
)
def update_graph1(toggle, report_type, severity, yaxis_type ):
    template = template_theme1 if toggle else template_theme2
    for ft in finding_types:
        app_data[ft]["daily_data"] = pd.DataFrame.from_dict(app_data[ft]["daily_data"]) 

    melted_dailies = {}
    for ft in finding_types:
        melted_dailies[ft] = pd.melt(
            app_data[ft]["daily_data"],
            id_vars=["creation_date"],
            var_name="severity",
            value_vars=["total", "critical", "high", "medium", "low"],
            value_name="counts")
        melted_dailies[ft]["report_type"] = ft

    result_vertical = pd.concat([melted_dailies[ft] for ft in finding_types], ignore_index=True)

    df_rt = result_vertical[result_vertical.report_type==report_type]
    df_sev = df_rt[df_rt.severity==severity]

    fig = px.line(df_sev,
        x="creation_date", y="counts", title=f"{report_type} - {severity}", template=template)
    fig.update_yaxes(title="issues", type="linear" if yaxis_type == "Linear" else "log")
    fig.update_layout(title={
            "text": f"{report_type} - {severity}",
            "x": 0.5,  # Center title horizontally
            "xanchor": "center",
            "font": {
                "size": 22,
                "family": "Arial",
                }},
        )
    return fig


# all-severity line chart definition
@callback(
    Output("graph2-content", "figure"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("report-type-selection", "value"),
    Input("yaxis-type-g2", "value"),
)
def update_graph2(toggle,report_type, yaxis_type ):
    template = template_theme1 if toggle else template_theme2
    for ft in finding_types:
        app_data[ft]["daily_data"] = pd.DataFrame.from_dict(app_data[ft]["daily_data"]) 

    df_melted = pd.melt(
        app_data[report_type]["daily_data"],
        id_vars=["creation_date"],
        var_name="severity",
        value_vars=["total", "critical", "high", "medium", "low"],
        value_name="counts")

    # df_melted.set_index('creation_date', inplace=True)

    fig = px.line(df_melted,
        x="creation_date", y="counts", color="severity", title=f"{report_type} - all severities", template=template)
    fig.update_yaxes(title="issues", type="linear" if yaxis_type == "Linear" else "log")
    fig.update_layout(title={
            "text": f"{report_type} - all severities",
            "x": 0.5,  # Center title horizontally
            "xanchor": "center",
            "font": {
                "size": 22,
                "family": "Arial",
                }},
        )
    return fig

if __name__ == "__main__":
    app.run(
        debug=True,
        # use_reloader=False,
        )
