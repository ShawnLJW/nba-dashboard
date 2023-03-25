from dash import Dash, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from nba_api.stats.static.players import get_players
from nba_api.stats.static.teams import get_teams
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playerdashboardbyyearoveryear
from nba_api.stats.endpoints import playergamelog

from plotting import plot_shotchart
from layouts import index

players = pd.DataFrame(get_players())
players = players.set_index('id')
teams = pd.DataFrame(get_teams())
teams = teams.set_index('id')

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = index()

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
    Output('gamelog', 'children'),
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
    
    shots, _ = shotchartdetail.ShotChartDetail(team_id, player_id, season_nullable=season).get_data_frames()
    shotchart = plot_shotchart(shots)
    
    games = playergamelog.PlayerGameLog(player_id, season).get_data_frames()[0]
    games = games[['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']]
    gamelog = dash_table.DataTable(games.to_dict('records'), [{"name": i, "id": i} for i in games.columns])
        
    return seasons_played, season, headshot_src, player, team, f'{points_per_game:.1f}', f'{rebounds_per_game:.1f}', f'{assists_per_game:.1f}', shotchart, gamelog


if __name__ == '__main__':
    app.run(debug=True)
