import random
players = ['Edouard', 'Catherine', 'William', 'Alexandre', 'Anthony', 'Isaac', 'Guillaume', 'René-Charles']
roles = []

def assigner_roles():
    #Assigner tricheur
    tricheur = random.choice(players)
    newplayers.append((tricheur, 'Tricheur'))
    players.pop(players.index(tricheur))

    #Assigner lecteur
    lecteur = random.choice(players)
    newplayers.append((lecteur, 'lecteur'))
    players.pop(players.index(lecteur))

    #Assigner joueurs
    for joueur in players:
        newplayers.append((joueur, 'joueur'))
        players.pop(players.index(joueur))

assigner_roles()

