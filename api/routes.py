from flask_restful import Api
from api import app
from api.resources.User import UserManagementResource, AdminUserManagementResource, LoginResource


# reroute traffic
@app.route('/')
def root_page():
    return('<a href="http://locovotiv.com">Main Site</a>')


# create an api
api = Api(app)

# add user routes
api.add_resource(UserManagementResource, '/UserManagement')
api.add_resource(AdminUserManagementResource, '/AdminUserManagement')
api.add_resource(LoginResource, '/Login')
