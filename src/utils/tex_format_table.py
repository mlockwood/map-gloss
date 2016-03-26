#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
