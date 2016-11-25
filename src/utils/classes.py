from src.utils.IOutils import load_json, export_json


class DataModelTemplate(object):

    json_path = ''
    objects = {}

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k != 'self']
        self.set_objects()
        self.set_object_attrs()

    def set_object_attrs(self):
        pass

    def set_objects(self):
        try:
            self.__class__.objects[self.id] = self
        except KeyError:
            raise NotImplementedError('DataModelTemplate classes must define a set_objects object method if the ' +
                                      'object\'s primary key is not `id`.')

    @classmethod
    def set_class_vars(cls):
        pass

    @classmethod
    def load(cls):
        # If only one path was provided
        if isinstance(cls.json_path, str):
            load_json(cls.json_path, cls)
        # If many paths were provided
        elif isinstance(cls.json_path, list) or isinstance(cls.json_path, tuple):
            for path in cls.json_path:
                load_json(path, cls)
        # Else raise error and alert user that load requires at least one JSON file
        else:
            raise ValueError('The class {} must have a file or list/tuple of files to load.'.format(str(cls)))
        cls.set_class_vars()

    @classmethod
    def export(cls):
        # If only one path was provided
        if isinstance(cls.json_path, str):
            export_json(cls.json_path, cls)
        # If many paths were provided only export to the first json_path
        elif isinstance(cls.json_path, list) or isinstance(cls.json_path, tuple):
            export_json(cls.json_path[0], cls)
        # Else raise error and alert user that load requires at least one JSON file
        else:
            raise ValueError('The class {} must have a file or list/tuple of files to load.'.format(str(cls)))

    @classmethod
    def print_stats(cls, view=10):
        print(cls.__name__, 'has a total of', len(cls.objects), 'objects.')
        index = len(cls.objects) if len(cls.objects) < view else view
        for key in list(cls.objects.keys())[:view]:
            print('\t', key, cls.objects[key].__dict__)