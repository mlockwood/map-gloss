#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'utils/tex_format_table.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def convert_to_tex_table(file, columns=0):
    reader = open(file, 'r')
    table = []
    for row in reader:
        line = row.rstrip()
        line = line.split(',')
        if columns:
            while len(line) < columns:
                line.append('')
        line = ' & '.join(line)
        line = line.rstrip()
        line += r'\\' + '\n'
        table.append(line)
    writer = open(file + '_tex_table', 'w')
    for line in table:
        writer.write(line)
    return True

#convert_to_tex_table('standard_values', columns=4)

import re
def convert_tex_table_to_percent(file):
    reader = open(file, 'r')
    table = []
    for row in reader:
        temp = []
        line = row.rstrip()
        line = line.split()
        for item in line:
            if re.search('[0|1]\.d*', item):
                item = float(item)
                item = int(round(item * 100))
                item = str(item) + '\%'
            temp.append(item)
        table.append(' '.join(temp) + '\n')
    writer = open(file + '_converted', 'w')
    for line in table:
        writer.write(line)
    return True


convert_tex_table_to_percent('tex_tables')
