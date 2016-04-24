### place holder for MI input and output####
import pickle

pickle_file = open("lingreg.p",'rb')
rreg = pickle.load(pickle_file)


def calculate(d):  # d is the input dictionary
    # day of month, day of week, dept time, arr time,
    # elapse, distance, cloud clear, dew point, temp ,
    # wind speed, win dir

    ml_list = []

    ml_list.append(int(d['day_of_month']))
    ml_list.append(int(d['day']) + 1)
    ml_list.append(int(d['dep_time']))
    ml_list.append(int(d['arr_time']))
    ml_list.append(int(d['elapsed_time']))
    ml_list.append(int(d['distance']))
    ml_list.append(int(d['cloud_cover_amount']))

    # ml_list.extend(convert_cloud(d['cloud_cover_amount']))
    ml_list.append(round(int(d['dew_point']) / 5 * 9 + 32) * 10)
    ml_list.append(round(int(d['temperature']) / 5 * 9 + 32) * 10)
    ml_list.append(int(d['wind_speed']) * 2.23694)
    ml_list.append(int(d['wind_direction']))
    # return ml_list
    return rreg.predict(ml_list)

def convert_cloud(cover_amount):
    # broken, clear, few, overcast, scattered
    clear = 100 if cover_amount == 0 else 0
    few = 100 if cover_amount == 1 else 0
    overcast = 100 if cover_amount == 8 else 0
    scatter = (cover_amount - 1 % 3) * 100 if cover_amount in range(2, 5) else 0
    broken = (cover_amount - 1 % 3) * 100 if cover_amount in range(5, 8) else 0

    return (broken, clear, few, overcast, scatter)


