import location

import yaml

import numpy as np
# import pandas as pd

# from pubg_python import PUBG, Shard
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")



# TODO move to config file.
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


def plot_location_overlay(telemetry, players):
  """"""  

  # TODO: move img_px and scaling factors to config file.
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
  telemetry = location.Telemetry(match_id)

  print(telemetry.get_team('eponymoose'))
  plot_location_overlay(telemetry, telemetry.get_team('eponymoose'))