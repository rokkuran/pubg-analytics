from common import Match

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")



class Player:
  """"""
  def __init__(self, name):
    self.name = name
    self.x = []
    self.y = []
    self.z = []
    self.t = []
  
  def update(self, t, x, y, z):
    self.x.append(x)
    self.y.append(y)
    self.z.append(z)
    self.t.append(t)


class Dataset(Match):
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
          
          self._player_positions[name].update(
            p.elapsed_time, 
            p.character.location.x, 
            p.character.location.y, 
            p.character.location.z)
      
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
  
  def get_winners(self):
    for i, roster in enumerate(self.match.rosters):
      if roster.won == 'true':
        return self._participant_names(roster)

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

  def p_t(self, name):
    xy = zip(self.player_positions[name].x, self.player_positions[name].y)
    return dict(zip(self.player_positions[name].t, xy))

  def zone_edge_distance_t(self, name):
    """"""
    p_t = self.p_t(name)

    distance_from_zone_edge = []

    t_min = min(self.sz_t.keys())
    last_zone = self.sz_t[t_min]

    for i in range(t_min, max(p_t.keys())):      

      if i in self.sz_t:
        last_zone = self.sz_t[i]

      if i in p_t:
        zx, zy, zr = last_zone
        px, py = p_t[i]
        d = np.sqrt((px - zx)**2 + (py - zy)**2)  # distance from centre of zone
        distance_from_zone_edge.append((i, zr - d))

    return np.array(distance_from_zone_edge)



if __name__ in "__main__":
  match_id = "68a03b73-8b2f-4f2c-9202-768a5e43d2ea"

  dataset = Dataset(match_id)

  # print(dataset.game_states)
  # print(dataset.player_positions)
  # print(dataset.zones)

  # print(dataset.get_team('eponymoose'))

  print(dataset.zone_edge_distance_t('eponymoose'))
