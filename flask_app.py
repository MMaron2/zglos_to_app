from flask import Flask
from extensions import db  # Import SQLAlchemy z extensions.py
from routes import routes  # Import Blueprint z routes.py

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Konfiguracja bazy danych
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Smiglo1222",
    password="z9x8c7v6",
    hostname="Smiglo1222.mysql.eu.pythonanywhere-services.com",
    databasename="Smiglo1222$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicjalizacja SQLAlchemy
db.init_app(app)

# Rejestracja Blueprint
app.register_blueprint(routes)

# Uruchomienie aplikacji
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tworzy tabele w bazie danych, jeśli ich nie ma
    app.run(debug=True)
