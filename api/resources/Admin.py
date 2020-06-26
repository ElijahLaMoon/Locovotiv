from flask_restful import Resource
from api.resources import load_json, TOKEN_MINUTES
from api.models import db, User, validate_admin
from api import app
from datetime import datetime as dt, timedelta
import jwt


# create a class for admins to get all the user data
class AdminUserManagementResource(Resource):
    # create a post method to get all the users
    def post(self):
        # get the admin_data and authenticate the admin
        data = load_json()

        # validate the admin
        privileges = jwt.decode(data['token'], app.config.get('SECRET_KEY'))

        if not (privileges['admin_access'] is True):
            return {'message': 'You are not allowed to access this resource.'}, 403

        # get the data from all the users
        users = [{'email': user.email} for user in User.query.all()]

        return {'users': users}, 201

    # create a method to delete users from the admin page (without a password)
    def delete(self):
        data = load_json()

        # validate the admin
        privileges = jwt.decode(data['token'], app.config.get('SECRET_KEY'))

        if not (privileges['admin_access'] is True):
            return {'message': 'You are not allowed to access this resource.'}, 403

        # find the user to delete via email
        user_email = data['user_email']
        user = User.query.filter_by(email=user_email).first()

        # if no user, return so
        if not user:
            return {'message': f"no account associated with {user_email}"}, 404

        # else delete the user
        db.session.delete(user)
        db.session.commit()

        return {'status': 'success', 'message': f"Deleted {user_email}"}, 201


# create a class to log in admins
class AdminLoginResource(Resource):
    def post(self):
        data = load_json()

        # validate the admin
        if not validate_admin(data['email'], data['password']):
            return {'message': 'You are not allowed to access this resource.'}, 403

        # get a token and give it to the admin
        token = jwt.encode({'admin_access': True, 'exp': dt.utcnow() + timedelta(minutes=TOKEN_MINUTES)}, app.config['SECRET_KEY']).decode('UTF-8')

        return {'status': 'success', 'token': token}
