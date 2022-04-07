from datetime import datetime, timedelta
from itertools import product
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text # textual queries
#rom sqlalchemy.ext.declarative import declarative_base

# ATTENTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#     You are currently viewing an unfinished product
#     PLEASE review TODOs in app.py functions
#     AND review table schema changes in comments before
#     removing this VERY IMPORTANT MESSAGE

# ATTENTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


hush_hush = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
#ripped off of flask's site for an example of a good secret key

# https://piazza.com/class/kxj5alixpjg4ft?cid=289 for info on these sets
students = set()
instructors = set()

app = Flask(__name__)
app.config['SECRET_KEY'] = hush_hush
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ass3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 8) #change as fit
#engine = create_engine('sqlite:///ass3.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Account(db.Model):
    __tablename__ = 'Account'
    Account_id = db.Column(db.Integer, primary_key = True, unique = True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    password = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False) #doesnt need unique
    type = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):
        return f"Account('{self.username}', '{self.email}, {self.password}, {self.type}')"

class Student(db.Model):
    __tablename__ = 'Student'
    Student_id = db.Column(db.Integer, db.ForeignKey('Account.Account_id'), nullable = False, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable = True) 
    def __repr__(self):
        return f"Student('{self.username}, {self.Student_id}"

class Instructor(db.Model):
    __tablename__ = 'Instructor'
    username = db.Column(db.String(20), unique=True, nullable = True) 
    Instructor_id = db.Column(db.Integer, db.ForeignKey('Account.Account_id'), nullable = False, primary_key = True)
    def __repr__(self):
        return f"Instructor('{self.username}, {self.Instructor_id}"

class Marks(db.Model):
    __tablename__ = 'Marks'
    student_id = db.Column(db.Integer, db.ForeignKey('Student.Student_id'), nullable = False, primary_key = True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Instructor.Instructor_id'), nullable = False)
    assessment = db.Column(db.String(20), nullable = False, primary_key = True)
    grade = db.Column(db.Integer, nullable = False)
    #spelling error: accessment -> assessment 

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    q1 = db.Column(db.Integer, nullable = False)
    q2 = db.Column(db.Integer, nullable = False)
    q3 = db.Column(db.Integer, nullable = False)
    q4 = db.Column(db.Integer, nullable = False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Instructor.Instructor_id'), nullable = False)
    Feed_id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)

class Remark(db.Model):
    __tablename__ = 'Remark'
    assessment = db.Column(db.String(20),db.ForeignKey('Marks.assessment'), nullable = False, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('Student.Student_id'), nullable = False, primary_key = True)
    blurb = db.Column(db.String(100), unique = False, nullable = True)

class RemarkRequest():
    def __init__(self, input):
        self.assessment = input.assessment  #spelling
        self.student = get_name_from_id(input.student_id)
        self.blurb = input.blurb

class Mark():
    def __init__(self, input):
        self.student = get_name_from_id(input.student_id)
        self.instructor = get_name_from_id(input.instructor_id)
        self.assessment = input.assessment  #spelling
        self.grade = input.grade

"""
#Filtering in SQLAlchemy
print('*******Filtering 1*******')
for person in db.session.query(Person).filter(Person.id == 5):
    print(person.username, person.email)

#Counting in SQLAlchemy
print('*******Counting*******')
print(db.session.query(Person).filter(Person.id > 3).count())

#order by in SQLAlchemy
print('*******Order By*******')
for person in db.session.query(Person).order_by(Person.id):
    print(person.username, person.email)

# IN operator 
print('*******In Operator*******')
ids_to_select = ['1', '2', '3']
r3 = db.session.query(Person).filter(Person.id.in_(ids_to_select)).all()
for person in r3:
    print(person.username)

# AND 
print('*******AND*******')
r4 = db.session.query(Person).filter(Person.username.like('P%'), Person.id.in_([1, 10]))
for person in r4:
    print(person.username)

"""
# ROUTING FOR NAVBAR

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/course_team')
def course_team():
    return render_template('course_team.html')

@app.route('/weekly_schedule')
def weekly_schedule():
    return render_template('weekly_schedule.html')

@app.route('/lectures')
def lectures():
    return render_template('lectures.html')

@app.route('/assignments')
def assignments():
    return render_template('assignments.html')

@app.route('/labs')
def labs():
    return render_template('labs.html')

#new pages for A3 ---------------------------------------------
@app.route('/stu_home')
def stu_home():
    pagename = 'Home Page'
    return render_template('stu_home.html', pagename = pagename)

@app.route('/submit_feedback' , methods = ['GET', 'POST'])
def submit_feedback():
    pagename = 'Anonymous Feedback'
    profs = get_all_profs()

    if request.method == 'GET':
        return render_template('submit_feedback.html', pagename = pagename, profs=profs)
    else: #POST
        q1 = request.form['Q1']
        q2 = request.form['Q2']
        q3 = request.form['Q3']
        q4 = request.form['Q4']
        instructor = request.form['instructor']
        feedback = (q1,q2,q3,q4,instructor)
        add_feedback(feedback)
        flash("feedback submitted!", "success")
        return render_template('submit_feedback.html', pagename = pagename, profs=profs)



@app.route('/view_marks', methods = ['GET', 'POST'])
def view_marks():
    pagename = 'View Marks'
    student = session['name']
    id = get_id_from_name(student)
    query_marks = query_student_marks(id)
    if request.method == 'GET':
        return render_template('view_marks.html', pagename = pagename, query_marks=query_marks)
    else: #POST
        assessment = request.form['assessment']
        reason = request.form[assessment]
        
        remark_req = (assessment, id,reason)
        add_remark(remark_req)
        return render_template('view_marks.html', pagename = pagename, query_marks=query_marks)
#TODO fix issue of assessments past the first not being accepted
#TODO check if there already exists a remark req in the db (same student same assessment), 
#           if so, flash a rejection message (only one remark per assessment)

@app.route('/instr_home')
def instr_home():
    pagename = 'Home Page'
    return render_template('instr_home.html', pagename = pagename)    

@app.route('/instr_marks', methods = ['GET', 'POST'])
def instr_marks():
    pagename = 'View Student Marks'
    if request.method == 'GET':
        query_marks = get_all_marks()
        marks = set()
        for mark in query_marks:
            temp = Mark(mark)
            marks.add(temp)
        return render_template('instr_marks.html', pagename = pagename, marks=marks)


@app.route('/view_feedback', methods = ['GET', 'POST'])
def view_feedback():
    pagename = 'View Feedback'
    if request.method == 'GET':
        prof_name = session['name']
        id = get_id_from_name(prof_name)
        query_feedbacks = get_feedback(id)
        return render_template('view_feedback.html', pagename = pagename, query_feedbacks=query_feedbacks)
#TODO the css file needs to center the table created by jinja code


@app.route('/view_remark', methods = ['GET', 'POST'])
def view_remark():
    pagename = 'Remarks'
    if request.method == 'GET':
        query_remarks = get_all_remark()
        remarks = set()
        for requests in query_remarks:
            remark = RemarkRequest(requests)
            remarks.add(remark)
        return render_template('view_remark.html', pagename = pagename, remarks=remarks)
#TODO center the table created by jinja in css file 


@app.route('/enter_marks', methods = ['GET', 'POST'])
def enter_marks():
    pagename = 'Enter Marks'
    if request.method == 'GET':
        return render_template('enter_marks.html', pagename = pagename)
    else: #POST
        student = request.form['student']
        assessment = request.form['assessment']
        grade = request.form['grade']

        #check if the student is real
        flag = False
        students = get_all_stus()
        for stu in students:
            if stu.username == student:
                flag = True #means the student exists
                break

        if(flag == False):
            flash("Student does not exist!", "error")
            return render_template('enter_marks.html', pagename = pagename) #happens when invalid student name

        stu_id = get_id_from_name(student)
        instr_id = get_id_from_name(session['name'])

        #check if the combo of stu_id+asessment exists (remark)
        student_marks = query_student_marks(stu_id)

        for mark in student_marks:
            if(mark.assessment  == assessment ): #db spelling error see Mark class
                
                mark.grade = grade #this updates the info
                db.session.commit()
                flash("Assessment remarked!", "success")
                return render_template('enter_marks.html', pagename = pagename)
                break 
        
        input = (stu_id,instr_id,assessment,grade)

        add_mark(input)
        #add a flash message for mark added
        flash("mark added!")
        return render_template('enter_marks.html', pagename = pagename)

@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    
    pagename = 'Register'
    if request.method == 'GET':
        return render_template('register.html', pagename = pagename)
    else: #POST aka checking db to see if credentials are correct
        username = request.form['Username']
        email = request.form['Email']

        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        types= request.form['Acc_Type'] 
        reg_details =(
            username,
            email,
            hashed_password,
            types
        )

        account = Account.query.filter_by(username = username).first()
        
        #if account with this name appeared in db --> username is already taken
        if account:
            flash("Username has already be taken!", "error") #ASSUMES WE CAN REBOOT DB (if not include email here)
            return redirect(url_for('register'))
        #otherwise, successful registration
        else:
            add_users(reg_details)
            #add the info to the related tables
            account1 = Account.query.filter_by(username = username).first()
            acc_num = account1.Account_id
            if ((types == 'Student') == True):
                students.add(username)
                add_users_student(reg_details, acc_num)
            else:
                instructors.add(username)
                add_users_instructor(reg_details, acc_num)
        
            flash('Registration Successful! Please login now:', "success")
            return redirect(url_for('login'))
#TODO add error checking when no inputs are entered for each inut field

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            flash('already logged in!!')

            #which page should be shown?
            if (session['type'] == 'Student'):
                return redirect(url_for('stu_home'))
            elif (session['type'] == 'Instructor'):
                return redirect(url_for('instr_home'))
            else:
                flash("but we couldn't retreive account type, please login again")
                return render_template('login.html')
        else:
            return render_template('login.html')
    else: #this means POST
        username = request.form['Username']
        password = request.form['Password']
        account = Account.query.filter_by(username = username).first()
        #if user fails authentication
        if not account or not bcrypt.check_password_hash(account.password, password):

            flash('Please check your login details and try again', 'error')
            return render_template('login.html')
        #if user is recognised
        else:
            session.pop('name', default = None) #reset session
            session['name'] = username
            session['type'] = account.type
            
            if (account.type == 'Student' ):
                session.permanent = True
                return redirect(url_for('stu_home'))
            elif (account.type == 'Instructor' ):
                session.permanent = True
                return redirect(url_for('instr_home'))
            else:
                flash('Please check your login details and try again', 'error')
                return render_template('login.html') 
    
# ROUTING FOR NAVBAR

def add_feedback(input):
    feedback = Feedback(q1 = input[0], q2 = input[1], q3 = input[2], q4 = input[3], instructor_id = input[4])
    db.session.add(feedback)
    db.session.commit()

def add_users(reg_details):
    account = Account(username = reg_details[0], email = reg_details[1], password = reg_details[2], type = reg_details[3])
    db.session.add(account)
    db.session.commit()

def add_users_student(reg_details, acc_num):
    student = Student(username = reg_details[0], Student_id =  acc_num)
    db.session.add(student)
    db.session.commit()

def add_users_instructor(reg_details, acc_num):
    account = Instructor(username = reg_details[0], Instructor_id =  acc_num)
    db.session.add(account)
    db.session.commit()

#add a mark to the Mark table
def add_mark(details):
    mark = Marks(student_id = details[0], instructor_id =  details[1],
    assessment  = details[2], grade =  details[3]) #db spelling error see Mark class
    db.session.add(mark)
    db.session.commit()

#add a remark to the Remark table
def add_remark(details):
    remark = Remark(assessment  = details[0], student_id =  details[1],
    blurb = details[2]) #db spelling error see Remark class
    db.session.add(remark)
    db.session.commit()

#getting list of profs from Instructor table
def get_all_profs():
    profs = Instructor.query.all()
    return profs

#getting list of students  from Student table
def get_all_stus():
    stu = Student.query.all()
    return stu

#getting all the marks in the database
def get_all_marks():
    marks = Marks.query.all()
    return marks

#get the account_id belonging to the given name
def get_id_from_name(name):
    account = Account.query.filter_by(username = name).first()
    id = account.Account_id
    return id

#get the username belonging to the given id
def get_name_from_id(id):
    account = Account.query.filter_by(Account_id = id).first()
    name = account.username
    return name

#get the all the remark requests from Remark table
def get_all_remark():
    remarks = Remark.query.all()
    return remarks

#get the feedback tuples of a given id
def get_feedback(instructor_id):
    feedbacks = Feedback.query.filter_by(instructor_id = instructor_id)
    return feedbacks

def query_student_marks(stu_id):
    marks = Marks.query.filter_by(student_id = stu_id)
    return marks

if __name__ == '__main__':
    app.run(debug=True)



