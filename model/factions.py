# Copyright 2013 Simon Dominic Hibbs
    #Factions text
    factions = []
    for f in range(random.randint(1, 3) + fact_mod):
        roll = d6() + d6()
        if 3 <= roll:
            factions.append([0, 'Obscure - few have heard of them, no popular support.'])
        elif 4 <= roll <= 5:
            factions.append([1, 'Fringe group - few supporters.'])
        elif 6 <= roll <= 7:
            factions.append([2, 'Minor group - some supportters.'])
        elif 8 <= roll <= 9:
            factions.append([3, 'Notable - Significant support, well known.'])
        elif 10 <= roll <= 11:
            factions.append([4, 'Significant - nearly as powerful as the government.'])
        elif 12 <= roll:
            factions.append([5, 'Overwhelming popular support.'])
    for faction in factions:
        fact_roll = d6() + d6() - 7 + pop_roll
        if fact_roll <= 0 : fact_roll = 0
        elif fact_roll >= 13: fact_roll = 13
        faction.append(numberToCode(fact_roll))
    factions = sorted(factions, key=lambda gov: gov[0])
