from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = '873h2h383283hurun2dy337489374628he'
socketio = SocketIO(app)

joueurs = []

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('join', namespace='/chat')
def on_join(data):
    nom_joueur = data['nom']
    if nom_joueur not in joueurs:
        joueurs.append(nom_joueur)
        emit('update_joueurs', {'joueurs': joueurs}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
