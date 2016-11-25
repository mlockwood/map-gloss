import math
import re


def validate_dms(gps):
    if parse_dms(gps):
        pass


def parse_dms(gps):
    return [x for x in re.split('[\'’\"”°]', re.sub(' ', '', gps.replace('\\', ''))) if x]


def factor_direction(gps, direction):
    if direction.lower() == 'n' or direction.lower() == 'e':
        return gps
    elif direction.lower() == 's' or direction.lower() == 'w':
        return 0 - gps
    else:
        raise ValueError('A GPS point has an invalid direction of {}.'.format(direction))


def dms_to_dd(gps):
    try:
        gps = parse_dms(gps)
        return factor_direction(int(gps[0]) + (int(gps[1]) / 60) + (float(gps[2]) / 3600), gps[3])
    except:
        return None


def tuple_to_dict(coord):
    return {'lat': coord[0], 'lng': coord[1]}


def haversine(x, y):
    if not isinstance(x, dict):
        raise TypeError('Haversine function\'s x parameter is not a dictionary.')
    if not isinstance(y, dict):
        raise TypeError('Haversine function\'s y parameter is not a dictionary.')

    # Set lat/lng for haversine
    lat = y['lat'] - x['lat']
    lng = y['lng'] - x['lng']

    # Calculate haversine
    a = math.sin(lat/2) ** 2 + math.cos(x['lat']) * math.cos(y['lat']) * math.sin(lng/2) ** 2
    c = 2 * math.asin(a ** 0.5)

    # Return haversine distance in kilometers
    return c * 6371

