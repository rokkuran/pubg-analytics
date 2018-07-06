import csv
import yaml

import numpy as np
import pandas as pd

from pubg_python import PUBG, Shard
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")



IMG_DIR = "c:/workspace/pubg-analytics/img"

MAP_IMG = {
  "Desert_Main": "{}/miramar_map.jpg".format(IMG_DIR),
  "Erangel_Main": "{}/erangel_map.jpg".format(IMG_DIR),
  "Savage_Main": "{}/sanhok_map.jpg".format(IMG_DIR)
}

MAP_SCALE_FACTOR = {
  "Desert_Main": 600,
  "Erangel_Main": 600,
  "Savage_Main": 300
}


class PlayerLocationHistory(object):
  """"""
  def __init__(self, name):
    self.name = name
    self.x = []
    self.y = []
    self.z = []
  
  def update(self, x, y, z):
    self.x.append(x)
    self.y.append(y)
    self.z.append(z)


def participant_names(roster):
  return [participant.name for participant in roster.participants]


def get_team(match_id, player_name):
  """"""
  match = api.matches().get(match_id)
  rosters = match.rosters

  for roster in rosters:
    names = participant_names(roster)
    if player_name in names:
      return names


def get_winners(rosters):
  for i, roster in enumerate(rosters):
    if roster.won == 'true':
      return i, participant_names(roster)


# TODO: make argument telemetry instead of match_id
def get_game_state_history(match_id):
  """"""
  match = api.matches().get(match_id)
  asset = match.assets[0]
  telemetry = api.telemetry(asset.url)

  log_game_state = telemetry.events_from_type('LogGameStatePeriodic')

  game_state_history = []
  for gs in log_game_state:

    game_state_history.append([
      gs.game_state.elapsed_time, 
      round(gs.game_state.elapsed_time / 60), 
      gs.game_state.num_alive_teams, 
      gs.game_state.num_alive_players,
      round(gs.game_state.safety_zone_position['x']),
      round(gs.game_state.safety_zone_position['y']),
      round(gs.game_state.safety_zone_position['z']),
      round(gs.game_state.safety_zone_radius),
      round(gs.game_state.poison_gas_warning_position['x']),
      round(gs.game_state.poison_gas_warning_position['y']),
      round(gs.game_state.poison_gas_warning_radius)
    ])

  header = (
    'elapsed_time_s', 
    'elapsed_time_m', 
    'num_alive_teams',
    'num_alive_players',
    'safety_zone_position_x',
    'safety_zone_position_y',
    'safety_zone_position_z',
    'safety_zone_radius',
    'poison_gas_warning_position_x',
    'poison_gas_warning_position_y',
    'poison_gas_warning_radius'
  )

  return pd.DataFrame(game_state_history, columns=header)


def get_zones(df):
  """"""
  zones = []

  # for i in range(2, len(df)):
  #   if df.safety_zone_radius[i] == df.safety_zone_radius[i-1]:
  #     xyr = [df.safety_zone_position_x[i], df.safety_zone_position_x[i], df.safety_zone_radius[i]]
  #     if xyr not in zones:
  #       zones.append(xyr)

  # using poison gas warnings
  for i in range(2, len(df)):
    if df.poison_gas_warning_radius[i] == df.poison_gas_warning_radius[i-1]:
      xyr = [df.poison_gas_warning_position_x[i], df.poison_gas_warning_position_y[i], df.poison_gas_warning_radius[i]]
      if xyr not in zones:
        zones.append(xyr)

  return zones



if __name__ in "__main__":

  config = yaml.safe_load(open('config.yml'))
  API_KEY = config['API_KEY']
  api = PUBG(API_KEY, Shard.PC_OC)

  # match_id = "00c10698-6e0a-40f5-8e78-083696d199d8"  # miramar/squad
  # match_id = "2a0346f6-2493-4deb-beb3-151af50ecf19"  # erangel/squad
  # match_id = "1859feb8-e65e-46eb-9ef0-555082002695"  # sanhok/squad
  # match_id = "1e22f335-8e59-4e1f-ad50-f85bd66fb244"  # erangel/squad
  # match_id = "b2a0a46b-df3c-40fe-8622-15baa76d78b5"  # miramar/squad
  match_id = "68a03b73-8b2f-4f2c-9202-768a5e43d2ea"  # sanhok/squad

  match = api.matches().get(match_id)
  print(match.map)

  asset = match.assets[0]
  telemetry = api.telemetry(asset.url)

  log_player_positions = telemetry.events_from_type('LogPlayerPosition')

  player_name = "eponymoose"
  team = get_team(match_id, player_name)
  print(team)

  players = {name: PlayerLocationHistory(name) for name in team}
  for p in log_player_positions:
    if p.elapsed_time > 0:
      if p.character.name in team:
        players[p.character.name].update(p.character.location.x, p.character.location.y, p.character.location.z)

  # game state manipulation
  game_state_history = get_game_state_history(match_id)
  zones = get_zones(game_state_history)

  # plotting begins
  img_px = 1364
  scaling_factor = MAP_SCALE_FACTOR[match.map]
  colours = ['magenta', 'y', 'cyan', 'lime']
  dpi = 96

  fig, ax = plt.subplots(figsize=(img_px/dpi, img_px/dpi), dpi=dpi)
  ax.axis('off')

  img = plt.imread(MAP_IMG[match.map])
  ax.imshow(img)

  # add zone circles
  for (x, y, r) in zones:
    ax.add_artist(
      plt.Circle(
        (x / scaling_factor, y / scaling_factor), r / scaling_factor, 
        fill=False, 
        ec='white'
      )
    )

  for i, player in enumerate(team):
    ax.plot(
      np.array(players[player].x) / scaling_factor, 
      np.array(players[player].y) / scaling_factor, 
      ls='-', lw=1, color=colours[i], label=player
    )

  ax.grid(False)
  plt.xlim(0, img_px)
  plt.ylim(img_px, 0)

  l = ax.legend(loc='lower left')
  for i, text in enumerate(l.get_texts()):
    text.set_color(colours[i])

  fig.subplots_adjust(bottom=0, top=1, left=0, right=1)

  output_path = 'c:/workspace/pubg-analytics/output/location_history_{}.png'.format(match_id)
  plt.savefig(output_path, dpi=dpi)