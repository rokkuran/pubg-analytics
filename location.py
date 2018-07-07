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


class API:
  def __init__(self, shard):
    config = yaml.safe_load(open('config.yml'))
    self.api = PUBG(config['API_KEY'], shard)


class Match(API):
  def __init__(self, match_id, shard=Shard.PC_OC):
    API.__init__(self, shard)
    self.match_id = match_id
    self.match = self.api.matches().get(match_id)


class Player:
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


class Telemetry(Match):
  """"""
  def __init__(self, match_id):
    Match.__init__(self, match_id)

    self.asset = self.match.assets[0]
    self.telemetry = self.api.telemetry(self.asset.url)

    self.players = {}
    
    self._log_game_states = None
    self._game_states = None

    self._log_player_positions = None
    self._player_positions = None

    self._zones = None
    self._sz_t = None

  @property
  def game_states(self):
    """"""
    if self._log_game_states is None:
      self._log_game_states = self.telemetry.events_from_type('LogGameStatePeriodic')

    if self._game_states is None:
      data = []
      for gs in self._log_game_states:

        data.append([
          gs.game_state.elapsed_time, 
          gs.game_state.num_alive_teams, 
          gs.game_state.num_alive_players,
          gs.game_state.safety_zone_position['x'],
          gs.game_state.safety_zone_position['y'],
          gs.game_state.safety_zone_position['z'],
          gs.game_state.safety_zone_radius,
          gs.game_state.poison_gas_warning_position['x'],
          gs.game_state.poison_gas_warning_position['y'],
          gs.game_state.poison_gas_warning_radius
        ])

      header = (
        'elapsed_time_s', 
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

      self._game_states = pd.DataFrame(data, columns=header)

    return self._game_states

  @property
  def player_positions(self):
    """"""
    if self._log_player_positions is None:
      self._log_player_positions = self.telemetry.events_from_type('LogPlayerPosition')

    if self._player_positions is None:
      self._player_positions = {}
      for p in self._log_player_positions:
        if p.elapsed_time > 0:
          name = p.character.name
          if name not in self._player_positions:
            self._player_positions[name] = Player(name)
          
          self._player_positions[name].update(p.character.location.x, p.character.location.y, p.character.location.z)
      
    return self._player_positions

  @property
  def zones(self):
    """
    Returns dict of time: (x, y, r) 
    where x, y are circle centre and r is the radius.
    time is in seconds; x, y, r are unscaled.
    """

    if self._zones is None:
      self._zones = {}

      previous_r = 0
      for i, row in self.game_states.iterrows():
        r = row['safety_zone_radius']

        if r == previous_r:
          xyr = [row['safety_zone_position_x'], row['safety_zone_position_y'], r]

          if xyr not in self._zones.values():
            self._zones[row['elapsed_time_s']] = xyr

        previous_r = r

    return self._zones

  def _participant_names(self, roster):
    return [participant.name for participant in roster.participants]

  def get_team(self, name):
    rosters = self.match.rosters

    for roster in rosters:
      names = self._participant_names(roster)
      if name in names:
        return names

  @property
  def sz_t(self):
    """
    Safety zone positions by time.
    returns dict - time: (x, y, r)
    """
    if self._sz_t is None:

      xyr = zip(
        self.game_states.safety_zone_position_x, 
        self.game_states.safety_zone_position_y, 
        self.game_states.safety_zone_radius)

      self._sz_t = dict(zip(self.game_states.elapsed_time_s, xyr))

    return self._sz_t

  def p_t(name):
    xy = zip(telemetry.player_positions[name].x, telemetry.player_positions[name].y)
    return dict(zip(telemetry.player_positions[name].t, xy))


def plot_location_overlay(telemetry, players):
   # plotting begins
  img_px = 1364
  scaling_factor = MAP_SCALE_FACTOR[telemetry.match.map]
  colours = ['magenta', 'y', 'cyan', 'lime']
  dpi = 96

  fig, ax = plt.subplots(figsize=(img_px/dpi, img_px/dpi), dpi=dpi)
  ax.axis('off')

  # TODO: match shouldn't be under telemetry?
  img = plt.imread(MAP_IMG[telemetry.match.map])
  ax.imshow(img)

  # add zone circles
  for (x, y, r) in telemetry.zones.values():
    ax.add_artist(
      plt.Circle(
        (x / scaling_factor, y / scaling_factor), r / scaling_factor, 
        fill=False, 
        ec='white'
      )
    )

  for i, player in enumerate(players):
    ax.plot(
      np.array(telemetry.player_positions[player].x) / scaling_factor, 
      np.array(telemetry.player_positions[player].y) / scaling_factor, 
      ls='-', lw=1
    )#, color=colours[i], label=player

  ax.grid(False)
  plt.xlim(0, img_px)
  plt.ylim(img_px, 0)

  fig.subplots_adjust(bottom=0, top=1, left=0, right=1)

  output_path = 'c:/workspace/pubg-analytics/output/location_history_{}.png'.format(telemetry.match_id)
  plt.savefig(output_path, dpi=dpi)



if __name__ in "__main__":
  match_id = "68a03b73-8b2f-4f2c-9202-768a5e43d2ea"

  telemetry = Telemetry(match_id)

  # print(telemetry.game_states)
  # print(telemetry.player_positions)
  # print(telemetry.zones)

  print(telemetry.get_team('eponymoose'))

  plot_location_overlay(telemetry, telemetry.get_team('eponymoose'))
