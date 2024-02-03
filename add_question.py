from app import db, Question

# Exemple d'ajout de question
question1 = Question(question="Quelle est la capitale de la France ?", reponse="Paris")
db.session.add(question1)

question1 = Question(question="Qui a ", reponse="Paris")
db.session.add(question1)

question1 = Question(question="Quelle est la capitale de la France ?", reponse="Paris")
db.session.add(question1)

question1 = Question(question="Quelle est la capitale de la France ?", reponse="Paris")
db.session.add(question1)

question1 = Question(question="Quelle est la capitale de la France ?", reponse="Paris")
db.session.add(question1)

# Ajoute d'autres questions de la même manière...

# Commit les changements dans la base de données
db.session.commit()
