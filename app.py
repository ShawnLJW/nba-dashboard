from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from nba_api.stats.static.players import get_players
from nba_api.stats.static.teams import get_teams
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playerdashboardbyyearoveryear

players = pd.DataFrame(get_players())
players = players.set_index('id')
teams = pd.DataFrame(get_teams())
teams = teams.set_index('id')

# Show LeBron James when page first loads
player = 'LeBron James'
player_id = players[players['full_name'] == player].index[0]
player_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id).get_data_frames()[1]
seasons_played = player_stats['GROUP_VALUE']
season_id = seasons_played[0]
team_id = player_stats.at[0, 'TEAM_ID']
team = teams.at[team_id, 'full_name']
shots, shot_averages = shotchartdetail.ShotChartDetail(team_id, player_id, season_nullable=season_id).get_data_frames()
games_played = player_stats.at[0, 'GP']
points_per_game = player_stats.at[0, 'PTS'] / games_played
rebounds_per_game = player_stats.at[0, 'REB'] / games_played
assists_per_game = player_stats.at[0, 'AST'] / games_played

def plot_shots(shots):
    fig = px.scatter(
        x=shots['LOC_X'], y=shots['LOC_Y'],
        width=540, height=490
    )
    fig.update_layout(margin={'l':20, 'r':20, 't':20, 'b':20}, plot_bgcolor="#e3b871")
    fig.update_xaxes(range=[-250, 250], visible=False)
    fig.update_yaxes(range=[-50, 425], visible=False)
    
    fig.add_shape(type='rect', x0=-250, x1=250, y0=-47.5, y1=422.5)
    fig.add_shape(type='rect', x0=-80, x1=80, y0=-47.5, y1=142.5)
    fig.add_shape(type='line',x0=-220, x1=-220, y0=-47.5, y1=92.5)
    fig.add_shape(type='line',x0=220, x1=220, y0=-47.5, y1=92.5)
    fig.add_shape(type='circle', x0=-237.5, x1=237.5, y0=-237.5, y1=237.5)
    fig.add_shape(type='line',x0=-30, x1=30, y0=-7.5, y1=-7.5)
    fig.add_shape(type='circle', x0=-7.5, x1=7.5, y0=-7.5, y1=7.5, line={'color':'#ec5f2f'})
    return fig

app = Dash(__name__)

app.layout = html.Div(children=[
    html.Header(children=[
        html.Img(src='https://cdn.nba.com/logos/leagues/logo-nba.svg', className='logo'),
        html.H1(children='Player Dashboard', className='title'),
    ]),
    
    html.Div(id='dashboard', children=[
        html.Div(id='dropdown-filters', children=[
            html.Div(children=[
                html.P(children='Player:'),
                dcc.Dropdown(players['full_name'], player, id='player-select'),
            ], className='dropdown-labeled'),
            html.Div(children=[
                html.P(children='Season:'),
                dcc.Dropdown(seasons_played, seasons_played[0], id='season-select'),
            ], className='dropdown-labeled')
            
        ]),
        
        html.Div(id='player-info', children=[
            html.Div(children=[
                html.P(id='player-team', children=team),
                html.H1(id='player-name', children=player), 
            ]),
            html.Img(id='player-headshot', src=f'https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png'),
        ]),

        html.Div(id='summary-stats', children=[
            html.Div(children=[
                html.H2(id='points', children=f'{points_per_game:.1f}'),
                html.P(children='Points Per Game'),
            ], className='summary-stat'),
            html.Div(children=[
                html.H2(id='rebounds', children=f'{rebounds_per_game:.1f}'),
                html.P(children='Rebounds Per Game'),
            ], className='summary-stat'),
            html.Div(children=[
                html.H2(id='assists', children=f'{assists_per_game:.1f}'),
                html.P(children='Assists Per Game'),
            ], className='summary-stat'),
        ]),
        
        dcc.Graph(id='shotchart', figure=plot_shots(shots))
    ]),

])


@app.callback(
    Output('season-select', 'options'),
    Output('season-select', 'value'),
    Output('player-headshot', 'src'),
    Output('player-name', 'children'),
    Output('player-team', 'children'),
    Output('points', 'children'),
    Output('rebounds', 'children'),
    Output('assists', 'children'),
    Output('shotchart', 'figure'),
    Input('player-select', 'value'),
    Input('season-select', 'value'),
)
def update_dashboard(player, season):
    player_id = players[players['full_name'] == player].index[0]
    player_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id).get_data_frames()[1]
    seasons_played = player_stats['GROUP_VALUE']
    if seasons_played.str.contains(season).any():
        season_index = player_stats[player_stats['GROUP_VALUE']==season].index[0]
    else:
        season_index = 0
        season = seasons_played[0]
    
    team_id = player_stats.at[season_index, 'TEAM_ID']
    team = teams.at[team_id, 'full_name']
        
    headshot_src = f'https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png'
    
    games_played = player_stats.at[season_index, 'GP']
    points_per_game = player_stats.at[season_index, 'PTS'] / games_played
    rebounds_per_game = player_stats.at[season_index, 'REB'] / games_played
    assists_per_game = player_stats.at[season_index, 'AST'] / games_played
    
    shots, shot_averages = shotchartdetail.ShotChartDetail(team_id, player_id, season_nullable=season).get_data_frames()
    shot_chart = plot_shots(shots)
        
    return seasons_played, season, headshot_src, player, team, f'{points_per_game:.1f}', f'{rebounds_per_game:.1f}', f'{assists_per_game:.1f}', shot_chart


if __name__ == '__main__':
    app.run(debug=True)
