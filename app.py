from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from cs50 import SQL
from flask_session import Session
from models import User, Option, Question, Section, Answer, SectionAnswer, QuestionnareResult
from helpers import get_element, get_subscript
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests
from urllib.parse import urlencode
import hashlib
import os
from dotenv import load_dotenv
import socket

# Load the environment variables from the .env file
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
DB_PATH = os.getenv('DB_PATH')

# Configure app
app = Flask(__name__, static_folder='static')

# Connect to database
db = SQL("sqlite:///" + DB_PATH + "questionnaire.db")

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Runtime data
def user():
    return session["user"]
    name = session["user_name"]
    hash = session["hash"]
    partner_id = session["partner_id"]
    return User(name, hash, partner_id)


def user_name():
    return user().name


def user_hash():
    return user().hash


def db_user_id():
    return get_subscript(
        get_element(db.execute("SELECT id FROM users WHERE hash=? LIMIT 1", user_hash()), 0),
        'id'
    )


def create_user_hash(email):
    return hashlib.sha256(email.encode()).hexdigest()


def create_user_partner_link():
    url = request.url_root 
    params = {"partner": user_hash()}
    query_string = urlencode(params)
    full_url = url + query_string
    return full_url


def db_update_user(user):
    partner_id = user.partner_id

    if is_user_registered() and not partner_id:
        return
    
    name = user.name
    hash = user.hash 
    if not partner_id:
        db.execute(
                "INSERT INTO users (name, hash) VALUES (?, ?)",
                name,
                hash
            )
    else:
        db.execute(
                "INSERT OR REPLACE INTO users (name, hash, partner_id) VALUES (?, ?, ?)",
                name,
                hash,
                partner_id
            )


def is_user_registered():
    return len(db.execute("SELECT * FROM users WHERE hash=(?) LIMIT 1", user_hash())) > 0


def is_user_answered():
    return len(db.execute("SELECT * FROM results WHERE user_id=(?) LIMIT 1", db_user_id)) > 0


def is_user_with_partner():
    return len(db.execute("SELECT partner_id FROM users WHERE hash=(?) AND partner_id IS NOT NULL LIMIT 1", user_hash())) > 0


def db_partner_id():
    return get_subscript(
        get_element(db.execute("SELECT partner_id FROM users WHERE hash=? LIMIT 1", user_hash()), 0),
        'partner_id'
    )


def db_partner_name():
    return get_subscript(
        get_element(db.execute("SELECT name FROM users WHERE id=? LIMIT 1", db_partner_id()), 0),
        'name'
    )

def is_user_partner_answered():
    if not is_user_with_partner():
        return False
    partner_id = db_partner_id()

    return len(db.execute("SELECT * FROM results WHERE user_id=(?) LIMIT 1", partner_id)) > 0

def db_sections():
    return db.execute("SELECT * FROM sections")


def retrieve_payload_from_JWT_token(token):
    return id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)


def db_questions():
    return db.execute("SELECT * FROM questions")


def db_questions_by_sections():
    return db.execute("""
        SELECT sections.text AS section_text, sections.id AS section_id, sections.page_order AS section_page_order, questions.id AS question_id, questions.text AS question_text
        FROM questions
        JOIN sections ON questions.section_id = sections.id
        ORDER BY sections.page_order
        """)


def db_options(): 
    return db.execute("SELECT * FROM options")


def db_user_answers_by_id(id):
    results_list = db.execute(
        "SELECT question_id, option_id FROM results WHERE user_id = ?", id
    )
    results_dict = {result['question_id']: result['option_id'] for result in results_list}
    return results_dict


def is_local_computer():
    hostname = socket.gethostname()
    return "local" in hostname


def session_save_user(user):
    session["user_name"] = user.name
    session["user_hash"] = user.hash
    # Check
    session["user"] = user


def save_user(user):
    session_save_user(user)
    db_update_user(user)


# define decorator to add CSP header
@app.after_request
def add_security_headers(resp):
    # To secure your app and prevent cross-site scripting (XSS) attacks
    resp.headers['Content-Security-Policy'] = """
        script-src 'self' https://accounts.google.com/gsi/client; 
        frame-src https://accounts.google.com/gsi/; 
        style-src 'self' https://accounts.google.com/gsi/style fonts.googleapis.com;
        connect-src 'self' https://accounts.google.com/gsi/;
        font-src 'self' fonts.gstatic.com data:;
    """.replace('\n', ' ')

    # To allow Sign In With Google button and/or Google One Tap to function well with popup windows
    resp.headers['Cross-Origin-Opener-Policy'] = "same-origin-allow-popups"

    return resp


@app.route('/api/client-id')
def get_client_id():
    return jsonify({'client_id': CLIENT_ID})


@app.route("/", methods=["GET"])
def home():
    if is_local_computer():
        mock_user = User("Megan", "12345")
        save_user(mock_user)
            
    return render_template("index.html")


def db_user_id_by(user_hash):
    return get_subscript(
        get_element(db.execute("SELECT id FROM users WHERE hash=? LIMIT 1", user_hash), 0),
        'id'
    )

def save_partner(user_hash):
    partner_id = db_user_id_by(user_hash)
    session["user_partner_id"] = partner_id


@app.route("/partner=<user_hash>", methods=["GET"])
def handle_partner(user_hash):
    save_partner(user_hash)
    return redirect("/")


@app.route("/partner_link", methods=["GET"])
def partner_link():
    name = user_name()
    link = create_user_partner_link()
    return render_template("partner_link.html", name = name, link = link)


@app.route("/questions", methods=["GET", "POST"])
def questions():
    if request.method == "GET":
        questions = db_questions_by_sections()
        sections = []

        for question in questions:
            question_model = Question(question["question_id"], question["question_text"])
            if len(sections) > 0 and sections[-1].id == question["section_id"]:
                sections[-1].questions.append(question_model)
            else:
                sections.append(
                    Section(
                        question["section_id"],
                        question["section_page_order"],
                        question["section_text"],
                        [question_model]
                    )
                )

        options = list(map(lambda option: Option(
            option["id"],
            option["text"]
        ), db_options()))

        link = None
        if not is_user_with_partner():
            link = create_user_partner_link()

        return render_template("questions.html", name = user_name(), link = link, sections = sections, options = options)
    else:
        questions = db_questions_by_sections()
        for question in questions:
            question_id = str(question["question_id"])
            answer = request.form.get(question_id)
            db.execute(
                "INSERT OR REPLACE INTO results (user_id, question_id, option_id) VALUES (?, ?, ?)",
                db_user_id(),
                question_id,
                answer
            )
        return redirect(url_for('results'))        


@app.route("/results", methods=["GET"])
def results():
    user_answers = db_user_answers_by_id(db_user_id())
    options = {option['id']: option['text'] for option in db_options()}

    partner_name = "💖"
    if is_user_with_partner():
        partner_name = db_partner_name()

    link = None
    partner_answers = {}
    if is_user_partner_answered():
        partner_answers = db_user_answers_by_id(db_partner_id())
    else:
        link = create_user_partner_link()

    questions = db_questions_by_sections()
    sectionAnswers = []

    for question in questions:
        user_answer = options[user_answers[question["question_id"]]]
        partner_answer = options.get(get_subscript(partner_answers, question["question_id"]), "?")
        answer = Answer(question["question_text"], user_answer, partner_answer)

        if len(sectionAnswers) > 0 and sectionAnswers[-1].id == question["section_id"]:
            sectionAnswers[-1].answers.append(answer)
        else:
            sectionAnswers.append(
                SectionAnswer(
                    question["section_id"], 
                    question["section_text"], 
                    [answer]
                )
            )

    result = QuestionnareResult(user_name(), partner_name, sectionAnswers)

    return render_template("results.html", result=result, link=link)


# @app.route("/results/save", methods=["GET"])
# def save_results():
#     render_template("results.html")


@app.route('/process_data', methods=["POST"])
def process_data():
    data = request.get_json()

    jwt_token = data.get('token')
    print(f"jwt_token python: {jwt_token}")

    if jwt_token is None:
        print(f"Error: jwt_token is None")
        return redirect("/")
    
    try:
        payload = retrieve_payload_from_JWT_token(jwt_token)
        user_name = payload['name']
        user_email = payload['email']
        user_hash = create_user_hash(user_email)
        user_partner_id = get_subscript(session, "user_partner_id")
        user = User(user_name, user_hash, user_partner_id)
        save_user(user)
        return redirect(url_for('partner_link'))
        
    except ValueError as error:
        # Invalid token
        # Return to the auth form with error
        # Show error
        assert()
        print(f"Error: {error}")
        return redirect("/")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
