from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    password = db.Column(db.String)

    def to_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password
        }
