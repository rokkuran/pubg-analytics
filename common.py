import yaml

from pubg_python import PUBG, Shard


class Configuration:
  def __init__(self):
    config = yaml.safe_load(open('config.yml'))
    self.API_KEY = config['API_KEY']
    self.IMG_DIR = config['IMG_DIR']
    self.MAP_SCALE_FACTOR = config['MAP_SCALE_FACTOR']

    self.MAP_IMG = {
      "Desert_Main": "{}/miramar_map.jpg".format(self.IMG_DIR),
      "Erangel_Main": "{}/erangel_map.jpg".format(self.IMG_DIR),
      "Savage_Main": "{}/sanhok_map.jpg".format(self.IMG_DIR)}


class API(Configuration):
  def __init__(self, shard):
    Configuration.__init__(self)
    self.api = PUBG(self.API_KEY, shard)


class Match(API):
  def __init__(self, match_id, shard=Shard.PC_OC):
    API.__init__(self, shard)
    self.match_id = match_id
    self.match = self.api.matches().get(match_id)