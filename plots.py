import dataset
from common import Configuration, API


import yaml

import numpy as np
# import pandas as pd

# from pubg_python import PUBG, Shard
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")



def plot_location_overlay(dataset, players):
  """"""  

  # TODO: move img_px and scaling factors to config file.
  img_px = 1364

  scaling_factor = dataset.MAP_SCALE_FACTOR[dataset.match.map]
  colours = ['magenta', 'y', 'cyan', 'lime']
  dpi = 96

  fig, ax = plt.subplots(figsize=(img_px/dpi, img_px/dpi), dpi=dpi)
  ax.axis('off')

  # TODO: match shouldn't be under dataset?
  img = plt.imread(dataset.MAP_IMG[dataset.match.map])
  ax.imshow(img)

  # add zone circles
  for (x, y, r) in dataset.zones.values():
    ax.add_artist(
      plt.Circle(
        (x / scaling_factor, y / scaling_factor), r / scaling_factor, 
        fill=False, 
        ec='white'
      )
    )

  for i, player in enumerate(players):
    ax.plot(
      np.array(dataset.player_positions[player].x) / scaling_factor, 
      np.array(dataset.player_positions[player].y) / scaling_factor, 
      ls='-', lw=1
    )#, color=colours[i], label=player

  ax.grid(False)
  plt.xlim(0, img_px)
  plt.ylim(img_px, 0)

  fig.subplots_adjust(bottom=0, top=1, left=0, right=1)

  output_path = 'c:/workspace/pubg-analytics/output/location_history_{}.png'.format(dataset.match_id)
  plt.savefig(output_path, dpi=dpi)


def plot_distance_from_zone(dataset):
  """"""
  all_participants = dataset.player_positions.keys()

  plt.style.use("dark_background")
  fig, ax = plt.subplots(figsize=(14, 9))
  for i, player in enumerate(all_participants):
    zed = dataset.zone_edge_distance_t(player)
    ax.plot(zed[:, 0] / 60, zed[:, 1] / dataset.MAP_SCALE_FACTOR[dataset.match.map])  # convert x time values to minutes
  
  _, x_max = plt.xlim()
  plt.xlim(0, x_max)
  ax.hlines(0, 0, max(dataset.game_states.elapsed_time_s) / 60, 'white', lw=0.5)
  
  y_min, y_max = plt.ylim()
  ax.vlines(np.array(list(dataset.zones.keys())) / 60, y_min, y_max, 'white', lw=1.5)
  
  # ax.grid(False)
  ax.grid(color='white', ls='--', lw=1, alpha=0.25)

  plt.title("Player Distance from Safety Zone Edge")
  plt.xlabel("Time (m)\nVertical lines are new zone timepoints")
  plt.ylabel("Distance from Safety Zone Edge")

  plt.tight_layout()

  output_path = 'c:/workspace/pubg-analytics/output/distance_from_zone_all_{}.png'.format(dataset.match_id)
  plt.savefig(output_path)

  plt.close()


def plot_distance_from_zone_player_comparison(dataset, name=None):
  """"""
  all_participants = dataset.player_positions.keys()
  winners = dataset.get_winners()  # TODO: make property?

  player_specified = False if name is None else True
  if player_specified:
    team = dataset.get_team(name)
  else:
    team = []

  winner_label_used = False
  rest_label_used = False
  teammate_label_used = False

  plt.style.use("dark_background")

  # greys = ['#262626', '#333333', '#404040']

  fig, ax = plt.subplots(figsize=(14, 9))
  for i, player in enumerate(all_participants):
    zed = dataset.zone_edge_distance_t(player)
    
    # TODO: use slightly differnt variation on the colours to tell apart players

    if player in winners:
      # http://www.flatuicolorpicker.com/category/orange
      # colour = '#F5AB35'  # lightning yellow
      colour = '#F62459'  # radical red
      zorder = 200
      label = 'winners'
      alpha = 0.75
      
      if winner_label_used:
        label = None
      winner_label_used = True
        
    elif player == name:
      colour = '#22A7F0'  # picton blue
      zorder = 300
      label = player
      alpha = 1.0
    
    elif player in team:
      colour = '#2ECC71'  # shamrock
      zorder = 250
      label = 'teammates'
      alpha = 0.75
      
      if teammate_label_used:
        label = None
      teammate_label_used = True

    else:
      # colour = greys[i % 3]
      colour = '#666666'
      zorder = i
      label = 'rest'
      alpha = 0.3

      if rest_label_used:
        label = None
      rest_label_used = True

    ax.plot(
      zed[:, 0] / 60, 
      zed[:, 1] / dataset.MAP_SCALE_FACTOR[dataset.match.map], 
      color=colour, zorder=zorder, label=label, alpha=alpha
    )

  # plt.legend(facecolor='inherit')

  leg = ax.legend()
  leg.remove()
  ax.add_artist(leg)
  
  _, x_max = plt.xlim()
  plt.xlim(0, x_max)
  ax.hlines(0, 0, max(dataset.game_states.elapsed_time_s) / 60, 'white', lw=0.5)
  
  y_min, y_max = plt.ylim()
  ax.vlines(np.array(list(dataset.zones.keys())) / 60, y_min, y_max, 'white', lw=1.5)
  
  # ax.grid(False)
  ax.grid(color='white', ls='--', lw=1, alpha=0.10)

  plt.title("Player Distance from Safety Zone Edge")
  plt.xlabel("Time (m)\nVertical lines are new zone timepoints")
  plt.ylabel("Distance from Safety Zone Edge")

  plt.tight_layout()

  output_path = 'c:/workspace/pubg-analytics/output/distance_from_zone_comparison_{}.png'.format(dataset.match_id)
  plt.savefig(output_path)

  plt.close()



if __name__ in "__main__":
  # match_id = "68a03b73-8b2f-4f2c-9202-768a5e43d2ea"
  # match_id = "2a0346f6-2493-4deb-beb3-151af50ecf19"  # squad/erangel
  # match_id = "1deb2118-557e-4945-a8e1-81ae70bf62e3"
  # match_id = "42f94823-1e69-423e-983a-02f0973c9534"  # duo/sanhok
  # match_id = "1859feb8-e65e-46eb-9ef0-555082002695"  # squad/sanhok
  # match_id = "e15b4139-38f8-4e67-a6ae-2f0c7cb02881"  # erangel/squad lame
  # match_id = "64c6a84d-49b4-4c6c-943e-26bc8676b611"
  match_id = "9ff7d88c-0665-438a-9e73-c562c7eb0a46"
  
  ds = dataset.Dataset(match_id)

  # print(ds.get_team('eponymoose'))
  # plot_location_overlay(ds, ds.get_team('eponymoose'))
  # plot_distance_from_zone(ds)
  # plot_distance_from_zone_player_highlighted(ds, 'eponymoose')
  # plot_distance_from_zone_player_comparison(ds, 'eponymoose')
  # plot_distance_from_zone_player_comparison(ds)

  api = API()

  for i, (player, match) in enumerate(api.iter_player_matches('eponymoose')):
    ds = dataset.Dataset(match.id)

    try:
      plot_distance_from_zone_player_comparison(ds, 'eponymoose')

    except IndexError:
      print("INDEX ERROR! {}".format(i))
      continue
    
    except TypeError:
      print("TYPE ERROR! {}".format(i))
      continue