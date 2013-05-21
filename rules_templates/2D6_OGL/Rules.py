# Copyright (c) Simon Dominic Hibbs 2012. All rights reserved.
# 2D6 OGL compatible rules file
# The entirety if this file is designated as Open Content.
# Refer to the file OGL_License.txt for details
#
# Deprecated - remove
#from model import Foundation
#from log import *

import random

from D6_OGL import *


DESCRIPTION = "A 2D6 OGL compatible SF RPG rules file for StarBase"

# The log module provides services for writing to the application log file.
# Try not to over-use it as the log file will get spammy. To write a log entry
# call it like this:
# debug_log('My log message ' + str(some_interesting_value))
#
# Note that the single parameter to the debug_log function must be a string,
# so you can't treat it like a print function, with comma separated values.


# Convenience functions

def zd(n):
    # return a number from 0 to n inclusive
    return random.randint(0, n - 1)

def d6():
    # Return a number from 1 to 6 inclusive
    return random.randint(1, 6)

# because the world attribute codes are keys in a dictionary they are unordered.
# The "codes" list is used to preserve key ordering.
codes = ['0', '1', '2', '3', '4', '5', '6', '7',
         '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
         'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']


# The API between this script and the main application consists of the
# attributeDefinitions list and the generateWorld() function. If these
# are renamed or not implemented correctly the App will break.

# A SEC file is a format used to exchange world data between legacy SF RPG software tools.
# The world co-ordinates in a SEC file cover a hex patch 32 hexes wide and 40 hexes high.
# To support SEC file import, a rules file must define at least 8 attributes,
# with codes defined to cover the range of values present in SEC files. Refer to
# SEC file format documentation for details.
# 
supportsSecFileImport = False

# This list is read by the main Application to access the world definitions.
attributeDefinitions = [starport_data,
                        size_data,
                        atmosphere_data,
                        hydrographic_data,
                        population_data,
                        government_data,
                        law_level_data,
                        tech_level_data,
                        system_data]

# The App calls this function to obtain stats when a world is first created,
# or is re-generated. This is a very basic implementation that just randomises
# each attribute. A simpleset of modifiers is applied to the 'Biosphere'
# attribute for demonstration purposes.
# The function returns a list of attribute codes, which match the attributes
# in the attributeDefinitions list. The two lists must be the same length and
# the attribute definitions must contain definitions for the codes returned
# by this function.
def generateWorld():
    
    dm = 0

    # Convenience function to turn random numbers into code strings,
    # while normalising out of range values.
    def numberToCode(number):
        if number < 0: number = 0
        elif number > 5: number = 5
        
        return codes[number]

    if (d6() + d6()) >= 10:
        gas_giant = False
    else:
        gas_giant = True

    if (d6() + d6()) >= 8:
        belts = False
    else:
        belts = True

    #Starport
    port_roll = d6() + d6()
    if port_roll <= 2:
        starport = 'X'
    elif port_roll in [3, 4]:
        starport = 'E'
    elif port_roll in [5, 6]:
        starport = 'D'
    elif port_roll in [7, 8]:
        starport = 'C'
    elif port_roll in [9, 10]:
        starport = 'B'
    elif port_roll >= 11:
        starport = 'A'

    # Size
    size_roll = d6() + d6() - 2
    size = numberToCode(size_roll)

    # Atmosphere
    atmo_roll = d6() + d6() - 7 + size_roll
    if atmo_roll <= 0: atmo_roll = 0
    atmosphere = numberToCode(atmo_roll)

    # Temperature
    if atmo_roll <= 1: temperature = 'Extreme Swings'
    else:
        if atmo_roll <= 3: dm = -2
        elif atmo_roll <= 5 or atmosphere == 'E': dm = -1
        elif atmo_roll <= 7: dm = 0
        elif atmo_roll <= 9: dm = 1
        elif atmosphere in ['A', 'D', 'F']: dm = 2
        elif atmosphere in ['B', 'C']: dm = 6
        temp_roll = d6() + d6() + dm
        if temp_roll <= 2: temperature = 'Frozen'
        elif temp_roll <= 4: temperature = 'Cold'
        elif temp_roll <= 9: temperature = 'Temperate'
        elif temp_roll <= 11: temperature = 'Hot'
        elif temp_roll >= 12: temperature = 'Roasting'

    #Hydrographics
    if size in ['0', '1']:
        hydrographics = '0'
    else:
        if atmosphere in ['0', '1', 'A', 'B', 'C']:
            dm = -4
        if temperature == 'Hot' : dm = dm - 2
        elif temperature == 'Roasting': dm = dm - 6

        hydro_roll = d6() + d6() - 7 + size_roll + dm
        if hydro_roll <= 0: hydro_roll = 0
        elif hydro_roll >= 10 : hydro_roll = 10

        hydrographics = numberToCode(hydro_roll)

    #Population
    pop_roll = d6() + d6() - 2
    population = numberToCode(pop_roll)

    #Government
    gov_roll = d6() + d6() - 7 + pop_roll
    if gov_roll <= 0 : gov_roll = 0
    elif gov_roll >= 13: gov_roll = 13
    government = numberToCode(gov_roll)

    #Law Level
    law_roll = d6() + d6() - 7 + gov_roll
    if law_roll <= 0 : law_roll = 0
    elif law_roll >= 9: law_roll = 9
    law_level = numberToCode(law_roll)

    #Technology Level
    tldm = 0
    if starport == 'A' : tldm = tldm + 6
    elif starport == 'B': tldm = tldm + 4
    elif starport == 'C': tldm = tldm + 2
    elif starport == 'X': tldm = tldm - 4
    if size in ['0', '1'] : tldm = tldm + 2
    elif size in ['2', '3', '4']: tldm = tldm + 1
    if atmosphere in ['0', '1', '2', '3', 'A', 'B', 'C', 'D', 'E', 'F']:
        tldm = tldm + 1
    if hydrographics in ['0', '9']: tldm = tldm + 1
    elif hydrographics == 'A' : tldm = tldm + 2
    if population in ['1', '2', '3', '4', '5', '9']: tldm = tldm + 1
    elif population == 'A': tldm = tldm + 2
    elif population == 'B': tldm = tldm + 3
    elif population == 'C': tldm = tldm + 4
    if government in ['0', '5'] : tldm = tldm + 1
    elif government == '7': tldm = tldm + 2
    elif government in ['D', 'E'] : tldm = tldm - 2
    tl_roll = d6() + tldm
    if tl_roll <= 0: tl_roll = 0
    tech_level = numberToCode(tl_roll)

    # System data attribute value is always the same,
    # but the description text is generated
    system_data='0'


    # Trade code generation
    trade_list = []

    if atmosphere in ['4', '5', '6', '7', '8', '9'] \
       and hydrographics in ['4', '5', '6', '7', '8'] \
       and population in ['5', '6', '7']:
        trade_list.append('Ag')
        tradeAg = True
    else:
        tradeAg = False

    if size == '0' \
       and atmosphere == '0' \
       and hydrographics == '0':
        trade_list.append('As')
        tradeAs = True
    else:
        tradeAs = False

    if population == '0' \
       and government == '0' \
       and law_level == '0':
        trade_list.append('Ba')
        tradeBa = True
    else:
        tradeBa = False

    if codes.index(atmosphere) >= 2 \
       and hydrographics == '0':
        trade_list.append('De')
        tradeDe = True
    else:
        tradeDe = False

    if codes.index(atmosphere) >= 10 \
       and codes.index(hydrographics) >= 1:
        trade_list.append('Fl')
        tradeFl = True
    else:
        tradeFl = False

    if atmosphere in ['4', '5', '6', '7', '8', '9'] \
       and hydrographics in  ['4', '5', '6', '7', '8']:
        trade_list.append('Ga')
        tradeGa = True
    else:
        tradeGa = False

    if codes.index(population) >= 9:
        trade_list.append('Hi')
        tradeHi = True
    else:
        tradeHi = False

    if codes.index(tech_level) >= 12:
        trade_list.append('Ht')
        tradeHt = True
    else:
        tradeHt = False

    if atmosphere in ['0', '1'] \
       and codes.index(hydrographics) >= 1:
        trade_list.append('IC')
        tradeIC = True
    else:
        tradeIC = False

    if atmosphere in ['0', '1', '2', '4', '7', '9'] \
       and codes.index(population) >= 9:
        trade_list.append('In')
        tradeIn = True
    else:
        tradeIn = False

    if codes.index(tech_level) <= 5:
        trade_list.append('Lt')
        tradeLt = True
    else:
        tradeLt = False

    if atmosphere in ['0', '1', '2', '3'] \
       and hydrographics in ['0', '1', '2', '3'] \
       and codes.index(population) >= 6:
        trade_list.append('Na')
        tradeNa = True
    else:
        tradeNa = False

    if population in ['4', '5', '6']:
        trade_list.append('NI')
        tradeNI = True
    else:
        tradeNI = False

    if atmosphere in ['2', '3', '4', '5'] \
       and hydrographics in ['0', '1', '2', '3']:
        trade_list.append('Po')
        tradePo = True
    else:
        tradePo = False

    if atmosphere in ['6', '8'] \
       and population in ['6', '7', '8']:
        trade_list.append('Ri')
        tradeRi = True
    else:
        tradeRi = False

    if atmosphere == '0':
        trade_list.append('Va')
        tradeVa = True
    else:
        tradeVa = False

    if hydrographics == 'A':
        trade_list.append('Wa')
        tradeWa = True
    else:
        tradeWa = False

    trade_codes = ' '.join(trade_list)

    if gas_giant:
        GG = 'Yes'
    else:
        GG = 'No'

    if belts:
        AB = 'Yes'
    else:
        AB = 'No'

    base = ''
    stellar = ''

    system_text = "Bases:".ljust(15) + base + "\n" +\
                  "Trade:".ljust(15) + trade_codes + "\n" +\
                  "Asteroids:".ljust(15) + str(AB) + "\n" +\
                  "Gas Giant(s):".ljust(15) + str(GG) + "\n" +\
                  "Star Data:".ljust(15) + stellar + "\n"


    # Building the list of generated stats to return to the application 
    stats = [starport, size, atmosphere, hydrographics, population, 
           government, law_level, tech_level, system_data]

    # You also need to return any customised text to go with the attributes.
    # If you want to use the default text for an attribute, just leave the
    # string empty.
    descriptions = ['',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    system_text]
    
    # Both returned parameters must be lists, NOT tupples
    return (stats, descriptions)


if __name__ == '__main__':
    world_stats, world_descriptions = generateWorld()
    report='World Name:\n'
    report += 'Allegiance:\n'
    report += 'Starport:'.ljust(15) + world_stats[0] + '\t' + starport_data["Code Data"][world_stats[0]]["Label"] + '\n'
    report += 'Size:'.ljust(15) + world_stats[1] + '\t' + size_data["Code Data"][world_stats[1]]["Label"] + '\n'
    report += 'Atmosphere:'.ljust(15) + world_stats[2] + '\t' + atmosphere_data["Code Data"][world_stats[2]]["Label"] + '\n'
    report += 'Hydrographics:'.ljust(15) + world_stats[3] + '\t' + hydrographic_data["Code Data"][world_stats[3]]["Label"] + '\n'
    report += 'Population:'.ljust(15) + world_stats[4] + '\t' + population_data["Code Data"][world_stats[4]]["Label"] + '\n'
    report += 'Government:'.ljust(15) + world_stats[5] + '\t' + government_data["Code Data"][world_stats[5]]["Label"] + '\n'
    report += 'Law Level:'.ljust(15) + world_stats[6] + '\t' + law_level_data["Code Data"][world_stats[6]]["Label"] + '\n'
    report += 'Tech Level:'.ljust(15) + world_stats[7] + '\t' + tech_level_data["Code Data"][world_stats[7]]["Label"] + '\n\n'
    report += 'System Data' + '\n'
    report += world_descriptions[8] + '\n'
    report += 'Starport\n'
    report += starport_data["Code Data"][world_stats[0]]["Description"] + '\n\n'
    report += 'Size\n'
    report += size_data["Code Data"][world_stats[1]]["Description"] + '\n\n'
    report += 'Atmosphere\n'
    report += atmosphere_data["Code Data"][world_stats[2]]["Description"] + '\n\n'
    report += 'Hydrographics\n'
    report += hydrographic_data["Code Data"][world_stats[3]]["Description"] + '\n\n'
    report += 'Population\n'
    report += population_data["Code Data"][world_stats[4]]["Description"] + '\n\n'
    report += 'Government\n'
    report += government_data["Code Data"][world_stats[5]]["Description"] + '\n\n'
    report += 'Law Level\n'
    report += law_level_data["Code Data"][world_stats[6]]["Description"] + '\n\n'
    report += 'Tech Level\n'
    report += tech_level_data["Code Data"][world_stats[7]]["Description"] + '\n\n'

    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'wb') as f:
            f.write(report)
    else:
        print report
    
