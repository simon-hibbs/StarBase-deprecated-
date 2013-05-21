# -*- coding: cp1252 -*-
# The entirety if this file is designated as Open Content.
# Refer to the file OGL_License.txt for details

starport_data = \
     {"Name": "Starport",
     "Codes": ['A', 'B', 'C', 'D', 'E', 'X'],
     "Code Data": \
         {"A": {"Label": "Starport",
                "Description": "A full starport with many landing and docking sites. " +\
                "Includes a shipyard capable of building and overhauling any kind of spacecraft, " +\
                "including ships with interstellar capability."},
          "B": {"Label": "Spaceport",
                "Description": "Comprehensive landing and docking facilities. " +\
                "Includes a shipyard capable of constructing and overhauling in-sytem spacecraft. " +\
                ""},
          "C": {"Label": "Small Spaceport",
                "Description": "Comprehensive landing and docking facilities, " +\
                "suitable for routine operations. No shipyard and only basic maintenance " +\
                "facilities are available."},
          "D": {"Label": "Basic Facility",
                "Description": "Only basic landing and service facilities are available." +\
                ""},
          "E": {"Label": "Landing Pad",
                "Description": "Basic landing area and shelter only." +\
                ""},
          "X": {"Label": "None",
                "Description": "No facilities for landing spacecraft are available." +\
                ""}
          }
      }


size_data = \
     {"Name": "Size",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A"],
     "Code Data": \
         {"0": {"Label": "800km",
                "Description": "Small planetoid with a diameter of 800km " +\
                "and negligible surface gravity."},
          "1": {"Label": "1,600km",
                "Description": "A planetoid with a diameter of 1,600km " +\
                "and surface gravity of 0.05G."},
          "2": {"Label": "3,200km",
                "Description": "Similarly sized to Luna, with a diameter of " +\
                "3,200km and surface gravity of 0.15G."},
          "3": {"Label": "4,800km",
                "Description": "A small planet, " +\
                "roughly the same size as Mars with a diameter of " +\
                "4,800km and surface gravity of 0.25G."},
          "4": {"Label": "6,400km",
                "Description": "A small Planet with a diameter of " +\
                "6,400km and surface gravity of 0.35G"},
          "5": {"Label": "8,000km",
                "Description": "A small planet with a diameter of " +\
                "8,000km and surface gravity of 0.45G"},
          "6": {"Label": "9,600km",
                "Description": "A small planet with a diameter of " +\
                "9,600km and surface gravity of 0.75G"},
          "7": {"Label": "11,200km",
                "Description": "A medium sized planet, slightly smaller " +\
                "than Earth, with a diameter of " +\
                "11,200km and surface gravity of 0.9G"},
          "8": {"Label": "12,800km",
                "Description": "A planet roughly the same size as Earth, " +\
                "with a diameter of 12,800km and surface gravity of 1.0G"},
          "9": {"Label": "14,400km",
                "Description": "A large high gravity planet with a diameter " +\
                "of 14,400km and surface gravity of 1.25G."},
          "A": {"Label": "16,000km",
                "Description": "A very large high gravity planet." +\
                "with a diameter of 16,000km and surface gravity of 1.4G"},
          }
      }


atmosphere_data = \
    {"Name": "Atmosphere",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"],
     "Code Data": \
         {"0": {"Label": "Vacuum",
                "Description": "No significant atmosphere. " +\
                "Requires a space suit."},
          "1": {"Label": "Trace",
                "Description": "Some traces of atmospheric gasses. " +\
                "Surface pressure is from 0.001 to 0.09 atm. "+\
                "Requires a space suit."},
          "2": {"Label": "Very Thin, Tainted", 
                "Description": "Very low atmospheric pressure of from " +\
                "0.1 to 0.42 atm. Requires the " +\
                "use of a respirator and an atmospheric filter due to " +\
                "the presence of a harmful taint."},
          "3": {"Label": "Very Thin", 
                "Description": "Very low atmospheric pressure of from " +\
                "0.1 to 0.42 atm."},
          "4": {"Label": "Thin, Tainted", 
                "Description": "Low pressure atmosphere with a surface pressure " +\
                "from 0.43 to 0.7 atm. The presence of a taint requires the use of " +\
                "a filter mask."},
          "5": {"Label": "Thin", 
                "Description": "Low pressure but breatheable atmosphere with a surface " +\
                "pressure from 0.43 to 0.7 atm."},
          "6": {"Label": "Standard",
                "Description": "Standard breatheable atmosphere with a surface pressure " +\
                "from 0.71 to 1.49 atm."},
          "7": {"Label": "Standard, Tainted",
                "Description": "Standard atmosphere with a surface pressure " +\
                "from 0.71 to 1.49 atm. the presence of a taint requires the use of a filter."},
          "8": {"Label": "Dense",
                "Description": "Breathable atmosphere with a surface pressure " +\
                "from 1.5 to 2.49 atm."},
          "9": {"Label": "Dense, Tainted",
                "Description": "A dense, tainted atmosphere with surface pressure from " +\
                "1.5 to 2.49 atm. Requires the use of a filter."},
          "A": {"Label": "Exotic",
                "Description": "An exotic atmosphere, requiring the use of a filter. "},
          "B": {"Label": "Corrosive",
                "Description": "A dangerously corrosive atmosphere. " +\
                "Requires a space suit."},
          "C": {"Label": "Insidious",
                "Description": "A highly reactive insidious atmosphere. " +\
                "Requires a space suit."},
          "D": {"Label": "Dense, High",
                "Description": "A thick N2/O2 atmospheres, but the mean surface pressure " +\
                "is too high to support unprotected human life (high pressure nitrogen " +\
                "and oxygen are deadly to humans). However, pressure naturally decreases " +\
                "with increasing altitude, so if there are highlands at the right " +\
                "altitude the pressure may drop enough to support human life. " +\
                "Alternatively, there may not be any topography high enough for humans " +\
                "to inhabit, necessitating floating gravitic or dirigible habitats or " +\
                " sealed habitats on the surface."},
          "E": {"Label": "Thin, Low",
                "Description": "A massive world have thin N2/O2 atmospheres that settles " +\
                "in the lowlands and depressions and are only breathable there – " +\
                "the pressure drops off so rapidly with altitude that the highest " +\
                "topographic points of the surface may be close to vacuum."},
          "F": {"Label": "Unusual",
                "Description": "A highly unusual atmosphere."},
        }
    }


hydrographic_data = \
    {"Name": "Hydrographics",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A"],
     "Code Data": \
         {"0": {"Label": "Desert world",
                "Description": "No significant water bodies. " +\
                "No more than 5% water coverage."},
          "1": {"Label": "Dry world",
                "Description": "Some small water bodies. " +\
                "Hydrographic percentage 6%-15%. "},
          "2": {"Label": "Small Seas",
                "Description": "Some small seas. " +\
                "Hydrographic percentage 16%-25%. "},
          "3": {"Label": "Small Seas/Oceans",
                "Description": "Some small seas and oceans. " +\
                "Hydrographic percentage 26%-35%." },
          "4": {"Label": "Wet world",
                "Description": "Wet world with seas and some oceans. " +\
                "Hydrographic percentage 36%-45%." },
          "5": {"Label": "Large Oceans",
                "Description": "Wet world with several large oceans. " +\
                "Hydrographic percentage 46%-55%." },
          "6": {"Label": "Large Oceans",
                "Description": "Wet world with several large oceans. " +\
                "Hydrographic percentage 56%-65%." },
          "7": {"Label": "Earth-like",
                "Description": "An earth-like world with many seas and large oceans. " +\
                "Hydrographic percentage 66%-75%." },
          "8": {"Label": "Water world",
                "Description": "The world's surface is mainly water with " +\
                "some small land masses. " +\
                "Hydrographic percentage 76%-85%." },
          "9": {"Label": "Few Islands",
                "Description": "Mainly water covered with only a few small " +\
                "islands and archipelagos. " +\
                "Hydrographic percentage 86%-95%." },
          "A": {"Label": "Almost entirely water",
                "Description": "A water world with no significant land formations. " +\
                "Hydrographic percentage 69%-100%." },
          }
     }



population_data = \
    {"Name": "Population",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C"],
     "Code Data": \
         {"0": {"Label": "None",
                "Description": "No permanent population. " +\
                "Population in the range 1+."},
          "1": {"Label": "Few",
                "Description": "A tiny farmstead or single family. " +\
                "Population in the range 1+."},
          "2": {"Label": "Hundreds",
                "Description": "A small village. " +\
                "Population in the range 100+."},
          "3": {"Label": "Thousands",
                "Description": "Large village, or scattered small settlements. " +\
                "Population in the range 1,000+."},
          "4": {"Label": "Tens of thousands",
                "Description": "Small town. " +\
                "Population in the range 10,000+."},
          "5": {"Label": "Hundreds of thousands",
                "Description": "Average city. " +\
                "Population in the range 100,000+."},
          "6": {"Label": "Millions",
                "Description": "Several cities. " +\
                "Population in the range 1,000,000+."},
          "7": {"Label": "Tens of millions",
                "Description": "Large city. " +\
                "Population in the range 10,000,000+."},
          "8": {"Label": "Hundreds of millions",
                "Description": "Several large cities. " +\
                "Population in the range 100,000,000+."},
          "9": {"Label": "Billions",
                "Description": "Similar population to early 21st century earth. " +\
                "Population in the range 1,000,000,000+."},
          "A": {"Label": "Tens of billions",
                "Description": "Densely populated world. " +\
                "Population in the range 10,000,000,000+."},
          "B": {"Label": "Hundreds of billions",
                "Description": "Incredibly crowded world. " +\
                "Population in the range 100,000,000,000+."},
          "C": {"Label": "Trillions",
                "Description": "World-city. " +\
                "Population in the range 1,000,000,000,000+."},
          }
     }


# Note that government types in the SRD top out at "D"
# so any result higher than that is treated as "D", hence the duplication
government_data = \
    {"Name": "Government",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "D", "D"],
     "Code Data": \
         {"0": {"Label": "None",
                'Description' : 'No persistent organised government. ' +
                'Any co-ordinated activity is on an ad-hoc basis, ' +
                'often based on personal or family bonds.'},
          "1": {"Label": "Company/corporation",
                'Description' : 'Most developed territory and infrastructure ' +
                'is the property of a single company, corporation or conglomerate, ' +
                'with governmental functions carried out by professional managers.'},
          "2": {"Label": "Participating democracy",
                'Description' : 'Most important decisions are voted for by ' +
                'the citizenry, who also directly appoint officials for limited terms.'},
          "3": {"Label": "Self-perpetuating oligarchy",
                'Description' : 'Rule by a restricted, usualy hereditary group ' +
                'with little or no influence by the majority of the population.'},
          "4": {"Label": "Representative democracy",
                'Description' : 'Rule is by representatives ' +
                'that are elected by the citizenry, usualy for limited terms of office.'},
          "5": {"Label": "Feudal technocracy",
                'Description' : 'Rule by a technical elite that performs essential ' +
                'technological functions in return for defined obligations or services'},
          "6": {"Label": "Captive government",
                'Description' : 'Governmental administration by leaders imposed  ' +
                'by an external authority such as a colonial power ' +
                'or military proconsul.'},
          "7": {"Label": "Balkanisation",
                'Description' : 'Rule by multiple rival governments with different ' +
                'territories or spheres of influence. The law level is that most commonly ' +
                'encountered by visitors.'},
          "8": {"Label": "Civil Service Bureaucracy",
                'Description' : 'Rule by governmental, bureaucratic organisations ' +
                'which recruit from the general citizenry whom they notionaly serve.'},
          "9": {"Label": "Impersonal Bureaucracy",
                'Description' : 'Rule by governmental, bureaucratic organisations ' +
                'with little or no reference to the concerns of ordinary citizens.'},
          "A": {"Label": "Charismatic Dictatorship",
                'Description' : 'Rule by a single leader whos authority is based on ' +
                'personal popularity with the citizenry.'},
          "B": {"Label": "Non-Charismatic Leader",
                'Description' : 'Rule by a single authoritarian leader ' +
                'who exercises personal power. This may be the result of ' +
                'a deputy taking power following the rule of a charismatic dictator.'},
          "C": {"Label": "Charismatic Oligarchy",
                'Description' : 'Rule by an organisation or group that enjoys ' +
                'the broad support and confidence of the citizenry.'},
          "D": {"Label": "Religious dictatorship",
                'Description' : 'Rule by a religious organisation such as a ' +
                'church, cult or oracle'}
          }
     }

law_9_plus =    {"Label": "Harsh",
                'Description' : 'Weapons: Any weapons.\n' +
                'Drugs: All drugs.\n' +
                'Information: Any data from offworld. ' +
                'No free press.\n' +
                'Technology: TL 3 items.\n' +
                'Travellers: No offworlders permitted.\n' +
                'Psionics: All psionics.'}

law_level_data = \
    {"Name": "Law Level",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F",
               "G", "H", "I", "J", "K"],
     "Code Data": \
         {"0": {"Label": "None",
                'Description' : 'No restrictions. '},

          "1": {"Label": "Permissive",
                'Description' : 'Weapons: Poison gas, explosives, ' + \
                'undetectable weapons, WMD.\n' + \
                'Drugs: Highly addictive and dangerous ' + \
                'narcotics.\n' + \
                'Information: Intellect programs.\n' + \
                'Technology: Dangerous technologies such as ' + \
                'nanotechnology.\n' + \
                'Travellers: Visitors must contact planetary ' + \
                'authorities by radio, landing is permited ' + \
                'anywhere.\n' + \
                'Psionics: Dangerous talents must be registered.'},
          "2": {"Label": "Few restrictions",
                'Description' : 'Weapons: Portable energy weapons (except ' +
                'ship-mounted weapons).\n' + 
                'Drugs: Highly addictive narcotics.\n' +
                'Information: Agent programs.\n' +
                'Technology: Alien technology.\n' +
                'Travellers: Visitors must report passenger ' +
                'manifests, landing is permitted anywhere.\n' +
                'Psionics: All psionic powers must be ' +
                'registered; use of dangerous powers forbidden.'},
          "3": {"Label": "Some restrictions",
                'Description' : 'Weapons: Heavy weapons.\n' +
                'Drugs: Combat drugs.\n' +
                'Information: Intrusion programs.\n' +
                'Technology: TL 15 items.\n' +
                'Travellers: Landing only at starports or ' +
                'other authorized sites.\n' +
                'Psionics: Use of telepathy restricted to ' +
                'government-approved telepaths.'},
          "4": {"Label": "Some restrictions",
                'Description' : 'Weapons: Light assault weapons ' +
                'and submachine guns.\n' +
                'Drugs: Addictive narcotics.\n' +
                'Information: Security programs.\n' +
                'Technology: TL 13 items.\n' +
                'Travellers: Landing only at starport.\n' +
                'Psionics: Use of teleportation and ' +
                'clairvoyance restricted.'},
          "5": {"Label": "Intermediate",
                'Description' : 'Weapons: Personal concealable ' +
                'weapons.\n' +
                'Drugs: Anagathics.\n' +
                'Information: Expert programs.\n' +
                'Technology: TL 11 items.\n' +
                'Travellers: Citizens must register offworld ' +
                'travel, visitors must register all business.\n' +
                'Psionics: Use of all psionic powers restricted ' +
                'to government psionicists.'},
          "6": {"Label": "Restrictive",
                'Description' : '' +
                'Weapons: All firearms except shotguns and ' +
                'stunners; carrying weapons discouraged.\n' +
                'Drugs: Fast and Slow drugs.\n' +
                'Information: Recent news from offworld.\n' +
                'Technology: TL 9 items.\n' +
                'Travellers: Visits discouraged; excessive ' +
                'contact with citizens forbidden.\n' +
                'Psionics: Possession of psionic drugs banned.'},
          "7": {"Label": "Controlling",
                'Description' : 'Weapons: Shotguns.\n' +
                'Drugs: All narcotics.\n' +
                'Information: Library programs, unfiltered data ' +
                'about other worlds. Free speech curtailed.\n' +
                'Technology: TL 7 items.\n' +
                'Travellers: Citizens may not leave planet; ' +
                'visitors may not leave starport.\n' +
                'Psionics: Use of psionics forbidden.'},
          "8": {"Label": "Repressive",
                'Description' : '' +
                'Weapons: All bladed weapons, stunners.\n' +
                'Drugs: Medicinal drugs.\n' +
                'Information: Information technology, ' +
                'any non-critical data from offworld personal ' +
                'media.\n' +
                'Technology: TL 5 items.\n' +
                'Travellers: Landing permitted only to ' +
                'imperial agents.\n' +
                'Psionics: Psionic-related technology banned.'},
          "9": law_9_plus,
          "A": law_9_plus,
          "B": law_9_plus,
          "C": law_9_plus,
          "D": law_9_plus,
          "E": law_9_plus,
          "F": law_9_plus,
          "G": law_9_plus,
          "H": law_9_plus,
          "I": law_9_plus,
          "J": law_9_plus,
          "K": law_9_plus,
          }
     }



tech_level_data = \
     {"Name": "Tech Level",
     "Codes": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F",
               "G", "H", "I", "J", "K", "L", "M", "N"],
     "Code Data": \
         {"0": {"Label": "None",
                'Description' : 'No technnology. TL 0 species ' +
                'have only discovered the simplest tools and ' +
                "principles, and are on a par with Earth's " +
                'stone age'},
          "1": {"Label": "Bronze/Iron Age",
                'Description' : 'Bronze or Iron Age. Most ' +
                'science is supersition, but they can ' +
                'manufacture weapons and work metal.'},
          "2": {"Label": "Renaisance",
                'Description' : 'Renaisance technology. Some ' +
                'understanding of chemistry, physics, biology ' +
                'and astronomy as well as the scientific method'},
          "3": {"Label": "Early Industrial",
                'Description' : 'Beginnings of the industrial ' +
                'revolution and steam power. Primitive firearms ' +
                'now dominate the battlefield.'},
          "4": {"Label": "Mid Industrial",
                'Description' : 'Industrialisation is complete ' +
                'bringing plastics, radio, etc.'},
          "5": {"Label": "Late Industrial",
                'Description' : 'Widespread electrification, ' +
                'telecommunications and internal combustion. ' +
                'Atomics and primitive computing are appearing.'},
          "6": {"Label": "Atomic",
                'Description' : 'Fission power and computing have been developed. ' +
                'Early space age.'},
          "7": {"Label": "Early Pre-Stellar",
                'Description' : 'Can reach orbit reliably and ' +
                'has telecommunications satelites. Computers ' +
                'become common.'},
          "8": {"Label": "Mid Pre-Stellar",
                'Description' : 'It is possible to reach other ' +
                'worlds in the solar system. Permanent ' +
                'space habitats become possible. Fusion power ' +
                'becomes commercialy viable.'},
          "9": {"Label": "Late Pre-Stellar",
                'Description' : 'Capable of Gravity manipulation. ' +
                'Experimental jump drives.'},
          "A": {"Label": "Early Stellar(A)",
                'Description' : 'Orbital habitats and factories ' +
                'are common. Capable of regular interstellar ' +
                'trade.'},
          "B": {"Label": "Early Stellar(B)",
                'Description' : 'True AI. Grav-supported ' +
                'structures. Jump-2. '},
          "C": {"Label": "Average Stellar(C)",
                'Description' : 'Weather control. man-portable ' +
                'plasma guns, mounted fusion guns. Jump-3.'},
          "D": {"Label": "Average Stellar(D)",
                'Description' : 'Battle dress, Cloning of ' +
                'body parts. Advanced hull design & thruster ' +
                'plates. Jump-4.'},
          "E": {"Label": "Average Stellar(E)",
                'Description' : 'Man-portable fusion weapons. ' +
                'Flying cities. Jump-5.'},
          "F": {"Label": "High Stellar(F)",
                'Description' : 'Black globe generators. ' +
                'Anagathics. Jump-6.'}, 
          "G": {"Label": "Advanced(G)",
                'Description' : 'Advanced technology.'}, 
          "H": {"Label": "Super-advanced(H)",
                'Description' : 'Super-advanced technology.'},
          "I": {"Label": "Sublime",
                'Description' : 'Sublime technology.'},
          "J": {"Label": "Sublime",
                'Description' : 'Sublime technology.'},
          "K": {"Label": "Sublime",
                'Description' : 'Sublime technology.'},
          "L": {"Label": "Sublime",
                'Description' : 'Sublime technology.'},
          "M": {"Label": "Sublime",
                'Description' : 'Sublime technology.'},
          "N": {"Label": "Sublime",
                'Description' : 'Sublime technology.'}
          }
      }


system_data = \
     {"Name": "System Data",
     "Codes": ["0"],
     "Code Data": \
         {"0": {"Label": "---",
                'Description' : ' '}
          }
      }





