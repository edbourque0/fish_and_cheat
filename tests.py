import random

points = {}
retourne = {}
roles = {}
joueurs = ['Edouard', 'Maxime', 'Simon', 'Julien', 'Catherine', 'Martin']

def retourner(role_retourne, joueur_retourne):
    global retourne
    retourne[joueur_retourne] = role_retourne

def assigner_roles():
    global roles
    temp_players = joueurs[:]
    tricheur = random.choice(temp_players)
    roles[tricheur] = 'Tricheur'
    temp_players.remove(tricheur)

    lecteur = random.choice(temp_players)
    roles[lecteur] = 'Lecteur'
    temp_players.remove(lecteur)

    for joueur in temp_players:
        roles[joueur] = 'Joueur'

def assigner_points():
    global retourne, points, joueurs
    for user in roles:
        if roles[user] == 'Lecteur' and len(retourne) == len(joueurs)-2:
            points[user] = len(joueurs)-1
        elif roles[user] == 'Lecteur' and len(retourne) != len(joueurs)-2:
            points[user] = 0
        elif roles[user] == 'Tricheur' and user in retourne.keys() and len(retourne) < len(joueurs)-2:
            points[user] = len(joueurs)-1 - len(retourne)
        elif roles[user] == 'Joueur' and user not in retourne.keys():
            points[user] = len(joueurs)-1 - len(retourne)

assigner_roles()
retourner('Joueur', 'Julien')
retourner('Joueur', 'Martin')
retourner('Tricheur', 'Edouard')
assigner_points()
print(roles)
print(points)
