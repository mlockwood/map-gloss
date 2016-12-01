from utils.classes import DataModelTemplate
from utils.functions import find_path


class Gram(DataModelTemplate):

    json_path = '{}/gloss/data/standard_grams.json'.format(find_path('map_gloss'))
    objects = {}

    def set_objects(self):
        Gram.objects[self.leipzig] = self
        Gram.objects[self.gold_ontology] = self


class Value(DataModelTemplate):

    json_path = '{}/gloss/data/standard_values.json'.format(find_path('map_gloss'))
    objects = {}

    def set_objects(self):
        Value.objects[self.gloss] = self


Gram.load()
Value.load()