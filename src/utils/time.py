import re


def convert_to_24_plus_time(date0, date1, seconds=True):
    if date0.day != date1.day:
        if seconds:
            return ':'.join(pad_time(t) for t in [date1.hour + 24, date1.minute, date1.second])
        else:
            return ':'.join(pad_time(t) for t in [date1.hour + 24, date1.minute])
    else:
        if seconds:
            return date1.strftime('%H:%M:%S')
        else:
            return date1.strftime('%H:%M')


def convert_to_24_time(time, seconds=True):
    time = re.split(':', time)
    hour = int(time[0])
    hour %= 24
    if seconds:
        return ':'.join(pad_time(t) for t in [hour] + time[1:])
    else:
        return ':'.join(pad_time(t) for t in [hour, time[1]])


def pad_time(time_unit):
    return '0' + str(time_unit) if len(str(time_unit)) == 1 else str(time_unit)


def to_list(time):
    if isinstance(time, str):
        time = re.sub(':', '', time)
    time = '{0:04d}'.format(int(time))
    return [time[:2], time[2:]]
