from flask import Flask

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

if __name__ == "__main__":
    app.run(debug=True)

