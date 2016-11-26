from utils.classes import DataModelTemplate


class Gram(DataModelTemplate):

    objects = {}

    def set_object_attrs(self):
        Gram.objects[self.leipzig] = self
        Gram.objects[self.gold_ontology] = self


class Value(DataModelTemplate):

    objects = {}

    def set_object_attrs(self):
        Value.objects[self.gloss] = self


Gram.load()
Value.load()