from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from models import db, User, Profile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, # nos permite vincular jwt a nuestra aplicacion
    create_access_token, # nos permite crear el token de authentication
    get_jwt_identity, # nos permite obtener el identificador del usuario
    jwt_required # nos permite definir la ruta privada (va a solicitar el token)
)
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = "dialect+driver://user:pass@host:port/database"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dev_4geeks.db"
app.config['JWT_SECRET_KEY'] = '33b9b3de94a42d19f47df7021954eaa8'
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost:3306/dev_4geeks"

db.init_app(app)
Migrate(app, db) # flask db init, flask db migrate, flask db upgrade
jwt = JWTManager(app)

@app.route('/')
def main():
    return jsonify({ "msg": "API REST FLASK"}), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email: return jsonify({ "msg": "Email is required!"}), 400
    if not password: return jsonify({ "msg": "Password is required!"}), 400

    user = User.query.filter_by(email=email).first()

    if not user: return jsonify({ "msg": "email/password are incorrects!"}), 401
    if not check_password_hash(user.password, password): return jsonify({ "msg": "email/password are incorrects!"}), 401

    expires = datetime.timedelta(minutes=1) # creamos la fecha o tiempo de duracion del token
    access_token = create_access_token(identity=user.id, expires_delta=expires) # creamos el token con el tiempo de duracion estipulado

    data = { # variable que contiene toda la informacion que se desea enviar mas el token de acceso
        "access_token": access_token,
        "user": user.serialize()
    }

    return jsonify(data), 200



@app.route('/test', methods=['GET', 'POST', 'PUT', 'DELETE'])
def test():
    if request.method == 'GET':
        return jsonify({ "method": "Usando el metodo GET"}), 200

    if request.method == 'POST':
        return jsonify({ "method": "Usando el metodo POST"}), 200

    if request.method == 'PUT':
        return jsonify({ "method": "Usando el metodo PUT"}), 200

    if request.method == 'DELETE':
        return jsonify({ "method": "Usando el metodo DELETE"}), 200

@app.route('/test-get', methods=['GET'])
def get_test():
    
    return jsonify({"saludo": "Hola estas usando el metodo GET"}), 404

@app.route('/test-post', methods=['POST'])
def post_test():
    pass

@app.route('/search/<desde>/<hasta>/category/<category>', methods=['POST'])
def test_params(desde, hasta, category):

    # body = json.loads(request.data)
    # body = request.get_json()

    #body = request.json.get('name')

    name = request.form.get('name')
    lastname = request.form.get('lastname')

    photo = request.files['photo']

    cv = request.files['cv']

    print(photo.filename)
    print(cv.filename)

    return jsonify({
        "desde": desde,
        "hasta": hasta,
        "category": category,
        "body": {
            "name": name,
            "lastname": lastname
        }
    }), 201

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
#@jwt_required()
def users(id = None):
    if request.method == 'GET':
        if id is not None:
            user = User.query.get(id)
            if not user: return jsonify({ "msg": "User not found!"}), 404
            return jsonify(user.serilize()), 200
        else:
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            print(current_user.name)

            users = User.query.all()
            users = list(map(lambda user: user.serialize(), users))
            return jsonify(users), 200

    if request.method == 'POST':
        #data = request.get_json()
        #data['name']

        name = request.json.get('name') # Asigna None si no existe el atributo
        lastname = request.json.get('lastname')
        email = request.json.get('email')
        password = request.json.get('password')
        bio = request.json.get('bio', "")
        facebook = request.json.get('facebook', "")
        twitter = request.json.get('twitter', "")
        instagram = request.json.get('instagram', "")

        if not name: return jsonify({ "msg": "Name is required!"}), 400
        if not lastname: return jsonify({ "msg": "Lastname is required!"}), 400
        if not email: return jsonify({ "msg": "Email is required!"}), 400
        if not password: return jsonify({ "msg": "Email is required!"}), 400

        user = User() # instancia de User
        user.name = name
        user.lastname = lastname
        user.email = email
        user.password = generate_password_hash(password)

        #db.session.add(user)
        #db.session.commit()

        profile = Profile()
        profile.bio = bio
        profile.facebook = facebook
        profile.twitter = twitter
        profile.instagram = instagram
        #profile.user_id = user.id

        #db.session.add(profile)
        #db.session.commit()

        user.profile = profile
        user.save()

        #db.session.add(user)
        #db.session.commit()


        return jsonify(user.serialize()), 201

    if request.method == 'PUT':
        #data = request.get_json()
        #data['name']

        name = request.json.get('name') # Asigna None si no existe el atributo
        lastname = request.json.get('lastname')
        bio = request.json.get('bio', "")
        facebook = request.json.get('facebook', "")
        twitter = request.json.get('twitter', "")
        instagram = request.json.get('instagram', "")

        if not name: return jsonify({ "msg": "Name is required!"}), 400
        if not lastname: return jsonify({ "msg": "Lastname is required!"}), 400

        user = User.query.get(id) # instancia de User

        if not user: return jsonify({ "msg": "User not found!"}), 404

        user.name = name
        user.lastname = lastname

        """
        profile = Profile.query.filter_by(user_id=id).first()

        profile.bio = bio
        profile.facebook = facebook
        profile.twitter = twitter
        profile.instagram = instagram

        user.profile = profile
        user.update()
        """

        user.profile.bio = bio
        user.profile.facebook = facebook
        user.profile.twitter = twitter
        user.profile.instagram = instagram
        user.update()

        return jsonify(user.serialize()), 200


@app.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    return jsonify(current_user.serialize()), 200

"""
@app.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    if request.method == 'GET':
       return "Estas buscando al usuario: " + str(id)
"""





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3452)