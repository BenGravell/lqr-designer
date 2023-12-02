import dash
from dash import Input, Output, Patch, dcc, html, clientside_callback
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt

import constants
import lqr
import utils


# Theme
THEME_NAME = "YETI"
THEME_NAME_DARK = f"{THEME_NAME}_DARK"
THEME = getattr(dbc.themes, THEME_NAME)

# stylesheet with the .dbc class to style dcc, DataTable and AG Grid components with a Bootstrap theme
DBC_CSS = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

EXTERNAL_STYLESHEETS = [THEME, dbc.icons.FONT_AWESOME, DBC_CSS]


app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)
app.title = "LQR Designer"
dbt.load_figure_template([THEME_NAME, THEME_NAME_DARK])

# Dark mode switch
color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color_mode_switch"),
        dbc.Switch(id="color_mode_switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color_mode_switch"),
    ],
    className="my-2",
)

# Dark mode switch
clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("color_mode_switch", "id"),
    Input("color_mode_switch", "value"),
)


state_title_map = {f"state_{i}": f"State {i+1}" for i in range(constants.NUM_STATES)}
action_title_map = {f"action_{i}": f"Action {i+1}" for i in range(constants.NUM_ACTIONS)}
state_action_title_map = {**state_title_map, **action_title_map}


slider_state_0 = html.Div(
    [
        dbc.Label("State 1 Penalty", className="p-1"),
        dcc.Slider(
            0,
            5,
            1,
            value=2,
            id="state_penalty_0",
        ),
    ],
)
slider_state_1 = html.Div(
    [
        dbc.Label("State 2 Penalty", className="p-1"),
        dcc.Slider(
            0,
            5,
            1,
            value=2,
            id="state_penalty_1",
        ),
    ],
)
slider_action_0 = html.Div(
    [
        dbc.Label("Action 1 Penalty", className="p-1"),
        dcc.Slider(
            0,
            5,
            1,
            value=2,
            id="action_penalty_0",
        ),
    ],
)
sliders = [slider_state_0, slider_state_1, slider_action_0]
controls = html.Div([html.H2("State & Action Penalties"), *sliders])


def create_system_matrix_infos(A, B, Q, R):
    return [
        {
            "label": "A",
            "description": (
                "The **state-to-state dynamics matrix A** governs how current states influence the next state."
            ),
            "data": A,
        },
        {
            "label": "B",
            "description": (
                "The **input-to-state control matrix B** governs how current inputs influence the next state."
            ),
            "data": B,
        },
        {
            "label": "Q",
            "description": (
                "The **state penalty matrix Q** governs how deviations of each state from the origin are penalized."
            ),
            "data": Q,
        },
        {
            "label": "R",
            "description": (
                "The **input penalty matrix R** governs how deviations of each input from the origin are penalized."
            ),
            "data": R,
        },
    ]


def create_matrix_str(label, data) -> str:
    return f"""$${label} = {utils.matrix_to_latex(data)}$$"""


def create_system_matrix_info_tab(system_matrix_info):
    label = system_matrix_info["label"]
    data = system_matrix_info["data"]
    matrix_str = create_matrix_str(label, data)
    description = system_matrix_info["description"]
    return dbc.Tab(
        dbc.Card(
            [
                html.P(
                    dcc.Markdown(description),
                    className="card-text px-3 pt-3",
                ),
                dcc.Markdown(matrix_str, mathjax=True, style={"textAlign": "center"}, id=f"system-matrix-str-{label}"),
            ],
            className="mt-4",
        ),
        label=label,
    )


system_matrix_infos = create_system_matrix_infos(constants.A, constants.B, constants.Q, constants.R)
tab_children = [create_system_matrix_info_tab(system_matrix_info) for system_matrix_info in system_matrix_infos]
system_matrix_verbiage = html.Div([html.H2("System Matrices"), dbc.Tabs(tab_children)])


app.layout = dbc.Container(
    [
        dbc.Row(
            html.H1("LQR Designer"),
            className="mt-4",
        ),
        dbc.Row(color_mode_switch),
        dbc.Row(
            [
                dbc.Col([controls, html.Br(), system_matrix_verbiage], lg=4, sm=12),
                dbc.Col(
                    html.Div(
                        [
                            html.H2("System Response"),
                            dcc.Graph(id="graph-system-response"),
                        ]
                    ),
                    lg=8,
                    sm=12,
                ),
            ],
        ),
    ],
    fluid=True,
    className="dbc",
)


@app.callback(
    Output("graph-system-response", "figure"),
    Input("state_penalty_0", "value"),
    Input("state_penalty_1", "value"),
    Input("action_penalty_0", "value"),
    Input("color_mode_switch", "value"),
)
def make_graph_system_response(state_penalty_0, state_penalty_1, action_penalty_0, color_mode_switch):
    df = lqr.get_df(state_penalty_0, state_penalty_1, action_penalty_0)
    template_name = THEME_NAME if color_mode_switch else THEME_NAME_DARK
    fig = px.line(
        df.rename(columns=state_action_title_map),
        x="t",
        y=list(state_action_title_map.values()),
        template=template_name,
    )
    return fig


@app.callback(
    Output("system-matrix-str-Q", "children"),
    Input("state_penalty_0", "value"),
    Input("state_penalty_1", "value"),
)
def make_state_penalty_matrix_str(state_penalty_0, state_penalty_1):
    Q = lqr.create_matrix_Q(state_penalty_0, state_penalty_1)
    return create_matrix_str("Q", Q)


@app.callback(
    Output("system-matrix-str-R", "children"),
    Input("action_penalty_0", "value"),
)
def make_action_penalty_matrix_str(action_penalty_0):
    R = lqr.create_matrix_R(action_penalty_0)
    return create_matrix_str("R", R)


# Dark mode switch
@app.callback(
    Output("graph-system-response", "figure", allow_duplicate=True),
    Input("color_mode_switch", "value"),
    prevent_initial_call=True,
)
def update_figure_template(switch_on):
    # When using Patch() to update the figure template, you must use the figure template dict
    # from plotly.io and not just the template name
    template = pio.templates[THEME_NAME] if switch_on else pio.templates[THEME_NAME_DARK]

    patched_figure = Patch()
    patched_figure["layout"]["template"] = template
    return patched_figure


if __name__ == "__main__":
    app.run_server(debug=True)
