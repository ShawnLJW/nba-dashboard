import pandas as pd
from dash import html, dcc, dash_table

from nba_api.stats.static.players import get_players
from nba_api.stats.static.teams import get_teams
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playergamelog

from plotting import plot_shotchart

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
games = playergamelog.PlayerGameLog(player_id, season_id).get_data_frames()[0]
games = games[['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']]

def index():
    return html.Div(children=[
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

            html.Div(children=[
                html.Div(children=[
                    html.H2(id='points', children=f'{points_per_game:.1f}'),
                    html.P(children='Points Per Game'),
                ], className='summary-stat col-md-4'),
                html.Div(children=[
                    html.H2(id='rebounds', children=f'{rebounds_per_game:.1f}'),
                    html.P(children='Rebounds Per Game'),
                ], className='summary-stat col-md-4'),
                html.Div(children=[
                    html.H2(id='assists', children=f'{assists_per_game:.1f}'),
                    html.P(children='Assists Per Game'),
                ], className='summary-stat col-md-4'),
            ], className='row gx-5'),
            
            html.Div(
                children=[
                    dcc.Graph(id='shotchart', figure=plot_shotchart(shots), className='col-lg-4'),
                    
                    html.Div(children=[
                        dash_table.DataTable(
                            games.to_dict('records'),
                            [{"name": i, "id": i} for i in games.columns]
                        )
                    ], id='gamelog', className='col-lg-8')
                ], className='row')
            
        ]),

    ])