import dataset
from common import Configuration


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



def plot_distance_from_zone_player_highlighted(dataset, name):
  """"""
  all_participants = dataset.player_positions.keys()

  plt.style.use("dark_background")
  fig, ax = plt.subplots(figsize=(14, 9))
  for i, player in enumerate(all_participants):
    zed = dataset.zone_edge_distance_t(player)

    ax.plot(
      zed[:, 0] / 60, 
      zed[:, 1] / dataset.MAP_SCALE_FACTOR[dataset.match.map], 
      color='r' if player == name else 'grey'
    )
  
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

  output_path = 'c:/workspace/pubg-analytics/output/distance_from_zone_all_highlighted_{}.png'.format(dataset.match_id)
  plt.savefig(output_path)


def plot_distance_from_zone_player_comparison(dataset, name):
  """"""
  all_participants = dataset.player_positions.keys()
  winners = dataset.get_winners()  # TODO: make property?

  plt.style.use("dark_background")

  winner_label_used = False
  rest_label_used = False

  fig, ax = plt.subplots(figsize=(14, 9))
  for i, player in enumerate(all_participants):
    zed = dataset.zone_edge_distance_t(player)
    
    if player in winners:
      # http://www.flatuicolorpicker.com/category/orange
      colour = '#F5AB35'  # lightning yellow
      zorder = 200
      label = 'winners'
      
      if winner_label_used:
        label = None
      
      winner_label_used = True
        
    elif player == name:
      colour = '#f03434'  # cinnabar
      zorder = 300
      label = player

    else:
      colour = 'grey'
      zorder = i
      label = 'rest'
      # label = None

      if rest_label_used:
        label = None
      
      rest_label_used = True

    ax.plot(
      zed[:, 0] / 60, 
      zed[:, 1] / dataset.MAP_SCALE_FACTOR[dataset.match.map], 
      color=colour, zorder=zorder, label=label
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
  ax.grid(color='white', ls='--', lw=1, alpha=0.25)

  plt.title("Player Distance from Safety Zone Edge")
  plt.xlabel("Time (m)\nVertical lines are new zone timepoints")
  plt.ylabel("Distance from Safety Zone Edge")

  plt.tight_layout()

  output_path = 'c:/workspace/pubg-analytics/output/distance_from_zone_comparison_{}.png'.format(dataset.match_id)
  plt.savefig(output_path)



if __name__ in "__main__":
  match_id = "68a03b73-8b2f-4f2c-9202-768a5e43d2ea"
  dataset = dataset.Dataset(match_id)

  # print(dataset.get_team('eponymoose'))
  # plot_location_overlay(dataset, dataset.get_team('eponymoose'))
  # plot_distance_from_zone(dataset)
  # plot_distance_from_zone_player_highlighted(dataset, 'eponymoose')
  plot_distance_from_zone_player_comparison(dataset, 'eponymoose')