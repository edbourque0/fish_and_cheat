import random
players = []
roles = []

def assigner_roles():
    #Assigner tricheur
    tricheur = random.choice(players)
    roles.append((tricheur, 'Tricheur'))
    players.pop(players.index(tricheur))

    #Assigner lecteur
    lecteur = random.choice(players)
    roles.append((lecteur, 'lecteur'))
    players.pop(players.index(lecteur))

    #Assigner joueurs
    for joueur in players:
        roles.append((joueur, 'joueur'))
        players.pop(players.index(joueur))

assigner_roles()

print(roles)
