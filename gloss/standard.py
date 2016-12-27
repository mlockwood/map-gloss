from utils.data_model import DataModel
from utils.IOutils import find_path


class Gram(DataModel):

    json_path = '{}/gloss/data/standard_grams.json'.format(find_path('map_gloss'))
    objects = {}

    def set_objects(self):
        Gram.objects[self.leipzig.lower()] = self
        Gram.objects[self.gold_ontology.lower()] = self


class Value(DataModel):

    json_path = '{}/gloss/data/standard_values.json'.format(find_path('map_gloss'))
    objects = {}

    def set_objects(self):
        Value.objects[self.gloss.lower()] = self


Gram.load()
Value.load()
