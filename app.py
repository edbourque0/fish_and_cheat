from flask import Flask, render_template, request, redirect, url_for, session
import requests
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '293ry827r82u3jd3y4fh29f34ojfi3u4fijwhf3'

joueursAassigner = []
joueursAssignees = []
roles = []  # Stocke le rôle de chaque joueur
question_actuelle = None

def obtenir_question():
    reponse = requests.get("https://opentdb.com/api.php?amount=1&difficulty=hard&type=multiple")
    if reponse.status_code == 200:
        data = reponse.json()
        question = data['results'][0]
        return {
            'question': question['question'],
            'correct_answer': question['correct_answer'],
            'incorrect_answers': question['incorrect_answers']
        }
    else:
        return None

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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom_joueur = request.form.get('nom')
        if nom_joueur and nom_joueur not in joueurs:
            joueurs.append(nom_joueur)
            session['nom'] = nom_joueur
            if len(joueurs) >= 3:  # Un nombre minimal de joueurs pour démarrer le jeu
                assigner_roles()
                return redirect(url_for('salle_attente'))
    return render_template('index.html')

@app.route('/salle_attente')
def salle_attente():
    if 'nom' not in session:
        return redirect(url_for('home'))
    if roles:  # Si les rôles ont été assignés
        return redirect(url_for('partie'))
    return render_template('salle_attente.html', joueurs=joueurs)

@app.route('/partie', methods=['GET', 'POST'])
def partie():
    role = roles.get(session.get('nom'), '')
    if request.method == 'POST' and role == 'lecteur':
        action = request.form.get('action')
        if action == 'changer':
            question_actuelle = obtenir_question()
        elif action == 'envoyer':
            # Lorsque la question est envoyée, elle ne change pas
            pass
    else:
        question_actuelle = obtenir_question() if not question_actuelle else question_actuelle

    return render_template('partie.html', role=role, question=question_actuelle)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2828)
