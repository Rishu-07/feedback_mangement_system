from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psycopg2
import os
import re
import secrets
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta

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
    try:
        conn = psycopg2.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )
        print("Database connection established.")
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", str(e))
        return None

@app.route('/')
@app.route('/home')
def home():
    print("Rendering home page.")
    return render_template('index.html')

@app.route('/about_us')
def about():
    return render_template('about_us.html')

@app.route('/login')
def login():
    session.pop('user_info', None)
    session.pop('token', None)
    session.pop('nonce', None)
    print("Session cleared. Redirecting to Google for authentication.")
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
        print("User authorized:", user_info)

        if re.match(r'^su-.*@sitare\.org$', email):
            return redirect(url_for('dashboard'))
        elif re.match(r'^kpuneet474@gmail\.com$', email):
            return redirect(url_for('teacher_portal'))
        elif re.match(r'^krishu747@gmail\.com$', email):
            return redirect(url_for('admin_portal'))
        else:
            print("Invalid email format:", email)
            return "Invalid email format", 400
    else:
        print("Authorization failed.")
        return "Authorization failed", 400

@app.route('/dashboard')
def dashboard():
    user_info = session.get('user_info')
    print("Accessing dashboard for user:", user_info)

    if not user_info:
        print("User not logged in. Redirecting to login.")
        return redirect(url_for('login'))

    if re.match(r'^su-.*@sitare\.org$', user_info['email']):
        return redirect(url_for('student_portal'))
    elif re.match(r'^kpuneet474@gmail\.com$', user_info['email']):
        return redirect(url_for('teacher_portal'))
    elif re.match(r'^krishu747@gmail\.com$', user_info['email']):
        return redirect(url_for('admin_portal'))
    else:
        print("Invalid user role for email:", user_info['email'])
        return "Invalid user role", 400

@app.route('/student_portal')
def student_portal():
    user_info = session.get('user_info')
    print("Accessing student portal for user:", user_info)

    if not user_info or not re.match(r'^su-.*@sitare\.org$', user_info['email']):
        print("User not authorized for student portal. Redirecting to login.")
        return redirect(url_for('login'))
    # make sure feedback will only open on saturday
    # current_day = datetime.now().weekday()
    # is_saturday = (current_day == 5)

    # if not is_saturday:
    #     print("Student portal is only accessible on Saturdays. Redirecting to home.")
    #     return redirect(url_for('not_saturday'))

    courses = []
    if re.match(r'^su-220.*@sitare\.org$', user_info['email']):
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
    elif re.match(r'^su-230.*@sitare\.org$', user_info['email']):
        courses = [
            {"course_id": 1, "course_name": "Course 1: Dr. Kushal Shah"},
            {"course_id": 2, "course_name": "Course 2: Dr. Nayan Patel"},
            {"course_id": 3, "course_name": "Course 3: Dr. Omkar Pandya"},
            {"course_id": 4, "course_name": "Course 4: Dr. Parth Patel"},
            {"course_id": 5, "course_name": "Course 5: Ms. Preeti Shukla"},
            {"course_id": 6, "course_name": "Course 6: Dr. Rakesh Jain"},
            {"course_id": 7, "course_name": "Course 7: Dr. Saurabh Shah"},
            {"course_id": 8, "course_name": "Course 8: Dr. Sonali Gupta"}
        ]
    print("Courses available for student:", courses)

    emails = {
        "Dr. Kushal Shah": "kpuneet474@gmail.com",
        "Dr. Sonika Thakral": "sonika@sitare.org",
        "Dr. Achal Agrawal": "achal@sitare.org",
        "Ms. Preeti Shukla": "preet@sitare.org",
        "Dr. Amit Singhal": "amit@siatre.org"
    }

    instructor_emails = {}
    for course in courses:
        course_name = course["course_name"]
        instructor_name = course_name.split(": ")[1]
        if instructor_name in emails:
            instructor_emails[course["course_id"]] = emails[instructor_name]

    session['instructor_emails'] = instructor_emails
    print("Instructor emails:", instructor_emails)

    # return render_template('student_portal.html', is_saturday=is_saturday, user_info=user_info, courses=courses)
    return render_template('student_portal.html', user_info=user_info, courses=courses)


@app.route('/not_saturday', methods=['GET', 'POST'])
def not_saturday():
    user_info = session.get('user_info')

    if not user_info or not re.match(r'^su-230.*@sitare\.org$', user_info.get('email', '')):
        print("User not authorized for student portal. Redirecting to login.")
        return redirect(url_for('login'))

    student_email = session.get('user_info', {}).get('email')
    num_feedback = '1' # Default for last 1 week
    if request.method == 'POST':
        num_feedback = request.form.get('num_feedback', 'all')
        print(num_feedback)

    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = """
            SELECT 
                CourseCode2, DateOfFeedback, Week, Question1Rating, Question2Rating, Remarks
            FROM 
                feedback
            WHERE 
                studentEmaiID = %s
            ORDER BY
                DateOfFeedback DESC
            """
            if num_feedback.isdigit():
                query += " LIMIT %s"
                cursor.execute(query, (student_email, int(num_feedback)))
            else:
                # query += " ORDER BY DateOfFeedback DESC"
                cursor.execute(query, (student_email,))
            
            feedback_data = cursor.fetchall()
            cursor.close()
            conn.close()
            cursor.close()
            conn.close()
            print("Feedback data fetched for student:", student_email)
        else:
            print("Failed to fetch feedback data due to connection issue.")
            feedback_data = []
    except psycopg2.Error as e:
        print(f"Database error while fetching feedback: {str(e)}")
        feedback_data = []

    return render_template('saturday.html', user_info=user_info, feedback_data=feedback_data)

@app.route('/teacher_portal')
def teacher_portal():
    user_info = session.get('user_info')
    if not user_info or not re.match(r'^kpuneet474@gmail\.com$', user_info['email']):
        return redirect(url_for('login'))

    instructor_email = user_info['email']
    feedback_data = []
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = """
                SELECT CourseCode2, DateOfFeedback, Week, Question1Rating, Question2Rating, Remarks 
                FROM feedback 
                WHERE instructorEmailID = %s AND DateOfFeedback >= (CURRENT_DATE - INTERVAL '2 weeks')
            """
            cursor.execute(query, (instructor_email,))
            feedback_data = cursor.fetchall()
            cursor.close()
            conn.close()
    except psycopg2.Error as e:
        print(f"Database error: {str(e)}")

    avg_question1_rating = avg_question2_rating = 0
    if feedback_data:
        total_question1_rating = sum(row[3] for row in feedback_data if row[3] is not None)
        total_question2_rating = sum(row[4] for row in feedback_data if row[4] is not None)
        num_feedbacks = len(feedback_data)
        avg_question1_rating = total_question1_rating / num_feedbacks
        avg_question2_rating = total_question2_rating / num_feedbacks

        rating_distribution_q1 = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        rating_distribution_q2 = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for row in feedback_data:
            q1_rating = row[3] if row[3] is not None else 0
            q2_rating = row[4] if row[4] is not None else 0
            if q1_rating in rating_distribution_q1:
                rating_distribution_q1[q1_rating] += 1
            if q2_rating in rating_distribution_q2:
                rating_distribution_q2[q2_rating] += 1
        print("Rating Distribution Q1:", rating_distribution_q1)
        print("Rating Distribution Q2:", rating_distribution_q2)
        if request.args.get('data') == 'json':
            return jsonify({
                'rating_distribution_q1': rating_distribution_q1,
                'rating_distribution_q2': rating_distribution_q2
            })



    return render_template(
    'teacher_portal.html',
    user_info=user_info,
    feedback_data=feedback_data,
    avg_question1_rating=avg_question1_rating,
    avg_question2_rating=avg_question2_rating
)




    
@app.route('/admin_portal')
def admin_portal():
    user_info = session.get('user_info')
    if not user_info or not re.match(r'^krishu747@gmail.com\.com$', user_info['email']):
        return redirect(url_for('login'))
    instructor_email = user_info['email']
    feedback_data = []
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = """
                SELECT CourseCode2, instructorEmailID, AVG(Question1Rating) AS avg_q1_rating, AVG(Question2Rating) AS avg_q2_rating
                FROM feedback_table
                WHERE instructorEmailID = %s
                GROUP BY CourseCode2, instructorEmailID
            """
            cursor.execute(query, (instructor_email,))
            ratings_data = cursor.fetchall()
            # Prepare data for the template
            ratings = []
            for row in ratings_data:
                ratings.append({
                    'course_code': row[0],
                    'instructor_email': row[1],
                    'avg_q1_rating': row[2],
                    'avg_q2_rating': row[3]
                })
            cursor.close()
            conn.close()
    except Exception as e:

        print("Error fetching ratings data:", e)
        ratings = []

    return render_template('admin_portal.html', ratings=ratings)

@app.route('/logout')
def logout():
    session.pop('user_info', None)
    session.pop('token', None)
    session.pop('nonce', None)
    print("User logged out. Session cleared.")
    return redirect(url_for('home'))

@app.route('/get_form/<course_id>')
def get_form(course_id):
    print(f"Rendering form for course ID: {course_id}")
    return render_template('course_form.html', course_id=course_id)

def create_feedback_table_if_not_exists():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS feedback (
        CourseCode2 VARCHAR(50),
        studentEmaiID VARCHAR(100),
        DateOfFeedback DATE,
        Week INT,
        instructorEmailID VARCHAR(100),
        Question1Rating INT,
        Question2Rating INT,
        Remarks TEXT
    );
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
            print("Table created or already exists.")
    except psycopg2.Error as e:
        print(f"Database error while creating table: {str(e)}")
    finally:
        conn.close()

@app.route('/submit_all_forms', methods=['POST'])
def submit_all_forms():
    instructor_emails = session.get('instructor_emails', {})
    data = request.form.to_dict(flat=False)
    print("Received form data:", data)  # Debugging line

    feedback_entries = {}
    date_of_feedback = datetime.now().date()
    student_email_id = session.get('user_info', {}).get('email')

    # Define the start date for the first week
    initial_start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")

    # Create the week table
    week_table = [
        {
            "week_no": i + 1,
            "start_date": initial_start_date + timedelta(weeks=i),
            "end_date": (initial_start_date + timedelta(weeks=i)) + timedelta(days=6)
        }
        for i in range(60)
    ]

    # Get the current date
    current_date = datetime.now()

    # Determine the current week
    current_week_no = next(
        (week["week_no"] for week in week_table if week["start_date"] <= current_date <= week["end_date"]),
        None
    )

    for key, values in data.items():
        match = re.match(r'course_(\d+)\[(\w+)\]', key)
        if not match:
            print(f"Key '{key}' does not match expected format.")
            continue
        
        course_id = match.group(1)
        field = match.group(2)
        if field not in ['understanding', 'revision', 'suggestion']:
            print(f"Field '{field}' is not a recognized feedback field.")
            continue
        
        if course_id not in feedback_entries:
            feedback_entries[course_id] = {'understanding': None, 'revision': None, 'suggestion': None}

        feedback_entries[course_id][field] = values[0]
    
    print("Processed feedback entries:", feedback_entries)  # Debugging line
    
    prepared_feedback_entries = []
    for course_id, form_data in feedback_entries.items():
        understanding_rating = form_data.get('understanding')
        revision_rating = form_data.get('revision')
        suggestion = form_data.get('suggestion')
        instructor = instructor_emails.get(course_id)
        print(f"Processing feedback for course {course_id}: {form_data}")

        if not understanding_rating or not revision_rating:
            print("Missing ratings. Returning error.")
            return jsonify({"status": "error", "message": "All questions must be rated."}), 400
        
        prepared_feedback_entries.append(
            (course_id, student_email_id, date_of_feedback, current_week_no, instructor, understanding_rating, revision_rating, form_data.get('suggestion', 'None')  # Default to 'None' if empty
)
        )
    
    create_feedback_table_if_not_exists()
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO feedback (CourseCode2, studentEmaiID, DateOfFeedback, Week, instructorEmailID, Question1Rating, Question2Rating, Remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, prepared_feedback_entries)
            conn.commit()
            cursor.close()
            conn.close()
            print("Feedback data successfully inserted.")
            return jsonify({"status": "success"})
        else:
            print("Failed to insert feedback due to connection issue.")
            return jsonify({"status": "error", "message": "Database connection failed."}), 500
    except psycopg2.Error as e:
        error_details = f"Database error: {str(e)}"
        print(error_details)  # Debugging line
        return jsonify({"status": "error", "message": error_details}), 500
    except Exception as e:
        error_details = f"Error: {str(e)}"
        print(error_details)  # Debugging line
        return jsonify({"status": "error", "message": error_details}), 500
    
# @app.route('/average_ratings', methods=['GET'])
# def average_ratings():
    try:
        conn = get_db_connection()
        if conn:
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
            print(f"Average ratings - Understanding: {avg_understanding_rating}, Revision: {avg_revision_rating}")

            return jsonify({
                "status": "success",
                "average_understanding_rating": avg_understanding_rating,
                "average_revision_rating": avg_revision_rating
            })
        else:
            print("Failed to calculate average ratings due to connection issue.")
            return jsonify({"status": "error", "message": "Database connection failed."}), 500
    except psycopg2.Error as e:
        error_details = f"Database error: {str(e)}"
        print(error_details)
        return jsonify({"status": "error", "message": error_details}), 500

if __name__ == '__main__':
    app.run(debug=True)
