# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction

import pandasql as ps
from pandasql import sqldf
import plotly.express as px

import dash_table
import plotly.graph_objs as go
import io
#import cufflinks as cf #Using cufflinks, a wrapper for easing plotting with pandas and plotly

import dash_daq as daq


app = dash.Dash(__name__)

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}


# Load Data
player_stats = pd.read_excel('2K Player Stats.xlsx')
team_stats = pd.read_excel('2KL Team Stats.xlsx')

player_stats = player_stats.rename(columns = {"FG%":"FG_pct","FG3%":"FDG3_pct","FT%":"FT_pct","eFG%":"effi_pct","TS%":"Tru_shoot_pct"})
team_stats = team_stats.rename(columns={"FG%":"FG_pct","3P%":"3P_pct","Opp_3P%":"Opp_3P_pct","Opp_FG%":"Opp_FG_pct"})

teams = team_stats['Nickname'].unique()
players = player_stats['Player'].unique()

team_stat_categories = team_stats.columns.tolist()
player_stat_categories = player_stats.columns.tolist()

pysqldf = lambda q: sqldf(q,globals())
q1 = '''
     SELECT Nickname,Points,Offensive_Rebounds,Defensive_Rebounds,Assists,Steals,Turnovers
     FROM team_stats
    '''
main_cats = pysqldf(q1)

def barplt_teams(data,feat):
    
    fig = px.bar(data.sort_values(by=[feat]), x='Nickname', y=str(feat),
                hover_data = ['Nickname'],color = feat,text = feat)
    fig.show()
    

def barplt_players(data,feat):
    data_names= data.columns.tolist()
    data_names.remove(feat)
    
    fig = px.bar(data.sort_values(by=[feat]), x='Player', y=str(feat),
                hover_data= ['Player','Team'],color=feat,text = feat)
    fig.show()


# App Layout
app.layout = html.Div(
    [
        # Left dropdown for team 1
        html.Div([
            dcc.Markdown('Select First Team'),
                dcc.Dropdown(
                    id = 'team1',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Blazer5 Gaming'),

        # Middle dropdown for team 2
            dcc.Markdown('Select Second Team'),
                dcc.Dropdown(
                    id = 'team2',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = '76ers GC'
                ),
            dcc.Graph(id = 'indicator-graphic')
            ],
            style = {'width' : '40%', 'display': 'inline-block', 'float': 'center'}
        ),



        # Right dropdown for category
        html.Div(
            [
                dcc.Markdown('All Teams'),
                    dcc.Dropdown(
                        id = 'team_stat_category',
                        options = [{'label': i, 'value': i} for i in team_stat_categories],
                        value = 'Blocked_Shots'
                    ),
                    dcc.Graph(id='allteams_output-graphic')
            ],
            style = {'width': '50%', 'display': 'inline-block', 'float': 'right'}
        ),



        html.Div(
            [
                dcc.Markdown('All Players'),
                    dcc.Dropdown(
                        id = 'player_stat_category',
                        options = [{'label': i, 'value': i}for i in player_stat_categories],
                        value = 'STL' 
                    ),
                    dcc.Graph(id='allplayers_output-graphic')
            ],
            style = {'width': '50%','display': 'inline-block', 'float': 'right'}
        )
        
    ]
)

@app.callback(
    Output('allteams_output-graphic', 'figure'),
    [Input('team_stat_category','value')])

def update_output_div(feat):
    data_feat = team_stats.sort_values(by=[feat], ascending=False)

    return {
        'data':[
        {'x':data_feat["Nickname"],'y':data_feat[feat],'type': 'bar','marker':{'color':data_feat[feat],'colorscale': 'Viridis'}}],
        'layout': {
            'title': (feat)
        }
}

@app.callback(
    Output('allplayers_output-graphic', 'figure'),
    [Input('player_stat_category','value')])

def update_output_div(feat):
    data_feat = player_stats.sort_values(by=[feat], ascending=False)

    return {
        'data':[
        {'x':data_feat["Player"],'y':data_feat[feat],'type': 'bar','marker':{'color':data_feat[feat],'colorscale': 'Viridis'}}],
        'layout': {
            'title': (feat)
        }
}


@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('team1', 'value'),
     Input('team2', 'value'),
     Input('team_stat_category', 'value')])

def update_graph(team_1, team_2, stat):
    return {
        'data': [
            {'x': [stat], 'y': team_stats[team_stats["Nickname"] == team_1][stat], 'type': 'bar', 'name': team_1},
            {'x': [stat], 'y': team_stats[team_stats["Nickname"] == team_2][stat], 'type': 'bar', 'name': team_2},
        ],
        'layout': {
            'title': (team_1 + ' vs. ' + team_2 + ' on ' + stat)
        }
    }




if __name__ == '__main__':
    app.run_server(debug=True)