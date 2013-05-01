# This file was authored by Simon Dominic Hibbs 2013, but copyright
# is not asserted. The file may be freely modified, distributed or used
# as a basis for derived works, either piblic domain, licensed or sold.
# This notice applies to this file only and not to any other file or script
# distributed with it.
# Default Rules File version 0.2.21
#from model import Foundation
import random
from log import *

# The log module provides services for writing to the application log file.
# Try not to over-use it as the log file will get spammy. To write a log entry
# call it like this:
# info_log('My log message ' + str(some_interesting_value))
#
# Note that the single parameter to the info_log function must be a string,
# so you can't treat it like a print function, with comma separated values.


# Convenience functions

def zd(n):
    # return a number from 0 to n inclusive
    return random.randint(0, n - 1)

def d6():
    # Return a number from 1 to 6 inclusive
    return random.randint(1, 6)


# World attributes such as 'Atmosphere', 'Technology', etc are each defined by
# a Python dictionary with the following keys:
# 'Name' :  The name of the attribute.
# 'Codes' : A list of one character codes used to identify discrete attribute
#           values. It is important because the codes in the 'Code data' dictionary
#           are unordered, so we need a way for the application to order the codes.
# 'Code Data': A dictionary with each key being a code. Each code references
#              a dictionary with two keys. 'Label' which is a short summary
#              of that code value used in buttons and drop-down lists, and
#              'Description' which is a more detailed explanation of what
#              that code means for use in text boxes and such. In tha App the
#              'Description' text can be customised for each world by the user.

# Note that the name of this variable 'atmo_data' itself isn't particularly significant.
atmo_data = \
    {"Name": "Atmosphere",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
         {"0": {"Label": "Vacuum",
                "Description": "No significant atmosphere. " +\
                "Requires a space suit.",
                "Surface Pressure": [0.0, 0.1]},
          "1": {"Label": "Trace",
                "Description": "Very thin atmosphere but enough " +\
                "to allow for winds, weathering and some precipitation. " +\
                "Requires a protective suit with breathing aparatus.",
                "Surface Pressure": [0.2, 0.5]},
          "2": {"Label": "Thin", 
                "Description": "Low atmoepheric pressure, but capable of " +\
                "sustaining life adapted to it. A protective suit is not " +\
                "required, but bottled oxygen or an air supply is recommended.",
                "Surface Pressure": [0.6, 0.7]},
          "3": {"Label": "Breathable", 
                "Description": "Comfortably breatheable though bear in mind " +\
                "some high altitude, polluted or hostile regions may still " +\
                "require assistance.",
                "Surface Pressure": [0.8, 1.5]},
          "4": {"Label": "Dense", 
                "Description": "Heavy, high pressure atmosphere that may be " +\
                "difficult to breathe and require filters or an air supply " +\
                "for extended visits.",
                "Surface Pressure": [1.6, 2.5]},
          "5": {"Label": "Hostile", 
                "Description": "Unbreathable and dangerous, requiring a " +\
                "protective suit and air supply. Corrosive or invasive " +\
                "substances may require specialist protective gear.",
                "Surface Pressure": [0.8, 4.0]}
        }
    }


hydro_data = \
    {"Name": "Hydrography",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
     {"0": {"Label": "Parched",
            "Description": "There is no liquid " + \
            "water on the surface and even any ice " + \
            "present is locked up in permafrost " + \
            "layers."},
      "1": {"Label": "Dry",
            "Description": "Very little surface " + \
            "water overall, but with some some small " + \
            "areas where moisture is available."},
      "2": {"Label": "Lakes", 
            "Description": "Mostly dry, with a few " + \
            "scattered lakes or small seas with " + \
            "vestigial river systems. water coverage."},
      "3": {"Label": "Seas", 
            "Description": "Several significant bodies " + \
            "of water and developed river basins."},
      "4": {"Label": "Oceans", 
            "Description": "The planet has extensive " + \
            "deep water oceans and many land masses " + \
            "have extensive river networks. "},
      "5": {"Label": "Water World", 
            "Description": "The planets surface is " + \
            "dominated by a single world ocean, with " + \
            "at most a scattering of small islands. "}
        }
    }

temp_data = \
    {"Name": "Temperature",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
         {"0": {"Label": "Frozen",
                "Description": "The entire planet experiences sub-zero " +\
                "temperatures most of the time. If surface water is present" +\
                "most of it will be ice, perhaps with occasional small " +\
                "areas of open water."},
          "1": {"Label": "Cold",
                "Description": "Much of the planet experiences sub-zero " +\
                "temperatures most of the time, with large ice caps if " +\
                "water is pesent. Equatorial regions have patchy temperate " +\
                "zones."},
          "2": {"Label": "Temperate", 
                "Description": "Large equatorial temperate zones, but " +\
                "saubstantial ice caps. There may be small regions with " +\
                "variant local climates such as desert or tropical patches."},
          "3": {"Label": "Varied", 
                "Description": "The planet has many varied climate zones " +\
                "from cold polar caps, merging into temperate zones at " +\
                "mid latitudes, then desert and tropical regions around " +\
                "the equator."},
          "4": {"Label": "Tropical", 
                "Description": "The planet is dominated by extensive hot " +\
                "zones, with desert regions where precipitation is uncommon."},
          "5": {"Label": "Burning", 
                "Description": "Most of the planet's surface is scorched by " +\
                "searing heat, with only the polar regions providing respite."}
        }
    }

resource_data = \
    {"Name": "Resources",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
         {"0": {"Label": "None",
                "Description": "No practically extractable resources other " +\
                "than common minerals."},
          "1": {"Label": "Poor",
                "Description": "A few scattered deposits of useful " +\
                "minerals, but they are often hard to extract."},
          "2": {"Label": "Sparse", 
                "Description": "Scattered small deposits of useful" +\
                "minerals. Extraction is reasonably easy but they will " +\
                "run out quickly. There may be a few small valuable finds"},
          "3": {"Label": "Moderate", 
                "Description": "Abundant sources of basic minerals. " +\
                "Valuable minerals are rarer and usualy harder to access, " +\
                "but there are some small but spectacular finds out there."},
          "4": {"Label": "Plentiful", 
                "Description": "A variety of rare and valuable minerals " +\
                "are easy to access. Most are moderate in size but " +\
                "there are a few extensive deposits of one or two " +\
                "unusual resources."},
          "5": {"Label": "Rich", 
                "Description": "One of the most valuable known sources " +\
                "of rare, valuable and exotic minerals that is unlikely " +\
                "to be exhausted for generations to come. "}
        }
    }

bio_data = \
    {"Name": "Biosphere",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
         {"0": {"Label": "Barren",
                "Description": "Little or no " + \
                "life. If there are any life forms present they may " + \
                "be residual microorganisms from a dying ecosystem " + \
                "that suffered environmental collapse, or dormant " + \
                "spores and vestigial traces left by off world " + \
                "visitors near their landing sites."},
          "1": {"Label": "Primordial",
                "Description": "Only simple and " + \
                "primitive organisms are present, mainly microorganisms, " + \
                "invertebrates and plant or fungal forms. If advanced " + \
                "animals are present they have almost certainly been " + \
                "introduced from other planets but the ecosystem is not " + \
                "developed enough to support many such species."},
          "2": {"Label": "Primitive", 
                "Description": ": The ecology supports " +\
                "greater diversity, with more sophisticated species higher " + \
                "up the food chain. Some regional ecosystems have become " + \
                "more specialized to their environment, with more complex " + \
                "food chains in order to exploit resources more " + \
                "efficiently, but there is still a tendency for large " + \
                "homogenous regions to be dominated by monocultures of " + \
                "relatively simple species, especially plants."},
          "3": {"Label": "Diverse", 
                "Description": "All major ecological " + \
                "zones now contain highly diverse communities of different " + \
                "species from multiple phylae. Many advanced animal species " + \
                "now exist in multiple regional variants adapted to their " + \
                "habitat and available food types. "},
          "4": {"Label": "Abundant", 
                "Description": "Most of the planet " + \
                "consists of rich, multi-layered ecosystems with " + \
                "sophisticated food chains. There is a high degree of " + \
                "diversity and some species have now evolved through " + \
                "multiple stages such as from aquatic forms to land " + \
                "animals to avian forms, which have then re-adapted to " + \
                "aquatic life."},
          "5": {"Label": "Exotic", 
                "Description": "Unusual local conditions " + \
                "have lead to an extreme biosphere supporting unique " + \
                "organisms and ecological niches or relationships."}
        }
    }


pop_data = \
    {"Name": "Population",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
        {"0": {"Label": "None",
               "Description": "No sustainable habitation."},
         "1": {"Label": "Minimal",
               "Description": "A small but possibly stable population " +\
               "of perhaps hundreds or a few thousand."},
         "2": {"Label": "Low", 
               "Description": "Mostly sparsely populated with perhaps a " +\
               "few dense population centres."},
         "3": {"Label": "Medium", 
               "Description": "Most habitable regions are well populated, " +\
               "with larger local settlements common. The largest cities " +\
               "have populations in the millions."},
         "4": {"Label": "High", 
               "Description": "The majority of the planet is settled, with " +\
               "extensive resource development. Large population centres " +\
               "are common, with numerous cities of tens of millions of " +\
               "inhabitants, while the total population is in the billions."},
         "5": {"Label": "Teeming", 
               "Description": "The planet is at about the limit of it's " +\
               "ability to support it's burgeoning population. Vast cities " +\
               "of tens of millions of inhabitants are common and only the " +\
               "most inhospitable regions are sparsely populated. Total " +\
               "population is in the tens of billions and pollution and " +\
               "waste disposal are significant issues."}
        }
    }


culture_data = \
    {"Name": "Culture",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
        {"0": {"Label": "Unknown",
               "Description": "Either there is no population, or it's" +\
               "attitude to external contact is ambiguous or unknown."},
         "1": {"Label": "Hostile",
               "Description": "The dominant attitude is hostility to " +\
               "any outside contact and visitors are highly likely to " +\
               "be subject to attempted assault or capture."},
         "2": {"Label": "Isolationist", 
               "Description": "The population avoids contact with " +\
               "outsiders and although they are not necesserily " +\
               "hostile, they are likely to resist attempts at " +\
               "contact and may become hostile if provoked. Some " +\
               "limited contact may be allowed under restrictive " +\
               "conditions."},
         "3": {"Label": "Neutral", 
               "Description": "External contact is neither encouraged " +\
               "or discouraged. Outsiders are likely to be treated " +\
               "fairly, but should beware of inadvertently breaking " +\
               "local customs or laws."},
         "4": {"Label": "Friendly", 
               "Description": "The local population encourages counact " +\
               "with outsiders and is particularly welcoming. This " +\
               "positive attitude may even provide special incentives and " +\
               "privileges to visitors."},
         "5": {"Label": "Activist", 
               "Description": "The prevailing attitude to " +\
               "outsiders is generaly positive and outgoing, it is " +\
               "accompanied by an agenda such as political, religious, " +\
               "cultural or commercial activism thaqt can cause " +\
               "complications in external relations. "}
        }
    }

tech_data = \
    {"Name": "Technology",
     "Codes": ["0", "1", "2", "3", "4", "5"],
     "Code Data": \
         {"0": {"Label": "Primitive",
                "Description": "Simple handmade tools and clothing."},
          "1": {"Label": "Artisan",
                "Description": "Specialist artisans produce high quality " +\
                "goods, sometimes in extensive workshops, but there is " +\
                "little automation."},
          "2": {"Label": "Industrial", 
                "Description": "Most production is performed by automated " +\
                "machinery using power sources such as steam. There is " +\
                "extensive co-ordination between raw material extraction, " +\
                "production and distribution. Automation also comes to " +\
                "mass transport systems such as rail, sea and " +\
                "personal vehicles."},
          "3": {"Label": "Spacefaring", 
                "Description": "Air travel and rocketry are advanced enough " +\
                "to enable orbital satelite launches and visits to moons or " +\
                "other planets. "},
          "4": {"Label": "Starfaring", 
                "Description": "FTL drives enable spacecraft to visit other " +\
                "planetary systems."},
          "5": {"Label": "Advanced", 
                "Description": "Post-singularity society."}
         }
    }


# The API between this script and the main application consists of the
# attributeDefinitions list and the generateWorld() function. If these
# are renamed or not implemented correctly the App will break.

# A SEC file is a format used to exchange world data between legacy SF RPG software tools.
# The world co-ordinates in a SEC file cover a hex patch 32 hexes wide and 40 hexes high.
# To support SEC file import, a rules file must define at least 8 attributes,
# with codes defined to cover the range of values present in SEC files. Refer to
# SEC file format documentation for details.
#
# SEC file format import is not yet completely implemented.
supportsSecFileImport = False

# This list is read by the main application to access the world definitions.
attributeDefinitions = [atmo_data,
                        hydro_data,
                        resource_data,
                        temp_data,
                        bio_data,
                        pop_data,
                        culture_data,
                        tech_data]

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
        codes = ["0", "1", "2", "3", "4", "5"]
        
        if number < 0: number = 0
        elif number > 5: number = 5
        
        return codes[number]

    atm = ('0', '1', '2', '2', '3', '3', '3', '4', '4', '5')[zd(10)]
    hyd = ('0', '1', '2', '2', '3', '3', '4', '4', '5')[zd(9)]
    res = ('0', '1', '2', '2', '3', '3', '3', '4', '4', '5')[zd(10)]
    tmp = ('0', '1', '1', '2', '2', '3', '3', '3', '4', '4', '5')[zd(11)]

    # determine biology
    # This shows how you can use attribute values to modify the values
    # of subsequently generated attributes.
    if atm == '0':
        bio = '0'
    else:
        roll = d6() - 1
        mod = 0
        if atm == '1': mod += -2
        elif atm == '2': mod += 0
        elif atm == '3': mod += 2
        elif atm == '4': mod += 1
        elif atm == '5': mod += -1
        if hyd in ['0', '1']:
            mod -= 1
        if hyd in ['3', '4']:
            mod += 1
        if res == '0': mod += -2
        if res == '1': mod += -1
        if res in ['4', '5']: mod += 1
        if tmp in ['0', '5']: mod += -1

        bio = numberToCode(roll + mod)

    pop = numberToCode(d6() - 1)
    cult = numberToCode(d6() - 1)
    tech = numberToCode(d6() - 1)
    
    # Building the list of generated stats to return to the application 
    codes = [atm,
             hyd,
             tmp,
             res,
             bio,
             pop,
             cult,
             tech]

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
                    '']
    # Both returned parameters must be lists, NOT tupples
    return (codes, descriptions)


                                 
