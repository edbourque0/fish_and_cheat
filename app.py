import random
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '872y3r872h3e872h367r24gr23ge'
socketio = SocketIO(app, logger=True)

joueurs = []  # Liste pour stocker les noms des joueurs inscrits
roles = {}    # Dictionnaire pour stocker les rôles des joueurs
partie_demarree = False #Variable pour savoir si la partie est commencée
question_actuelle = None  # Stocke la question actuelle et ses détails
points = {} #Dictionnaire pour stocker les points des joueurs
retourne = {} #Dictionnaire pour stocker les joueurs retournés lors de la partie
tricheur_revele = False #Variable pour savoir si le tricheur a été révélé
tricheur = '' #Variable pour stocker le nom du tricheur temporairement
round_number = 0 #Nombre de round jouées dans la partie
joueurs_en_attente = []


def obtenir_question(max_retries=5):
    #Va chercher la question sur l'API de opentdb
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]
        time.sleep(1)
    return None


def assigner_roles():
    #Assigne les roles aux joueurs
    global tricheur
    temp_players = joueurs[:]
    tricheur = random.choice(temp_players)
    roles[tricheur] = 'Tricheur'
    temp_players.remove(tricheur)
    lecteur = random.choice(temp_players)
    roles[lecteur] = 'Lecteur'
    temp_players.remove(lecteur)
    for joueur in temp_players:
        roles[joueur] = 'Joueur'


def reset_param():
    #Fonction pour reseter les paramêtres pour pouvoir jouer une nouvelle partie
    global joueurs, roles, partie_demarree, question_actuelle, tricheur, tricheur_revele, round_number
    joueurs = []
    roles = {}
    partie_demarree = False
    question_actuelle = None
    tricheur_revele = False
    tricheur = ''
    init_points()
    round_number = 0
    joueurs_en_attente.clear()

def retourner(role_retourne, joueur_retourne):
    #Fonction pour retourner un joueur
    retourne[joueur_retourne] = role_retourne
    socketio.emit('Joueur retourne', {'joueur': joueur_retourne, 'role': role_retourne})

def init_points():
    #Assigner 0 points à tout les joueurs
    for user in roles:
        points[user] = 0

def assigner_points():
    #Assigner les points de la partie aux joueurs
    for user in roles:
        if roles[user] == 'Lecteur' and len(retourne) == len(joueurs)-2:
            points[user] += len(joueurs)-1
        elif roles[user] == 'Lecteur' and len(retourne) != len(joueurs)-2:
            points[user] += 0
        elif roles[user] == 'Tricheur' and user in retourne.keys() and len(retourne) < len(joueurs)-2:
            points[user] += len(joueurs)-1 - len(retourne)
        elif roles[user] == 'Joueur' and user not in retourne.keys():
            points[user] += len(joueurs)-1 - len(retourne)
        else:
            points[user] += 0
    print(points)

def verifier_nouveau_joueur(nom):
    #Vérifier qu'un nouveau joueur n'est pas ajouté lors d'une partie
    if round_number > 0 and nom not in joueurs:
        return False
    return True

def attendre(nom):
    #Crée une liste des joueurs en attente
    if nom not in joueurs_en_attente:
        joueurs_en_attente.append(nom)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom_joueur = request.form.get('nom')
        if verifier_nouveau_joueur(nom_joueur) is True:
            if nom_joueur and nom_joueur not in joueurs:
                joueurs.append(nom_joueur)
                session['nom'] = nom_joueur
            return redirect(url_for('salle_attente'))
        socketio.emit('Nouvelle partie')
        return render_template('index.html', message=True)
    return render_template('index.html', nbattente=len(joueurs_en_attente), round_number=round_number)

@app.route('/reset', methods=['POST'])
def reset():
    reset_param()
    socketio.emit('Nouvelle partie crée')
    return redirect(url_for('home'))

@app.route('/salle_attente')
def salle_attente():
    global tricheur_revele
    tricheur_revele = False
    socketio.emit('Joueur en attente', joueurs)
    attendre(session['nom'])
    if partie_demarree:
        return redirect(url_for('partie'))
    premier_joueur = joueurs[0] if joueurs else None
    return render_template('salle_attente.html', joueurs=joueurs, joueur_session=session.get('nom'),premier_joueur=premier_joueur, joueurs_en_attente=len(joueurs_en_attente), nbjoueurs=len(joueurs))

@app.route('/lancer_jeu', methods=['POST'])
def lancer_jeu():
    global partie_demarree, question_actuelle
    if 'nom' in session and joueurs and session['nom'] == joueurs[0]:
        question_actuelle = obtenir_question()
        if len(joueurs_en_attente) == len(joueurs):
            if question_actuelle:
                partie_demarree = True
                socketio.emit('Partie commencée')
                assigner_roles()
                return redirect(url_for('partie'))
            partie_demarree = False
            return "Erreur lors de la récupération de la question, veuillez réessayer.", 500
        else:
            return redirect(url_for('salle_attente'))
    return redirect(url_for('salle_attente'))

@app.route('/partie')
def partie():
    joueurs_en_attente.clear()
    if tricheur_revele:
        return redirect(url_for('resultat'))
    nom_joueur = session['nom']
    role_joueur = roles.get(nom_joueur, 'Joueur')
    afficher_reponse = role_joueur in ['Joueur', 'Tricheur']
    return render_template('partie.html', role=role_joueur, question=question_actuelle, afficher_reponse=afficher_reponse, nom_joueur=nom_joueur, roles=roles, tricheur_revele=tricheur_revele, round_number=round_number)

@app.route('/nouvelle_question', methods=['POST'])
def nouvelle_question():
    global question_actuelle
    question_actuelle = obtenir_question()
    if question_actuelle:
        socketio.emit('Nouvelle question')
        return redirect(url_for('partie'))
    else:
        # Gérer le cas où aucune question n'a pu être récupérée
        return "Erreur lors de la récupération de la nouvelle question, veuillez réessayer.", 500

@app.route('/verifier_joueur/<joueur>', methods=['POST'])
def verifier_joueur(joueur):
    global tricheur_revele, round_number, tricheur
    if tricheur_revele:  # Si le tricheur a déjà été révélé, ne rien faire
        return jsonify({"redirect": url_for('resultat')}), 200
    if roles[joueur] == 'Tricheur':
        tricheur_revele = True
        socketio.emit('Tricheur revélé')
        tricheur = joueur
        if round_number == 0:
            init_points()
        round_number += 1
        assigner_points()
        return jsonify({"redirect": url_for('resultat', tricheur=joueur, points=points)}), 200
    else:
        retourner(roles[joueur], joueur)
        return jsonify({"result": "non-tricheur"}), 200

@app.route('/resultat')
def resultat():
    global points, tricheur, partie_demarree
    partie_demarree = False
    return render_template('resultat.html', tricheur=tricheur, points=points)

@socketio.on('connect')
def handle_connect():
    global joueurs_connectes
    print('Nouveau joueur connecté!')
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=2827, allow_unsafe_werkzeug=True)
