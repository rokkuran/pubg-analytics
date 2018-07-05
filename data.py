import csv
import yaml

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pubg_python import PUBG, Shard
from datetime import datetime


config = yaml.safe_load(open('config.yml'))

API_KEY = config['API_KEY']


def convert_timestamp(s):
  """"""
  # return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
  return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_player_ids(names, verbose=False):
  """return player ids from usernames"""

  players = api.players().filter(player_names=names)

  if verbose:
    for player in players:
      print('{}: {}'.format(player.name, player.id))

  return players


def participant_names(roster):
  return [participant.name for participant in roster.participants]


def get_winners(rosters):
  for i, roster in enumerate(rosters):
    if roster.won == 'true':
      return i, participant_names(roster)


def print_match_history():
  player_names = ['eponymoose']
  # player_names = ['Stalkyard']

  players = api.players().filter(player_names=player_names)
  player = players[0]

  print("name: {}\nid: {}\n".format(player.name, player.id))

  matches = player.matches

  match_ids = [match.id for match in matches]

  matches = api.matches().filter(match_ids=match_ids)

  for i, match_id in enumerate(match_ids):
    match = api.matches().get(match_id)
    print("{}: {}; {}; {}; {}".format(
      i, match.id, datetime.strptime(match.created_at, "%Y-%m-%dT%H:%M:%SZ"), match.game_mode, match.map))

    rosters = match.rosters
    
    for roster in rosters:
      if any([participant.name in player_names for participant in roster.participants]):
        print([participant.name for participant in roster.participants])
        
        for participant in roster.participants:
          print("\t{}: kills={}; death_type={}; kill_place={}".format(
            participant.name, participant.kills, participant.death_type, participant.kill_place))
  #             print("winners(s): {}".format(roster.won))
    try:
      roster_index, winning_participants = get_winners(rosters)
      print("winners(s) [{}]: {}\n".format(roster_index, winning_participants))

    except TypeError:
      print('\nEXCEPTION! None type returned get_winners()\n')
      continue

  print('end')


def write_match_kill_details():

  non_player_kills = [
    "Damage_BlueZone",
    "Damage_Drown",
    "Damage_Explosion_RedZone",
    "Damage_Instant_Fall",
    "Damage_VehicleCrashHit"]

  player_names = ['eponymoose']
  players = api.players().filter(player_names=player_names)
  player = players[0]

  print("name: {}\nid: {}\n".format(player.name, player.id))

  matches = player.matches
  match_ids = [match.id for match in matches]

  match_id = match_ids[0]
  # match_id = "2a0346f6-2493-4deb-beb3-151af50ecf19"  # squad/erangel
  # match_id = "1deb2118-557e-4945-a8e1-81ae70bf62e3"
  # match_id = "42f94823-1e69-423e-983a-02f0973c9534"  # duo/sanhok

  match = api.matches().get(match_id)
  asset = match.assets[0]
  telemetry = api.telemetry(asset.url)

  player_kill_events = telemetry.events_from_type('LogPlayerKill')

  # print(player_kill_events)


  with open('c:/workspace/pubg-analytics/output/pubg_kill_events_{}.csv'.format(match.id), 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(["killer", "killer_team_id", "victim", "victim_team_id"])
    for i, event in enumerate(player_kill_events):
      
      # TODO: add in logic for suicides
      killer_team = event.killer.team_id
      
      if event.damage_type_category in non_player_kills:
        killer_name = event.damage_type_category
        killer_team = 0
      else:
        if event.killer.name == "":
          killer_name = event.damage_type_category + "_MISSING_KILLER"
        else:
          killer_name = event.killer.name

      writer.writerow([killer_name, event.killer.team_id, event.victim.name, event.victim.team_id])  



if __name__ in '__main__':

  api = PUBG(API_KEY, Shard.PC_OC)
  names = ['eponymoose', 'Stalkyard', 'Ritalin', 'yakabox']

  # get_player_ids(names, verbose=True)

  write_match_kill_details()


