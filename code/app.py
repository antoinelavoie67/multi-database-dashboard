from dash import Dash, html, dcc, Input, Output, dash_table, State, ctx, no_update
import mongodb_utils
import neo4j_utils
import mysql_utils
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
from dash import dcc
from dash import html
import math
import plotly.express as px


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/style.css'])

watchlist_schools = []

app.layout = dbc.Container(fluid=True, children=[

##################### ROW 1 ##################### 

    dbc.Row([
        ### TITLE AND YEAR SLIDER
        dbc.Col([
            html.H1("Faculty Research Funding Board", style={'textAlign': 'center'}),
            dcc.RangeSlider(
                id='year-slider',
                min=1982,
                max=2023,
                value=[1982, 2023],
                marks={str(year): {'label': str(year) if year % 5 == 0 else '', 'style': {'color': '#000080'}} for year in range(1982, 2024)},
                tooltip={"placement": "bottom", "always_visible": True},
                className='small_widget'
            ),
        ], width=12)
    ], justify="center", className='widget'),

##################### ROW 2 ##################### 

    dbc.Row([

        ### WIDGET: Displaying Top 10 Universities for Selected Keyword

        dbc.Col([
            
            html.H2(id="top_10_universities_for_keyword", children="Top 10 Universities by Avg. Citations on [Keyword]"),
            dbc.Row([
                dbc.Col([
                    html.H4("Keyword"),
                    dcc.Dropdown(
                        id="keyword_dropdown", placeholder="Explore Possible Keywords...",
                        options=neo4j_utils.keywords,
                        value=None,
                        multi=False,
                        style={'width': '100%'}
                    ),
                    html.Br(),  # Adds a break between the dropdown and input
                    dbc.Input(id="keyword_input", placeholder="Enter Keyword Here...", type="text")
                ], width=11, className='small_widget')
            ]),
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="university_keyword_table",
                        columns=[
                            {"name": "Logo", "id": "logo", "presentation": "markdown"},
                            {"name": "University", "id": "university"},
                            {"name": "Publication Count", "id": "count"},
                            {"name": "Average Citations", "id": "average"},
                        ],
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'logo'}, 'textAlign': 'center'}
                        ],
                        style_table={'width': '100%', 'maxWidth': '100%', 'overflowX': 'auto'},
                        markdown_options={"html": True},
                    )
                ], width=11, class_name='small_widget')
            ])
        ], width=12, lg=6),
        
        dbc.Col([
            html.H2(id="create_school_watchlist", children="Create University Watchlist"),
            dbc.Row([
                dbc.Col([
                    html.H4("Schools of Interest"),
                    dcc.Dropdown(
                        id="school_dropdown",
                        options=neo4j_utils.universities,
                        value=None,
                        multi=True,
                        style={'width': '100%'}
                    )
                ], width=11, class_name='small_widget')
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Number Of Universities Selected:"),
                            html.Div(id='num_schools', children='0', className="card-text centered-text")
                        ])
                    ], className="small_widget"),
                ], width=4),
                
                ### WIDGET: Number Of Faculty Who Referenced [Keyword]

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Number Of Faculty Who Referenced [Keyword]:"),
                            html.Div(id='num_prof', children='0', className="card-text centered-text")
                        ])
                    ], className="small_widget"),
                ], width=4),

                ### WIDGET: Number Of Publications Which Referenced [Keyword]

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Number Of Publications Which Referenced [Keyword]:"),
                            html.Div(id="num_pub", children='0', className="card-text centered-text")
                        ])
                    ], className="small_widget"),
                ], width=4),
            ]),

            ### WIDGET: Add To/Remove From Watchlist
            ### EC: Generating Map/Data Addition

            dbc.Row([
                dbc.Col([
                    dbc.Button('Add To Watchlist', id='add-to-watchlist-button', n_clicks=0, color='primary', style={'backgroundColor': '#20b558', 'fontSize': '18px', 'padding': '15px 30px'}, className='mr-2')
                ], width='auto'),
                dbc.Col([
                    dbc.Button('Remove From Watchlist', id='remove-from-watchlist-button', n_clicks=0, color='primary', style={'backgroundColor': '#d01322', 'fontSize': '18px', 'padding': '15px 30px'}, className='mr-2')
                ], width='auto'),
                dbc.Col([
                    dbc.Button('Generate Map', id='map_button', n_clicks=0, color='primary', style={'backgroundColor': '#0c6efd', 'fontSize': '18px', 'padding': '15px 30px'}, className='mr-2')
                ], width='auto')
            ]),
            dbc.Row([
                dbc.Col([
                    html.H4("Watchlist"),
                    dash_table.DataTable(
                        id="university_watchlist_table",
                        columns=[
                            {"name": "Logo", "id": "logo", "presentation": "markdown"},
                            {"name": "University", "id": "university"},
                            {"name": "Rank", "id": "univ_rank"},
                            {"name": "Enrollment", "id": "enrollment"},
                            {"name": "Avg SAT", "id": "avg_sat"},
                            {"name": "Avg ACT", "id": "avg_act"},
                            {"name": "City", "id": "city"},
                            {"name": "State", "id": "state"}
                        ],
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'photo_url'}, 'textAlign': 'center'}
                        ],
                        style_table={'width': '100%', 'maxWidth': '100%', 'minWidth': '100%'},
                        markdown_options={"html": True},
                    )
                ], width=12, class_name='small_widget')
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='university_map')
                ])
            ])
        ], width=12, lg=6),
    ], class_name='small_widget'),

##################### ROW 3 ##################### 

    dbc.Row([

        ### WIDGET: Faculty Research and Filter By University Watchlist

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H2(id="mongo_faculty_analysis", children="Target Faculty Analysis:")
                ], width='auto'),
                dbc.Col([
                    dbc.Button('Filter By University Watchlist', id='university_filter_button', n_clicks=0, color='primary', style={'backgroundColor': '#0c6efd', 'fontSize': '18px', 'padding': '10px 15px'}, className='mr-2')
                ], width='auto')
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    html.H4("Faculty Research Interest"),
                    dbc.Input(id="faculty_analysis_text", placeholder="Enter Research Interest Here...", type="text")
                ], width=11, class_name='small_widget')
            ]),
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="faculty_analysis_table",
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Photo", "id": "picture", "presentation": "markdown"},
                            {"name": "Name", "id": "name"},
                            {"name": "University", "id": "affiliation"},
                            {"name": "Position", "id": "position"},
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Total Score", "id": "total score"}
                        ],
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'logo'}, 'textAlign': 'center'}
                        ],
                        style_table={'width': '100%', 'maxWidth': '100%', 'overflowX': 'auto'},
                        markdown_options={"html": True},
                    )
                ], width=11, class_name='small_widget')
            ]),
        ], width=11, lg=6),
                
        dbc.Col([
            html.H2(id="faculty_collab", children="Faculty Collaboration Explorer:"),

            ### WIDGET: Faculty Collaboration

            dbc.Row([
               dbc.Col([
                   html.H4("Faculty Explorer"),
                    dcc.Dropdown(
                        id="faculty_dropdown",
                        options=neo4j_utils.faculties,
                        value=None,
                        multi=False,
                        style={'width': '100%'}
                    ),
               ],  width=11, className='small_widget'),
            ]),
            dbc.Row([
               dcc.Graph(id='neo4j_graph')
            ]),

            ### WIDGET: Add To Reach Out Remove From Reach Out

            dbc.Row([
                dbc.Col([
                    dbc.Button('Reach Out To', id='reach-out-to-button', n_clicks=0, color='primary', style={'backgroundColor': '#0c6efd', 'fontSize': '18px', 'padding': '10px 15px'}, className='mr-2')
                ], width='auto'),
                dbc.Col([
                    dbc.Button('Remove From Reach Out List', id='remove-from-reach-button', n_clicks=0, color='primary', style={'backgroundColor': '#0c6efd', 'fontSize': '18px', 'padding': '10px 15px'}, className='mr-2')
                ], width='auto'),
            ]),
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="faculty_watchlist_table",
                        columns=[
                            {"name": "University", "id": "affiliation"},
                            {"name": "Picture", "id": "picture", "presentation": "markdown"},
                            {"name": "Name", "id": "name"},
                            {"name": "Position", "id": "position"},\
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Time of Update", "id": "updated_at"}
                        ],
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'logo'}, 'textAlign': 'center'}
                        ],
                        style_table={'width': '100%', 'maxWidth': '100%', 'overflowX': 'auto'},
                        markdown_options={"html": True},
                    )
                ], width=11, class_name='small_widget')
            ])
        ], width=11, lg=6)
    ], class_name='small_widget'),

##################### ROW 4 ##################### 

    dbc.Row([
        dbc.Col([
            
            ### WIDGET: Faculty Funding 

            dbc.Row([
                dbc.Col([
                    html.H2(id="budgeting_title", children="Faculty Investments: Budgeting"),
                    html.H4("Investment Amount"),
                    dbc.Input(id="input_budget", placeholder="Enter Total Budget Here...", type="text"),
                    dbc.Row([
                        dbc.Button('Fund', id='add_funding_button', n_clicks=0, color='primary', style={'backgroundColor': '#20b558', 'fontSize': '18px', 'padding': '10px 15px'}, className='mr-2')
                    ], className='mt-3'),
                    html.Br(),
                    dbc.Row([
                        dbc.Button('Remove Fund', id='remove_funding_button', n_clicks=0, color='primary', style={'backgroundColor': '#d01322', 'fontSize': '18px', 'padding': '10px 15px'}, className='mr-2')
                    ], className='mt-3')
                ], width=12, lg=3, class_name='small_widget mr-lg-3'),
                dbc.Col([], width=12, lg=1),
                dbc.Col([
                    dash_table.DataTable(
                        id="faculty_fund_watchlist_table",
                        columns=[
                            {"name": "Logo", "id": "logo", "presentation": "markdown"},
                            {"name": "University", "id": "affiliation"},
                            {"name": "Rank", "id": "rank"},
                            {"name": "Enrollment", "id": "enrollment"},
                            {"name": "State", "id": "state"},
                            {"name": "Photo", "id": "picture", "presentation": "markdown"},
                            {"name": "Name", "id": "name"},
                            {"name": "Position", "id": "position"},
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Fund", "id": "fund"}
                        ],
                        style_cell={'textAlign': 'center'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'logo'}, 'textAlign': 'center'}
                        ],
                        style_table={'width': '100%', 'maxWidth': '100%', 'overflowX': 'auto'},
                        markdown_options={"html": True},
                    )
                ], width=12, lg=8, class_name='small_widget')
            ])
        ], class_name='small_widget')
    ])
])


##################### HELPER FUNCTIONS ##################### 

#Grab Images to Display in DCC Table
def prepare_data_with_images(results, widget):
    global watchlist_schools
    if widget == 1:
        data = []
        for record in results:
            data.append({
                'logo': f"<img src='{record['logo']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                'university': record['university'],
                'count': record['count'],
                'average': record['average']
            })
    elif widget == 2:
            data = []
            current_schools = []
            for record in results:
                current_schools.append(record['name'])
                data.append({
                    'logo': f"<img src='{record['photo_url']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                    'university': record['name'],
                    'univ_rank': record['univ_rank'],
                    'enrollment': record['enrollment'],
                    'avg_sat': record['avg_sat'],
                    'avg_act': record['avg_act'],
                    'city': record['city'],
                    'state': record['state']
                })
            for university in current_schools:
                if university not in watchlist_schools:
                    watchlist_schools.append(university)
            watchlist_schools = [university for university in watchlist_schools if university in current_schools]
    elif widget == 3:
        data = []
        for record in results:
            data.append({
                "id": record["faculty_id"],
                "picture": f"<img src='{record['faculty_photoUrl']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                "name": record["faculty_name"],
                "affiliation": record["affiliation_name"],
                "position": record["faculty_position"],
                "email": record["faculty_email"],
                "phone": record["faculty_phone"],
                "total score": record["total_keyword_score"]
            })
    elif widget == 4:
        data = []
        for record in results:
            data.append({
                "affiliation": record["university_name"],
                "picture": f"<img src='{record['faculty_photo_url']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                "name": record["faculty_name"],
                "position": record["faculty_position"],
                "email": record["faculty_email"],
                "phone": record["faculty_phone"],
                "updated_at": record["updated_at"]
            })
    elif widget == 5:
        data = []
        for record in results:
            data.append({
                "logo": f"<img src='{record['photo_url']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                "affiliation": record["name"],
                "rank": record["univ_rank"],
                "enrollment": record["enrollment"],
                "state": record["state"],
                "picture": f"<img src='{record['faculty_photo_url']}' style='height:50px; width:auto; display:block; margin:auto;'>",
                "name": record["faculty_name"],
                "position": record["faculty_position"],
                "email": record["faculty_email"],
                "phone": record["faculty_phone"],
                "fund": record["fund"]
            })
    else:
        print("Inputted wrong widget number...check")
    return data

#US Centered Map
def create_university_map(df):
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", text="name",
                            hover_name="name", zoom=4, height=600)
    fig.update_traces(marker=dict(size=25, color='red'))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 37.0902, "lon": -95.7129},
        mapbox_zoom=4,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig


#Neo4j Map
def add_node(G, x, y, text, size=30, color='blue', text_size=14):
    G.add_trace(go.Scatter(
        x=[x], y=[y],
        text=[text],
        mode='markers+text',
        marker=dict(size=size, color=color, line=dict(width=2, color='DarkSlateGrey')),
        textposition='top center',
        textfont=dict(size=text_size),
        hoverinfo='text'
    ))
def add_edge(G, x0, y0, x1, y1, width=4, color='grey'):
    G.add_trace(go.Scatter(
        x=[x0, x1],
        y=[y0, y1],
        mode='lines',
        line=dict(width=width, color=color)
    ))
def create_graph(df):
    G = go.Figure()
    center_x, center_y = 0, 0
    num_coauthors = df['CoauthorName'].nunique()
    angle_step = 2 * math.pi / num_coauthors
    positions = {df.iloc[0]['FacultyName']: (center_x, center_y)}

    for i, coauthor in enumerate(df['CoauthorName'].unique()):
        x = center_x + 3 * math.cos(i * angle_step)
        y = center_y + 3 * math.sin(i * angle_step)
        positions[coauthor] = (x, y)

    for _, row in df.iterrows():
        faculty = row['FacultyName']
        coauthor = row['CoauthorName']
        institute = row['CoauthorInstituteName']

        faculty_pos = positions[faculty]
        coauthor_pos = positions[coauthor]
        institute_pos = (coauthor_pos[0] + 3, coauthor_pos[1])

        add_node(G, *faculty_pos, faculty, size=50, color='blue', text_size=18)
        add_node(G, *coauthor_pos, coauthor, size=40, color='green', text_size=16)
        add_node(G, *institute_pos, institute, size=30, color='red', text_size=14)

        add_edge(G, *faculty_pos, *coauthor_pos, width=3)
        add_edge(G, *coauthor_pos, *institute_pos, width=3)

    G.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return G


##################### ROW 2 CALLBACKS ##################### 

### WIDGET: Displaying Top 10 Universities for Selected Keyword
@app.callback(
    Output("university_keyword_table", "data"),
    Input("keyword_input", "value"),
    Input("year-slider", "value")
)    
def update_results_table(keyword, year_range):
    start_year, end_year = year_range
    df = neo4j_utils.top_10_highest_avg_citations_keyword_year(keyword, start_year, end_year)
    formatted_data = prepare_data_with_images(df.to_dict('records'), 1)
    return formatted_data

#Doesn't Use any DB
@app.callback(
    Output("num_schools", "children"),
    Input("school_dropdown", "value")
)    
def update_num_schools(schools):
    num_schools = len(schools) if schools else 0
    return f"{num_schools}"

### WIDGET: Number Of Faculty Who Referenced [Keyword]
@app.callback(
    Output("num_prof", "children"),
    Input("keyword_input", "value"),
    Input("school_dropdown", "value"),
    Input("year-slider", "value")
)    
def update_num_faculty(keyword, schools, year_range):
    if keyword is None or schools is None:
        return "0"
    start_year, end_year = year_range
    num_faculty = neo4j_utils.num_fac_keyword(keyword, schools, start_year, end_year)
    return f"{num_faculty}"

### WIDGET: Number Of Publications Which Referenced [Keyword]
@app.callback(
    Output("num_pub", "children"),
    Input("keyword_input", "value"),
    Input("school_dropdown", "value"),
    Input("year-slider", "value")
)    
def update_num_pub(keyword, schools, year_range):
    if keyword is None or schools is None:
        return "0"
    start_year, end_year = year_range
    num_publication = neo4j_utils.num_pub_keyword(keyword, schools, start_year, end_year)
    return f"{num_publication}"

### WIDGET: Add To/Remove From Watchlist
@app.callback(
    Output("university_watchlist_table", "data"),
    [Input("add-to-watchlist-button", "n_clicks"),
     Input("remove-from-watchlist-button", "n_clicks")],
    [State("school_dropdown", "value")]
)
def update_university_watchlist(add_clicks, remove_clicks, schools):    
    if not ctx.triggered or not schools:
        return no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == "add-to-watchlist-button" and add_clicks:
        watchlist_df = mysql_utils.manage_watchlist("add", schools)
    elif button_id == "remove-from-watchlist-button" and remove_clicks:
        watchlist_df = mysql_utils.manage_watchlist("remove", schools)
    else:
        return no_update, no_update
    
    formatted_data = prepare_data_with_images(watchlist_df[['photo_url', 'name', 'univ_rank', 'enrollment', 'avg_sat', 'avg_act', 'city', 'state']].to_dict('records'), 2)
    return formatted_data

### EC MAP
@app.callback(
    Output("university_map", "figure"),
    Input("map_button", "n_clicks"),
    State("university_watchlist_table", "data")
)
def update_university_map(n_clicks, watchlist_data):
    if n_clicks is None or n_clicks == 0:
        return  create_university_map(pd.DataFrame(columns=['latitude', 'longitude', 'name']))
    if not watchlist_data:
        return create_university_map(pd.DataFrame(columns=['latitude', 'longitude', 'name']))
    watchlist_universities = [entry['university'] for entry in watchlist_data]
    all_university_data = mysql_utils.get_all_university_data()
    filtered_university_data = all_university_data[all_university_data['name'].isin(watchlist_universities)]

    if not filtered_university_data.empty:
        figure = create_university_map(filtered_university_data)
    else:
        figure = create_university_map(pd.DataFrame(columns=['latitude', 'longitude', 'name']))
    return figure

##################### ROW 3 CALLBACKS ##################### 

### WIDGET: Faculty Research and Filter By University Watchlist
@app.callback(
    Output("faculty_analysis_table", "data"),
    [Input("faculty_analysis_text", "value"),
     Input("university_filter_button", "n_clicks")],
    [ State("keyword_input", "value")]
)
def update_faculty_analysis_table(research_interest, n_clicks, keyword):
    if keyword is None:
        return
    if research_interest is None:
        research_interest = ""
    else:
        if n_clicks % 2 == 1:
            df = mongodb_utils.get_top_faculty(research_interest, keyword, watchlist_schools)
            formatted_data = prepare_data_with_images(df.to_dict('records'), 3)
            return formatted_data
        else:
            df = mongodb_utils.get_top_faculty(research_interest, keyword, None)
            formatted_data = prepare_data_with_images(df.to_dict('records'), 3)
            return formatted_data
@app.callback(
    Output('neo4j_graph', 'figure'),
    [Input('faculty_dropdown', 'value'),
     Input('keyword_input', 'value')]
)
def faculty_connection(faculty, keyword):
    if not faculty or not keyword:
        return go.Figure()

    df = neo4j_utils.get_graph(faculty, keyword)
    if df.empty:
        return go.Figure()
    return create_graph(df)

### WIDGET: Add To Faculty Reach Out Remove From Reach Out
@app.callback(
    Output('faculty_watchlist_table', 'data'),
    [Input('faculty_dropdown', 'value'),
     Input('reach-out-to-button', 'n_clicks'),
     Input('remove-from-reach-button', 'n_clicks')])
def update_faculty_watchlist(faculty_select, reach_out_clicks, remove_from_clicks):
    if not faculty_select:
        return no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "reach-out-to-button" and reach_out_clicks:
        df = mysql_utils.manage_faculty_watchlist("add", faculty_select)
    elif button_id == "remove-from-reach-button" and remove_from_clicks:
        df = mysql_utils.manage_faculty_watchlist("remove", faculty_select)
    else:
        return no_update
    
    return prepare_data_with_images(df.to_dict('records'), 4)

##################### ROW 4 CALLBACKS ##################### 

### WIDGET: Faculty Funding 

@app.callback(
    Output('faculty_fund_watchlist_table', 'data'),
    [Input('add_funding_button', 'n_clicks'),
     Input('remove_funding_button', 'n_clicks')],
     [State('input_budget', 'value'),
        State('faculty_dropdown', 'value')]
)
def update_faculty_funding_watchlist(fund_clicks, remove_fund_clicks, total_budget, faculty_select):
    if not ctx.triggered or not faculty_select:
        return no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        total_budget = float(total_budget)
        if total_budget < 0:
            raise ValueError("Total budget must be non-negative.")
    except ValueError:
        return [{"logo": "", "affiliation": "", "picture": "", "name": "", "position": "", "email": "", "phone": "", "fund": "Error: Your budget is not a number or is negative"}]
    
    df = None
    if triggered_id == 'add_funding_button':
        df = mysql_utils.manage_faculty_fund_watchlist(total_budget)
    elif triggered_id == 'remove_funding_button':
        df = mysql_utils.manage_faculty_fund_watchlist(0)

    if df is not None:
        formatted_data = prepare_data_with_images(df.to_dict('records'), 5)
        return formatted_data
    return no_update

if __name__ == "__main__":
    app.run_server(debug=True)