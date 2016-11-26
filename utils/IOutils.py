import json
import os
import re


def set_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def set_file_directory(file):
    if not os.path.isdir(os.path.dirname(os.path.realpath(file))):
        os.makedirs(os.path.dirname(os.path.realpath(file)))


def load_json(file, cls):
    with open(file, 'r') as infile:
        [cls(**obj) for obj in json.load(infile)]


def export_json(file, cls):
    with open(file, 'w') as outfile:
        if 'get_json' in dir(cls):
            json.dump(list(cls.objects[o].get_json() for o in sorted(cls.objects.keys())), outfile, indent=4,
                      sort_keys=True)
        else:
            json.dump(list(cls.objects[o].__dict__ for o in sorted(cls.objects.keys())), outfile, indent=4,
                      sort_keys=True)


def json_to_txt(json_file, txt_file, header, order=None, booleans=True, defaults={}, conversions={}, filtered={}):
    writer = open(txt_file, 'w')
    writer.write('{}\n'.format(','.join(header)))
    with open(json_file, 'r') as infile:
        for obj in json.load(infile):
            accept = True

            # If no order was provided use alphabetical key order
            if not order:
                order = []
                for key in sorted(obj.keys()):
                    order.append(key)
                # writer.write('{}\n'.format(','.join(str(s) for s in order)))

            # Add defaults if needed
            for key in defaults:
                obj[key] = defaults[key]

            # Make conversions if needed
            for key in conversions:
                obj[key] = re.sub(conversions[key][0], conversions[key][1], obj[key])

            # Use filter
            for key in filtered:
                if obj[key] not in filtered[key]:
                    accept = False

            if not accept:
                continue

            # Write row values
            row = []
            for key in order:
                try:
                    row += [obj[key]] if booleans or not isinstance(obj[key], bool) else [int(obj[key])]
                except KeyError:
                    # Handle different naming conventions in key of 'id' field
                    if re.search('_id', key) and 'id' in obj:
                        row += [obj['id']]
            writer.write('{}\n'.format(','.join(str(s) for s in row)))


def txt_to_json(txt_file, json_file):
    reader = open(txt_file, 'r')
    rows = []
    for row in reader:
        row = row.rstrip()
        rows.append(re.split(',', row))
    reader.close()

    data = []
    for row in rows[1:]:
        data.append(dict((k, v) for k, v in zip(rows[0], row)))

    with open(json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def txt_writer(matrix, file):
    if not matrix or len(matrix) == 1:
        return False

    set_directory(os.path.dirname(file))
    writer = open(file, 'w')

    # Write header
    writer.write('{}\n'.format(','.join(str(s) for s in matrix[0])))
    # Write rows
    for row in sorted(matrix[1:]):
        writer.write('{}\n'.format(','.join(str(s) for s in row)))
    writer.close()
    return True
