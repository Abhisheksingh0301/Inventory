from flask import Flask
from datetime import datetime

from db import close_db, init_db
# Set a secret key (keep this secret in production)
app = Flask(__name__, template_folder='app/templates')
app.secret_key = 'abhishek0301'  # Replace with a strong random string

from app.routes import main
app.register_blueprint(main)

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route('/init-db')
def initialize_database():
    init_db()
    return "Database tables created!"
#app.jinja_env.filters['format_dmy'] = format_dmy


# from app.routes import main
# app.register_blueprint(main)
def format_dmy(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d-%b-%y')
    except Exception:
        return value

app.jinja_env.filters['format_dmy'] = format_dmy

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True, port=5051)