from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psycopg2
import os
import re
import secrets
from authlib.integrations.flask_client import OAuth
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '43dce9f95d583e2537057a62713f51ab56895991d7f6507cb464fe0751c9692a')

# Database configuration
db_config = {
    'dbname': "dhp2024",
    'user': "postgres",
    'password': "54321",
    'host': "localhost",
    'port': "5432"
}

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', '39257771502-vsoftekttnf9ga7l8i49oohlse57b29q.apps.googleusercontent.com'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', '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'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    redirect_uri='http://127.0.0.1:5000/authorize',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
)

def get_db_connection():
    return psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

    # creating a table
create_table = """
    CREATE TABLE IF NOT EXISTS feedback (
        CourseCode2 INTEGER NOT NULL,
        DateOfFeedback DATE NOT NULL,
        Week INTEGER NOT NULL,
        instructorEmailID VARCHAR(255) NOT NULL,
        Question1Rating INTEGER CHECK (Question1Rating BETWEEN 1 AND 5),
        Question2Rating INTEGER CHECK (Question2Rating BETWEEN 1 AND 5),
        Remarks TEXT,
        PRIMARY KEY (CourseCode2, DateOfFeedback, instructorEmailID)
    );
"""

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(create_table)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    session.pop('user_info', None)
    session.pop('token', None)
    session.pop('nonce', None)

    redirect_uri = url_for('authorize', _external=True)
    nonce = secrets.token_urlsafe(16)
    state = secrets.token_urlsafe(16)
    session['nonce'] = nonce
    session['state'] = state
    return google.authorize_redirect(redirect_uri, nonce=nonce, state=state)

@app.route('/authorize')
def authorize():
    nonce = session.pop('nonce', None)

    token = google.authorize_access_token(nonce=nonce)
    session['token'] = token
    user_info = google.parse_id_token(token, nonce=nonce)

    if user_info:
        email = user_info['email']
        name = user_info.get('name', 'User')  # Use 'User' as a default name if not present
        session['user_info'] = {'email': email, 'name': name}

        if re.match(r'^su-.*@sitare\.org$', email) or email == 'admin@sitare.org':
            return redirect(url_for('dashboard'))
        elif re.match(r'^kpuneet474@gmail\.com$', email):
            return redirect(url_for('teacher_portal'))
        else:
            return "Invalid email format", 400
    else:
        return "Authorization failed", 400

@app.route('/dashboard')
def dashboard():
    user_info = session.get('user_info')

    if not user_info:
        return redirect(url_for('login'))

    if re.match(r'^su-.*@sitare\.org$', user_info['email']):
        return redirect(url_for('student_portal'))
    elif re.match(r'^kpuneet474@gmail\.com$', user_info['email']):
        return redirect(url_for('teacher_portal'))
    elif user_info['email'] == 'admin@sitare.org':
        return redirect(url_for('admin_portal'))
    else:
        return "Invalid user role", 400

@app.route('/student_portal')
def student_portal():
    user_info = session.get('user_info')

    if not user_info or not re.match(r'^su-.*@sitare\.org$', user_info['email']):
        return redirect(url_for('login'))

    courses = []
    if re.match(r'^su-230.*@sitare\.org$', user_info['email']):
        courses = [
            {"course_id": 1, "course_name": "DHP: Dr. Kushal Shah"},
            {"course_id": 2, "course_name": "DSA: Dr. Sonika Thakral"},
            {"course_id": 3, "course_name": "MFC: Dr. Achal Agrawal"},
            {"course_id": 4, "course_name": "Communication and Ethics: Ms. Preeti Shukla"},
            {"course_id": 5, "course_name": "Book Club and Social Emotional Intelligence: Ms. Preeti Shukla"},
            {"course_id": 6, "course_name": "Calculus: Dr. Achal Agrawal"}
        ]
    elif re.match(r'^su-240.*@sitare\.org$', user_info['email']):
        courses = [
            {"course_id": 1, "course_name": "Linear Algebra: Dr. Kushal Singh"},
            {"course_id": 2, "course_name": "Intro. to Communication and Ethics: Ms. Preeti Shukla"},
            {"course_id": 3, "course_name": "Book Club and Social Emotional Intelligence: Ms. Preeti Shukla"},
            {"course_id": 4, "course_name": "Programming Methodology in Python: Dr. Kushal Shah"},
            {"course_id": 5, "course_name": "ITC: Dr. Anuja Agrawal"}
        ]
    elif re.match(r'^su-220.*@sitare\.org$', user_info['email']):
        courses = [
            {"course_id": 1, "course_name": "Course 1: Dr. Mahesh Singh"},
            {"course_id": 2, "course_name": "Course 2: Dr. Nayan Patel"},
            {"course_id": 3, "course_name": "Course 3: Dr. Omkar Pandya"},
            {"course_id": 4, "course_name": "Course 4: Dr. Parth Patel"},
            {"course_id": 5, "course_name": "Course 5: Dr. Qureshi Sheikh"},
            {"course_id": 6, "course_name": "Course 6: Dr. Rakesh Jain"},
            {"course_id": 7, "course_name": "Course 7: Dr. Saurabh Shah"},
            {"course_id": 8, "course_name": "Course 8: Dr. Sonali Gupta"}
        ]
    emails = {
        "Dr. Kushal Shah": "kushal@sitare.org",
        "Dr. Sonika Thakral": "sonika@sitare.org",
        "Dr. Achal Agrawal": "achal@sitare.org",
        "Ms. Preeti Shukla": "preet@sitare.org",
        "Dr. Amit Singhal":"amit@siatre.org"
        }
    
    instructor_emails = {}
    for course in courses:
        course_name = course["course_name"]
        instructor_name = course_name.split(": ")[1]
        if instructor_name in emails:
            instructor_emails[instructor_name] = emails[instructor_name]
            session['instructor_emails'] = instructor_emails

    

    return render_template('student_portal.html', user_info=user_info, courses=courses)

@app.route('/teacher_portal')
def teacher_portal():
    user_info = session.get('user_info')

    if not user_info or not re.match(r'^kpuneet474@gmail\.com$', user_info['email']):
        return redirect(url_for('login'))

    return render_template('teacher_portal.html')

@app.route('/admin_portal')
def admin_portal():
    user_info = session.get('user_info')

    if not user_info or user_info['email'] != 'admin@sitare.org':
        return redirect(url_for('login'))

    return render_template('admin_portal.html')

@app.route('/logout')
def logout():
    session.pop('user_info', None)
    session.pop('token', None)
    session.pop('nonce', None)
    return redirect(url_for('home'))

@app.route('/get_form/<course_id>')
def get_form(course_id):
    return render_template('course_form.html', course_id=course_id)

# @app.route('/submit_all_forms', methods=['POST'])
# def submit_all_forms():
#     instructor_emails = session.get('instructor_emails')
#     data = request.form.to_dict(flat=False)
#     feedback_entries = []
#     date_of_feedback = datetime.now().date()
#     week = datetime.now().isoweekday()
#     for course_key, form_data_list in data.items():
#         course_id = course_key.split('_')[1]
#         form_data = {key: value[0] for key, value in zip(['understanding', 'revision', 'remarks'], form_data_list)}
#         understanding_rating = form_data.get('understanding')
#         revision_rating = form_data.get('revision')
#         remarks = form_data.get('remarks')
    

#         # Ensure all required fields are filled
#         if understanding_rating is None or revision_rating is None:
#             return jsonify({"status": "error", "message": "All questions must be rated."}), 400

#         feedback_entries.append(
#             (course_id, date_of_feedback, week, instructor_emails, understanding_rating, revision_rating, remarks)
#         )

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         insert_query = """
#         INSERT INTO feedback 
#         (CourseCode2, DateOfFeedback, Week, instructorEmailID, Question1Rating, Question2Rating, Remarks)
#         VALUES 
#         (%s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.executemany(insert_query, feedback_entries)
#         conn.commit()
#         cursor.close()
#         conn.close()
#     except psycopg2.Error as e:
#         return jsonify({"status": "error", "message": str(e)})
@app.route('/submit_all_forms', methods=['POST'])
def submit_all_forms():
    instructor_emails = session.get('instructor_emails', {})
    data = request.form.to_dict(flat=False)
    
    # Debug: print the received data
    print("Received data:", data)
    
    feedback_entries = []
    date_of_feedback = datetime.now().date()
    week = datetime.now().isoweekday()
    
    for course_key, form_data_list in data.items():
        # Debug: print each course key and form data list
        print(f"Processing {course_key}: {form_data_list}")
        
        course_id = course_key.split('_')[1]
        form_data = {key: value[0] for key, value in zip(['understanding', 'revision', 'remarks'], form_data_list)}
        
        understanding_rating = form_data.get('understanding')
        revision_rating = form_data.get('revision')
        remarks = form_data.get('remarks')
        
        # Ensure all required fields are filled
        if understanding_rating is None or revision_rating is None:
            return jsonify({"status": "error", "message": "All questions must be rated."}), 400
        
        # Debug: print the prepared feedback entry
        print("Prepared feedback entry:", (course_id, date_of_feedback, week, instructor_emails, understanding_rating, revision_rating, remarks))
        
        feedback_entries.append(
            (course_id, date_of_feedback, week, instructor_emails.get(form_data['instructor']), understanding_rating, revision_rating, remarks)
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO feedback 
        (CourseCode2, DateOfFeedback, Week, instructorEmailID, Question1Rating, Question2Rating, Remarks)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, feedback_entries)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except psycopg2.Error as e:
        # Debug: print the error
        print("Database error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/average_ratings', methods=['GET'])
def average_ratings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT 
            AVG(Question1Rating) AS avg_understanding_rating,
            AVG(Question2Rating) AS avg_revision_rating
        FROM feedback
        """
        cursor.execute(query)
        result = cursor.fetchone()
        avg_understanding_rating = result[0]
        avg_revision_rating = result[1]

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "average_understanding_rating": avg_understanding_rating,
            "average_revision_rating": avg_revision_rating
        })
    except psycopg2.Error as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
