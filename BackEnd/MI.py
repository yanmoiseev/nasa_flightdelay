### place holder for MI input and output####
import math

def calculate(d):  # d is the input dictionary
    ml_list = []
    ml_list.extend(convert_cloud(d['cloud_cover_amount']))
    ml_list.append(round(int(d['dew_point']) / 5 * 9 + 32) * 10)
    ml_list.append(round(int(d['temperature']) / 5 * 9 + 32) * 10)
    ml_list.append(int(d['wind_speed']) * 2.23694 * 10)
    ml_list.append(int(d['wind_direction']))
    # TODO
    ml_list.append(int(d['day']) + 1)

    return ml_list


def convert_cloud(cover_amount):
    # broken, clear, few, overcast, scattered
    cover_amount = int(cover_amount) / 100 * 8

    cover_amount = math.ceil(cover_amount)

    clear = 100 if cover_amount == 0 else 0
    few = 100 if cover_amount == 1 else 0
    overcast = 100 if cover_amount == 8 else 0
    scatter = 100 if cover_amount in range(2, 5) else 0
    broken = 100 if cover_amount in range(5, 8) else 0

    return (broken, clear, few, overcast, scatter)