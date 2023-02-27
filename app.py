from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

from nba_api.stats.static.players import get_players
from nba_api.stats.static.teams import get_teams
from nba_api.stats.endpoints import playercareerstats
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
team = teams.at[player_stats.at[0, 'TEAM_ID'], 'full_name']
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
        
    team = teams.at[player_stats.at[season_index, 'TEAM_ID'], 'full_name']
        
    headshot_src = f'https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png'
    
    games_played = player_stats.at[season_index, 'GP']
    points_per_game = player_stats.at[season_index, 'PTS'] / games_played
    rebounds_per_game = player_stats.at[season_index, 'REB'] / games_played
    assists_per_game = player_stats.at[season_index, 'AST'] / games_played
        
    return seasons_played, season, headshot_src, player, team, f'{points_per_game:.1f}', f'{rebounds_per_game:.1f}', f'{assists_per_game:.1f}'


if __name__ == '__main__':
    app.run(debug=True)
