from api import db
from api import bcrypt
from api.admin_config import ADMIN_PROFILE


# create a user model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    # create a state
    state = db.Column(db.String(50), default=None, nullable=True)

    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


# create a function to validate users
def validate_user(email, password):
    # get the user
    user = User.query.filter_by(email=email).first()

    if not user:
        return False, {'message': f"no account associated with {email}"}, 404

    # check if passwords match
    if not bcrypt.check_password_hash(user.password, password):
        return False, {'message': f"incorrect password for {email}"}, 401

    return True, user, 201


def validate_admin(email, password):
    print(ADMIN_PROFILE['email'] + ' ' + ADMIN_PROFILE['password'])
    if email != ADMIN_PROFILE['email']:
        return False
    elif password != ADMIN_PROFILE['password']:
        return False
    else:
        return True
