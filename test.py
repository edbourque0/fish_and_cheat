def chooseliar(playernames):
    chosenliar = random.randint(0, len(playernames)-1)
    liar = playernames[chosenliar]
    return liar

print(chooseliar(['Edouard', 'Catherine', 'William', 'Alexandre']))
