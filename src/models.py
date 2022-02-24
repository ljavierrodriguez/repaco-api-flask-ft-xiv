from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "profile": self.profile.serialize()
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text(), default="")
    facebook = db.Column(db.Text(), default="")
    twitter = db.Column(db.Text(), default="")
    instagram = db.Column(db.Text(), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #user = db.relationship('User', uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "bio": self.bio,
            "facebook": self.facebook,
            "name": self.user.name
        }