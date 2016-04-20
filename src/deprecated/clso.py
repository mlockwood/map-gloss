__author__ = 'Michael Lockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


import inspect
import re
import types


class CLSO:
    """Data format created by Michael Lockwood that stores files of
    classes and objects (hence the name CLS - class and O - ojbect).

    Note the following code option was tried in previous versions but
    was replaced:

    import ast
    ast.literal_eval() # Convert str to dict, tuple, list
    """

    objects = {}
    evaluation = ''

    def __init__(self, file, option='r'):
        self.file = open(str(file)+'.clso', option)
        CLSO.objects[file] = self

    def type_check(value):
        type_matches = []
        for method in dir(types):
            try:
                match = isinstance(value, eval('types.'+str(method)))
                if match:
                    type_matches.append(method)
            except:
                pass
        return type_matches

    def eval_list(L):
        S = '['
        L = L[1:-1]
        items = re.split(',', L)
        for item in items:
            item = re.sub(' ', '', item)
            if not item:
                continue
            if re.search('\'.*\'', item) or re.search('\".*\"', item):
                item = item[1:-1]
            if re.search('\[.*\]', item):
                S += CLSO.eval_list(L) + ','
            elif re.search('\'', item):
                item = re.sub('\'', '\\\'', item)
                S += '\'' + item + '\', '
            else:
                S += '\'' + item + '\', '
        if S[-2:] == ', ':
            S = S[:-2]
        S += ']'
        return S

    def str_list(L):
        return '\"' + CLSO.eval_list(L) + '\"'

    def load(self):
        clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        cls = ''
        values = {}
        for line in self.file:
            line = line.rstrip()
            # If blank, continue
            if not line:
                continue
            # If ID line set class to the value between the angle brackets
            if re.search('<[\w]*>', line):
                cls = line[1:-1]
            # If class variable process immediately
            elif line[0] == '$':
                exec(line[1:])
            # If value delimiter process the object and reset the value DS
            elif line == '@':
                for member in clsmembers:
                    if cls == member[0]:
                        # Add __init__ arguments
                        init_values = inspect.getargspec(eval(cls+'._init__'))
                        init_code = cls + '('
                        for value in init_values.args[1:]:
                            if value in values:
                                if re.search('\[.*\]', values[value]):
                                    init_code += (CLSO.str_list(values[value])
                                                  + ', ')
                                elif re.search('\'', values[value]):
                                    init_code += '\"' + values[value] + '\", '
                                else:
                                    init_code += '\'' + values[value] + '\', '
                                del values[value]
                            elif ('_'+value) in values:
                                if re.search('\[.*\]', values['_'+value]):
                                    init_code += (CLSO.str_list(
                                                  values['_'+value]) + ', ')
                                elif re.search('\'', values['_'+value]):
                                    init_code += ('\"' + values['_'+value] +
                                                  '\", ')
                                else:
                                    init_code += ('\'' + values['_'+value] +
                                                  '\', ')
                                del values['_'+value]
                            else:
                                raise ValueError('Missing argument in CLSO ' +
                                                 'object from ' + str(cls) +
                                                 ': ' + str(value))
                        init_code += ')'
                        obj = eval(init_code)
                        # Add all other values
                        for value in values:
                            # If not a Built-In Function or Method
                            try:
                                exec('CLSO.evaluation='+str(values[value]))
                                match = CLSO.type_check(CLSO.evaluation)
                                # If a Built-In Function or Method
                                if (match or values[value] == 'help' or
                                    values[value] == 'obj'):
                                    # STRING OPTION
                                    exec('obj.'+str(value) + '=\''+
                                        str(values[value] + '\''))
                                # If not a Built-In Function or Method
                                else:
                                    # VAR OPTION
                                    exec('obj.'+str(value)+'=' +
                                         str(values[value]))
                            except:
                                try:
                                    # STRING OPTION
                                    exec('obj.'+str(value) + '=\''+
                                         str(values[value] + '\''))

                                except:
                                    # TUPLE OPTION
                                    exec('obj.'+str(value) + '=\"'+
                                         str(values[value] + '\"'))
                values = {}
            # If close line process the object and reset the cls DS
            elif re.search('</[\w]*\>', line):
                cls = ''
            # If it is a value, process as value
            else:
                line = line.split('=')
                values[line[0]] = line[1]
        return True

    def _dump_helper(self, obj, cls_variables):
        methods = {}
        temp = inspect.getmembers(obj, inspect.ismethod)
        for method in temp:
            methods[method[0]] = True
        for value in dir(obj):
            if not re.search('__[\w]*__', value):
                if value not in methods and value not in cls_variables:
                    self.file.write(value + '=' + str(eval('obj.' + value))
                                     + '\n')
        self.file.write('@\n')
        return True

    def dump(self, obj):
        cls = str(obj._class__)[17:-2]
        if cls[0] == '.':
            cls = cls[1:]
        cls_variables = []
        for value in dir(eval(cls)):
            if not re.search('__[\w]*__', value):
                cls_variables.append(value)
        self.file.write('<' + cls + '>\n')
        self.dump_helper(obj, cls_variables)
        self.file.write('</' + cls + '>\n\n')
        return True

    def bulk_dump(self, cls):
        self.file.write('<' + cls + '>\n')
        cls_variables = []
        for value in dir(eval(cls)):
            if not re.search('__[\w]*__', value):
                cls_variables.append(value)
        cls_functions = {}
        for func in inspect.getmembers(eval(cls), inspect.isfunction):
            cls_functions[func[0]] = True
        for var in cls_variables:
            if var != 'objects' and var not in cls_functions:
                self.file.write('$' + cls + '.' + str(var) + '=' + str(
                                 eval(cls +'.' + str(var))) + '\n')
        for obj in eval(str(cls) + '.objects'):
            if isinstance(obj, tuple):
                self.dump_helper(eval(str(cls) + '.objects[' + str(obj) +
                                       ']'), cls_variables)
            elif isinstance(obj, str):
                self.dump_helper(eval(str(cls) + '.objects[\'' + str(obj) +
                                       '\']'), cls_variables)
            else:
                raise TypeError('Object must be string or tuple.')
        self.file.write('</' + cls + '>\n\n')
        self.file.close()

    def close(self):
        self.file.close()