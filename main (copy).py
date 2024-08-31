from flask import Flask, render_template, request, redirect, url_for
from replit import db

app = Flask(__name__)

# Page d'accueil
@app.route('/')
def index():
    loverooms = db.get("loverooms", [])
    return render_template('index.html', loverooms=loverooms)

# Page pour ajouter une nouvelle loveroom
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']

        loveroom_id = len(db.get("loverooms", [])) + 1
        new_loveroom = {
            "id": loveroom_id,
            "name": name,
            "description": description,
            "price": price,
            "location": location
        }

        loverooms = db.get("loverooms", [])
        loverooms.append(new_loveroom)
        db["loverooms"] = loverooms

        return redirect(url_for('index'))

    return render_template('add.html')

# Page pour voir les détails d'une loveroom
@app.route('/loveroom/<int:id>')
def loveroom_detail(id):
    loverooms = db.get("loverooms", [])
    loveroom = next((room for room in loverooms if room["id"] == id), None)
    return render_template('loveroom_detail.html', loveroom=loveroom)

# Démarrer l'application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)