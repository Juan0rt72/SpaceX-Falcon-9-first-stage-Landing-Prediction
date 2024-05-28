# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# List of names of launch sites
names_launch = list(spacex_df['Launch Site'].unique())

# We create a list of dictionaries for the options of the dropdown
option_list = [{'label':'All Sites', 'value':'ALL'}]
for name in names_launch:
    option_list.append({'label':name,'value':name})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options = option_list, value = 'ALL',
                                             placeholder = 'Select a Launch Site',
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(0,10000,1000,
                                                marks = {i:'{}'.format(i) for i in range(0,10001,500)},
                                                value = [min_payload,max_payload],id='payload-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Callback decorator
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
               Input(component_id='site-dropdown',component_property='value'))

def get_pie_chart(site:str) -> go.Figure:
    df = spacex_df  
    if site == 'ALL':
        fig = px.pie(df, values='class',names='Launch Site',
                     title = 'Total Success Launches By Site')
    else:
        df['class_success'] = pd.Series(['Success' if value == 1 else 'Failure' for value in df['class']])
        fig = px.pie(df[df['Launch Site'] == site], names='class_success',title = 'Total Success Launches for site '+ site)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart',component_property='figure'),
    [Input(component_id='site-dropdown',component_property='value'),
     Input(component_id='payload-slider', component_property= 'value')]
)

def get_scatter_chart(site:str,slider:list) -> go.Figure:
    # We filter the values of the df with the values of the slider 
    slider_st = (spacex_df['Payload Mass (kg)']>= slider[0]) & (spacex_df['Payload Mass (kg)']<= slider[1])
    df = spacex_df[slider_st]
    
    if site == 'ALL':
        fig = px.scatter(df,x ='Payload Mass (kg)',y = 'class', color= 'Booster Version Category',
                         title='Correlation between Payload and success for all sites')
    else:
        fig = px.scatter(df[df['Launch Site'] == site],x ='Payload Mass (kg)',y = 'class',
                        color= 'Booster Version Category',
                        title = 'Correlation between Payload and success rate for site '+ site)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()