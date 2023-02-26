from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

from nba_api.stats.static.players import get_players
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import playerdashboardbyyearoveryear

players = pd.DataFrame(get_players())
players = players.set_index('id')

# Show LeBron James when page first loads
player = 'LeBron James'
player_id = players[players['full_name'] == player].index[0]
player_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id).get_data_frames()[1]
seasons_played = player_stats['GROUP_VALUE']
games_played = player_stats.at[0, 'GP']
points_per_game = player_stats.at[0, 'PTS'] / games_played
rebounds_per_game = player_stats.at[0, 'REB'] / games_played
assists_per_game = player_stats.at[0, 'AST'] / games_played

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

        html.Div(id='summary-stats', children=[
            html.Div(children=[
                html.H2(id='points', children=f'PPG: {points_per_game:.0f}'),
            ], className='summary-stat'),
            html.Div(children=[
                html.H2(id='rebounds', children=f'REB: {rebounds_per_game:.0f}'),
            ], className='summary-stat'),
            html.Div(children=[
                html.H2(id='assists', children=f'AST: {assists_per_game:.0f}'),
            ], className='summary-stat'),
        ]),
    ]),

])


@app.callback(
    Output('season-select', 'options'),
    Output('season-select', 'value'),
    Output('points', 'children'),
    Output('rebounds', 'children'),
    Output('assists', 'children'),
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
    
    games_played = player_stats.at[season_index, 'GP']
    points_per_game = player_stats.at[season_index, 'PTS'] / games_played
    rebounds_per_game = player_stats.at[season_index, 'REB'] / games_played
    assists_per_game = player_stats.at[season_index, 'AST'] / games_played
        
    return seasons_played, season, f'PPG: {points_per_game:.0f}', f'RPG: {rebounds_per_game:.0f}', f'APG: {assists_per_game:.0f}'


if __name__ == '__main__':
    app.run(debug=True)
