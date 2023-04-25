from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<MenuItem {self.name}>'

@app.route('/', methods=['GET', 'POST'])
def index():
    menu_items = MenuItem.query.all()
    return render_template('index.html', menu_items=menu_items)

@app.route('/submit', methods=['POST'])
def submit_menu_item():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image = request.files.get('image')

    if not name or not description or not price:
        flash('Visi lauki ir obligāti!', 'error')
        return redirect(url_for('index'))

    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    else:
        image_filename = None

    new_item = MenuItem(name=name, description=description, price=price, image=image_filename)

    try:
        db.session.add(new_item)
        db.session.commit()
        flash('Jauns ēdiens veiksmīgi pievienots!', 'success')
    except Exception as e:
        flash(f'Kļūda pievienojot ēdienu: {e}', 'error')

    return redirect(url_for('index'))



@app.route('/update/<int:item_id>', methods=['POST'])
def update_menu_item(item_id):
    menu_item = MenuItem.query.get(item_id)

    if menu_item is None:
        flash('Ēdiens nav atrasts!', 'error')
        return redirect(url_for('index'))

    menu_item.name = request.form['name']
    menu_item.description = request.form['description']
    menu_item.price = request.form['price']
    image = request.files.get('image')

    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        menu_item.image = image_filename

    db.session.commit()

    flash('Ēdiens ir veiksmīgi atjaunināts!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)