# Copyright 2013 Simon Dominic Hibbs
import random

def zd(n):
    return random.randint(0, n - 1)

def numberToCode(number):
        codes = ["0", "1", "2", "3", "4", "5"]
        return codes[number]


worldTypeDescription(code):

data = {"0" : {[1]: "The only habitat is a crippled spaceship.",
               [2, 3]: "The population inhabits a single large " + \
        "habitat manufactured from a metalic asteroid or proto-planet, " + \
        "which is spun for artificial pseudo-gravity. ",
               [4, 5]: "There is a single main population centre " + \
               "formed from many smaller habitats joined together " + \
               "or in close proximity to each other.",
               [6] : "There are many small habitats scattered across " + \
               "the system."}
        }

    for data_code, data_options in data.items():
        if code == data_code:
            r = zd(6) + 1
            for numbers, txt in data_options.items():
                if r in numbers:
                    description = txt

    return description


def generateWorld():

    atmo_mod = 0; hydro_mod = 0; temp_mod = 0; resource_mod = 0
    bio_mod = 0; pop_mod = 0; culture_mod = 0; tech_mod = 0

    system_type = ['0', '1', '2', '2', '3', '3', '3', '4', '4', '5'].index(zd(10))

    if system_type in ['0']:
        atmo_type = '0'
    elif system_type in ['1', '2']:
        atmo_mod = ['0', '0', '1', '1', '2', '2', '3'].index(zd(7))
    elif system_type in ['3', '4']:
        atmo_type = ['0', '1', '2', '2', '3', '3', '3', '4', '4', '5'].index(zd(10))
    elif system_type in ['5']:
        atmo_type = ['0', '1', '2','3', '4', '5'].index(zd(10))

    temp_type = ['0', '1', '2', '2', '3', '3', '3', '4', '4', '5'].index(zd(10))

    
    if temp_type in ['0', '5']:
        hydro_mod = 0
    else:
        hydro_mod = +1

    if temp_type in ['0', '5']:
        hydro_type = '0'
    else:
        if atmo_type in ['0', '5']:
            hydro_mod = 0
        else:
            hydro_mod = +3
        hydro_type = ['0', '0', '1', '0', '1', '2', '3', '4', '5'].index(zd(6))
        
    
