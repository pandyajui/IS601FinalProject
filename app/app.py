from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'bioData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'BioStats Data'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM biostats')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, biostats=result)


@app.route('/graph', methods=['GET'])
def myGraph():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT Weight_lbs, Height_in FROM biostats')
    result = cursor.fetchall()
    result = json.dumps(result)
    # return str(result)
    return render_template('graph.html', title='Graph', answers=result)

@app.route('/view/<int:biostats_id>', methods=['GET'])
def record_view(biostats_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM biostats WHERE id=%s', biostats_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', biostats=result[0])


@app.route('/edit/<int:biostats_id>', methods=['GET'])
def form_edit_get(biostats_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM biostats WHERE id=%s', biostats_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', biostats=result[0])


@app.route('/edit/<int:biostats_id>', methods=['POST'])
def form_update_post(biostats_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Name'), request.form.get('Sex'), request.form.get('Age'),
                 request.form.get('Height_in'), request.form.get('Weight_lbs'),
                 biostats_id)
    sql_update_query = """UPDATE biostats b SET b.Name = %s, b.Sex = %s, b.Age = %s, b.Height_in = 
        %s, b.Weight_lbs = %s WHERE b.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/biostats/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Biostats Form')


@app.route('/biostats/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Name'), request.form.get('Sex'), request.form.get('Age'),
                 request.form.get('Height_in'), request.form.get('Weight_lbs'))
    sql_insert_query = """INSERT INTO biostats (Name, Sex, Age, Height_in, Weight_lbs) VALUES (%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:biostats_id>', methods=['POST'])
def form_delete_post(biostats_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM biostats WHERE id = %s """
    cursor.execute(sql_delete_query, biostats_id)
    mysql.get_db().commit()
    return redirect("/", code=302)

#Get the API info
@app.route('/api/v1/biostats', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM biostats')
    result = cursor.fetchall()
    json_results = json.dumps(result);
    resp = Response(json_results, status=200, mimetype='application/json')
    return resp

#Retrieve API info for id
@app.route('/api/v1/biostats/<int:biostats_id>', methods=['GET'])
def api_retrieve(biostats_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM biostats WHERE id=%s', biostats_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

#Edit data for ID
@app.route('/api/v1/biostats/<int:biostats_id>', methods=['PUT'])
def api_edit(biostats_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Name'], content['Sex'], content['Age'], content['Height_in'], content['Weight_lbs'], biostats_id)
    sql_update_query = """UPDATE biostats t SET t.Name = %s, t.Sex = %s, t.Age = %s, t.Height_in = %s, t.Weight_lbs = %s WHERE t.id = %s"""
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

#Adding new data
@app.route('/api/v1/biostats', methods=['POST'])
def api_add() -> str:

    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['Name'], content['Sex'], content['Age'], content['Height_in'], content['Weight_lbs'])
    sql_insert_query = """INSERT INTO biostats (Name,Sex,Age,Height_in, Weight_lbs) VALUES (%s,%s,%s,%s,%s )"""
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

#Deleting data by id
@app.route('/api/v1/biostats/<int:biostats_id>', methods=['DELETE'])
def api_delete(biostats_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM biostats WHERE id = %s """
    cursor.execute(sql_delete_query, biostats_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

QUICK_MAIL_VERIFICATION_API_KEY = 'xxxx'
SEND_GRID_API_KEY = 'xxxx'


@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        ##to get the registration data
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        password = request.form.get("password")
        ##to avoid duplicate emails registered
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT email FROM information where email=%s', email)
        checkIfemailExists = cursor.fetchall()
        if checkIfemailExists:
            return render_template("register.html",
                                   msg="Sorry, the email is already taken! Please use a different email")
        ##to verify the email
        client = quickemailverification.Client(QUICK_MAIL_VERIFICATION_API_KEY)
        quickemailverification = client.quickemailverification()
        response = quickemailverification.verify(email)
        for i in response:
            if i['result'] == 'valid':
                inputData = (fname, lname, address, email, password)
                sql_insert_query = """INSERT INTO information(firstName, lastName, address, email,password) VALUES (%s, %s,%s, %s,%s) """
                cursor.execute(sql_insert_query, inputData)
                mysql.get_db().commit()
                return redirect("home.html", code=302)
            else:
                return render_template("register.html",
                                       msg="Sorry, this is a invalid email, Please try with a valid mail")

    if request.method == "GET":
        return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT email,password FROM information where email=%s and password =%s', (email, password))
        result = cursor.fetchall()
        json_result = json.dumps(result)
        print(result)
        print(json_result)
        if (result):
            return render_template("homepageAfterLogin.html", msg="Logged In Successfully!!!")
        else:
            return render_template("login.html", msg="Incorret Login ID/Password !")

    if request.method == "GET":
        return render_template("login.html")

@app.route("/sendMail", methods=['POST'])
def sendmail():
    ## first- get the data from the page
    toemail = request.form.get("email")
    sub = request.form.get("subject")
    content = request.form.get("myTextArea")
    message = Mail(
        from_email='pv36@njit.edu.com',
        to_emails=toemail,
        subject=sub,
        html_content=content)

    try:
        sg = SendGridAPIClient(SEND_GRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)
    return render_template("homepageAfterLogin.html", msg="Message Sent")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

