from flask import Flask

app = Flask(__name__)
app.secret_key = 'koech'

from users.views import users
from entries.views import apps
from routes import main
#from users.views import Users

import jwt



app.register_blueprint(users, prefix='api/v2/users')
app.register_blueprint(apps, prefix='api/v2/entries')
app.register_blueprint(main, prefix='api/v2')

