'''
this module converts csv file to flat json file
'''

import csv,os

CSVF = os.path.join("airports_latlong.csv")

dictl = []
def csvdict():
    ''' writes the csv file to dictionary '''
    with open (CSVF) as csvfd:
        dictf = csv.DictReader(csvfd)# by default first row is used for keys
        for line in dictf:
        	dictl.append(line)
    return dictl

print csvdict()


