from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from extensions import db  # Import SQLAlchemy
from sqlalchemy import func

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Model użytkownika
class Uzytkownicy(db.Model):
    __tablename__ = 'Uzytkownicy'
    ID_Uzytkownika = db.Column(db.Integer, primary_key=True)
    Nazwa_Uzytkownika = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Haslo = db.Column(db.String(255), nullable=False)
    Rola = db.Column(db.String(50), nullable=True)
    Data_Rejestracji = db.Column(db.Date, nullable=False, default=datetime.now().date)
    ID_Nagrody = db.Column(db.Integer, nullable=True)

class Nagrody(db.Model):
    __tablename__ = 'Nagrody'
    ID_Nagrody = db.Column(db.Integer, primary_key=True, nullable=False)
    Kryteria = db.Column(db.String(200), nullable=True)
    Typ_Nagrody = db.Column(db.String(100), nullable=True)

class Zgloszenia(db.Model):
    __tablename__ = 'Zgloszenia'  # Nazwa tabeli w bazie danych
    ID_Zgloszenia = db.Column(db.Integer, primary_key=True)  # Klucz główny
    Typ_Zgloszenia = db.Column(db.String(50), nullable=False)  # Typ zgłoszenia
    Opis = db.Column(db.Text, nullable=True)  # Opis zgłoszenia
    Lokalizacja_GPS = db.Column(db.String(50), nullable=True)  # Lokalizacja GPS
    Data_Czas_Zgloszenia = db.Column(db.DateTime, nullable=True)  # Data i czas zgłoszenia
    Status = db.Column(db.String(20), nullable=True)  # Status zgłoszenia
    ID_Uzytkownika = db.Column(db.Integer, db.ForeignKey('Uzytkownicy.ID_Uzytkownika'), nullable=True)  # Klucz obcy
    zdjecie_url = db.Column(db.String(2083), nullable=True)

# Strona startowa
def load_start_page():
    return render_template('login.html')

# przekierowanie na strone logowania
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        # Sprawdzenie użytkownika w bazie danych
        user = Uzytkownicy.query.filter_by(Email=email).first()

        if user and user.Haslo == password:  # Prosta weryfikacja hasła
            # Zapisanie danych w sesji
            session['user_id'] = user.ID_Uzytkownika
            session['user_name'] = user.Nazwa_Uzytkownika
            session['user_role'] = user.Rola
            session['lat'] = 0
            session['lng'] = 0

            if  session['user_role']=='user':
                 flash("Zalogowano pomyślnie!", "success")
                 return redirect(url_for('routes.dashboard')) #jak macie url_for i zmieniacie endpoint to zawsze przed nazwą endpointu dodajecie "routes.przykładowy_endpoint"
            if   session['user_role']=='admin' or session['user_role']=='moderator ':
                 flash("Zalogowano pomyślnie adminie!", "success")
                 return redirect(url_for('routes.admin_dashboard'))

        flash("Nieprawidłowy email lub hasło!", "error")
        return redirect(url_for('routes.login'))

    return render_template('login.html')

# Przekierowanie na stronę głowna
def admin_dashboard():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    reports = db.session.query(
        Zgloszenia.Typ_Zgloszenia,
        Zgloszenia.Opis,
        Zgloszenia.Status,
        Zgloszenia.Lokalizacja_GPS,
        Zgloszenia.Data_Czas_Zgloszenia,
        Zgloszenia.ID_Zgloszenia,
        Zgloszenia.zdjecie_url
    ).filter(
        Zgloszenia.Status == 'oczekujące').all()

    return render_template('dashboard_admin.html', reports=reports)

def change_status(report_id):
    data = request.get_json()
    new_status = data.get('status')

    report = Zgloszenia.query.get(report_id)
    if report:
        report.Status = new_status
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Report not found'}), 404

def register():
    return render_template('register.html',)

def submit_register():
    try:
        # Pobieranie danych z formularza
        email = request.form.get('email')
        password = request.form.get('password')
        re_password =  request.form.get('re_password')
        username = request.form.get('username')

        # Walidacja wprowadzonych danych
        if not email or not password or not re_password or not username:
            return jsonify({'status': 'error', 'message': 'Wszystkie pola są wymagane.'}), 400

        if password != re_password:
            return jsonify({'status': 'error', 'message': 'Hasła się nie zgadzają.'}), 400

        # Sprawdzenie, czy e-mail już istnieje
        if Uzytkownicy.query.filter_by(Email=email).first():
            return jsonify({'status': 'error', 'message': 'E-mail jest już zajęty.'}), 400

        # Tworzenie nowego użytkownika
        nowy_uzytkownik = Uzytkownicy(
            ID_Uzytkownika = db.session.query(func.max(Uzytkownicy.ID_Uzytkownika)).scalar()+1,
            Nazwa_Uzytkownika=username,
            Email=email,
            Haslo=password,
            Rola='user',
            Data_Rejestracji=datetime.now().strftime('%Y-%m-%d'),
        )

        # Zapis do bazy danych
        db.session.add(nowy_uzytkownik)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Użytkownik został zarejestrowany pomyślnie.'}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Błąd serwera: {str(e)}'}), 500


def dashboard():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    return render_template('dashboard.html', user_name=session['user_name'], user_role=session['user_role'])

# przekierowanie na strone zgloszen
def report():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    return render_template('report.html')

def submit_report():
    try:
        # Pobranie danych z formularza
        vehicle_type = request.form.get('vehicle_type')
        photo = request.files.get('photo')  # Plik przesłany przez użytkownika
        description = request.form.get('description')  # Opcjonalny opis
        print(photo)
       # Przechowywanie zdjęcia (w katalogu `/home/Smiglo1222/mysite/static/uploads`)
        photo_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo.filename}"
        photo.save(f"/home/Smiglo1222/mysite/static/uploads/{photo_filename}")
        photo_filename = f"uploads/{photo_filename}"


        # Tworzenie nowego zgłoszenia
        new_report = Zgloszenia(
            ID_Zgloszenia = db.session.query(func.max(Zgloszenia.ID_Zgloszenia)).scalar()+1,
            Typ_Zgloszenia=vehicle_type,
            Opis=description,
            Lokalizacja_GPS=f"{session['lat']},{session['lng']}",
            Data_Czas_Zgloszenia=datetime.now().date().strftime('%Y-%m-%d'),
            Status="oczekujące",  # Domyślny status
            ID_Uzytkownika= session['user_id'],
            zdjecie_url = photo_filename
        )

        # Dodanie zgłoszenia do bazy danych
        db.session.add(new_report)
        db.session.commit()

        return redirect(url_for('routes.report_success'))

    except Exception as e:
        return jsonify({'error': f'Wystąpił błąd: {str(e)}'}), 500

def report_success():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    return render_template('report_success.html')

# przekierowanie na odznaki
def badges():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    progress = {
    typ_zgloszenia: liczba_odznak
    for typ_zgloszenia, liczba_odznak in db.session.query(
        Zgloszenia.Typ_Zgloszenia,
        func.count(Zgloszenia.ID_Zgloszenia).label('Liczba_Zgloszeni')
    ).filter(Zgloszenia.ID_Uzytkownika == session.get('user_id')).group_by(Zgloszenia.Typ_Zgloszenia).all()
}
    return render_template('badges.html', progress = progress)

# przekierowanie na stronę z raportami
def my_reports():
    if 'user_id' not in session:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "error")
        return redirect(url_for('login'))

    reports = db.session.query(
        Zgloszenia.Typ_Zgloszenia,
        Zgloszenia.Opis,
        Zgloszenia.Status
    ).filter(
        Zgloszenia.ID_Uzytkownika == session['user_id']).all()
    print(reports)
    return render_template('my_reports.html', reports=reports)


# endpoint wylogowania
def logout():
    session.clear()
    flash("Wylogowano pomyślnie!", "success")
    return redirect(url_for('routes.login'))


def save_point():
    data = request.get_json()  # Pobranie danych JSON z żądania
    lat = data.get('lat')  # Pobranie szerokości geograficznej
    lng = data.get('lng')  # Pobranie długości geograficznej
    session['lng'] = lng
    session['lat'] = lat
    # Tutaj można zapisać dane w bazie danych lub logach
    print(f"Otrzymano dane: lat={lat}, lng={lng}")
    # Odesłanie odpowiedzi do frontendu
    return jsonify({'status': 'success', 'message': 'Punkt zapisany pomyślnie'})

