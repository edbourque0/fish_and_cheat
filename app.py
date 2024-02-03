from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import random
import time
import json

POINTS_FICHIER = 'points.json'

def lire_points():
    """Lire les points des joueurs depuis le fichier JSON."""
    try:
        with open(POINTS_FICHIER, 'r') as fichier:
            return json.load(fichier)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'une_cle_secrete_tres_secure'

joueurs = []  # Liste pour stocker les noms des joueurs inscrits
roles = {}    # Dictionnaire pour stocker les rôles des joueurs
partie_demarree = False
question_actuelle = None  # Stocke la question actuelle et ses détails
points = 0
tricheur_revele = False

def obtenir_question(max_retries=5):
    url = "https://opentdb.com/api.php?amount=1&difficulty=hard&type=multiple"
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]
        else:
            print(f"Tentative {attempt + 1} échouée, statut {response.status_code}. Réessai dans 1 seconde...")
            time.sleep(1)
    return None

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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom_joueur = request.form.get('nom')
        if nom_joueur and nom_joueur not in joueurs:
            joueurs.append(nom_joueur)
            session['nom'] = nom_joueur
        return redirect(url_for('salle_attente'))
    return render_template('index.html')

@app.route('/salle_attente')
def salle_attente():
    if partie_demarree:
        return redirect(url_for('partie'))
    premier_joueur = joueurs[0] if joueurs else None
    return render_template('salle_attente.html', joueurs=joueurs, joueur_session=session.get('nom'), premier_joueur=premier_joueur)

@app.route('/lancer_jeu', methods=['POST'])
def lancer_jeu():
    global partie_demarree, question_actuelle
    if 'nom' in session and joueurs and session['nom'] == joueurs[0]:
        partie_demarree = True
        question_actuelle = obtenir_question()
        if question_actuelle:
            assigner_roles()
            return redirect(url_for('partie'))
        else:
            # Gérer le cas où aucune question n'a pu être récupérée
            partie_demarree = False  # Réinitialiser si la récupération échoue
            return "Erreur lors de la récupération de la question, veuillez réessayer.", 500
    return redirect(url_for('salle_attente'))

@app.route('/partie')
def partie():
    if not partie_demarree or 'nom' not in session:
        return redirect(url_for('salle_attente'))
    nom_joueur = session['nom']
    role_joueur = roles.get(nom_joueur, 'Joueur')
    afficher_reponse = role_joueur in ['Joueur', 'Tricheur']
    return render_template('partie.html', role=role_joueur, question=question_actuelle, afficher_reponse=afficher_reponse, nom_joueur=nom_joueur, roles=roles, tricheur_revele = tricheur_revele)

@app.route('/nouvelle_question', methods=['POST'])
def nouvelle_question():
    global question_actuelle
    question_actuelle = obtenir_question()  # Obtenir une nouvelle question de l'API
    if question_actuelle:
        return redirect(url_for('partie'))
    else:
        # Gérer le cas où aucune question n'a pu être récupérée
        return "Erreur lors de la récupération de la nouvelle question, veuillez réessayer.", 500

@app.route('/verifier_joueur/<joueur>', methods=['POST'])
def verifier_joueur(joueur):
    global points, tricheur_revele
    if tricheur_revele:  # Si le tricheur a déjà été révélé, ne rien faire
        return jsonify({"redirect": url_for('resultat')}), 200
    if roles[joueur] == 'Tricheur':
        tricheur_revele = True
        return jsonify({"redirect": url_for('resultat', tricheur=joueur, points=points)}), 200
    else:
        points += 1
        return jsonify({"result": "non-tricheur", "points": points}), 200


@app.route('/resultat')
def resultat():
    tricheur = request.args.get('tricheur')
    points = request.args.get('points')
    return render_template('resultat.html', tricheur=tricheur, points=points)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2828)
