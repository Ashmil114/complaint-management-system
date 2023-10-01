from flask import Flask,render_template,request,redirect,url_for,flash,session
from flask_mysqldb import MySQL

app=Flask(__name__)
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="cmplnt"
app.secret_key="sample_key" # its for msg flashing



mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cur = mysql.connection.cursor()
        #checking for user is already have account or not
        users = cur.execute("SELECT * FROM users WHERE username = %s AND email = %s",(username,email))
        if users == 0:
            cur.execute("INSERT INTO `users` (`username`, `email`, `password`) VALUES (%s, %s, %s)",(username,email,password))
            mysql.connection.commit()
            cur.close()
            flash('Registration Successfull,Login Now !')
            return redirect(url_for('login'))
        else:
            flash('Username already Existed !')
            return redirect(url_for('register'))
    return render_template("register.html")

@app.route('/login',methods=['POST','GET'])
def login():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur =mysql.connection.cursor()
        user = cur.execute("SELECT * FROM users WHERE email = %s AND password = %s ",(email,password))
        if user == 1:
            Details = cur.fetchall()
            return  redirect(url_for('user',user=Details[0][1]))
        else:
            flash('User Not Found !')
            return render_template("login.html")
    return render_template("login.html")

@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur =mysql.connection.cursor()
        user = cur.execute("SELECT * FROM admin WHERE username = %s AND password = %s ",(username,password))
        users = cur.fetchall()
        if user == 1:
            return  redirect(url_for('AdminPage',user=users[0][1]))

    return render_template("adminLogin.html")

@app.route('/user/<user>',methods=['POST','GET'])
def user(user):
    cur =mysql.connection.cursor()
    user = cur.execute("SELECT * FROM users WHERE username = %s",(user,))
    user=cur.fetchall()
    session["user"] = user
    username = user[0][1]
    email = user[0][2]
    if request.method == 'POST':
        complaint = request.form['complaint']   
        suggestion = request.form['suggestion'] 
        status = "pending"
        cur.execute("INSERT INTO `complaints` (`username`, `email`, `complaint`, `suggestion`, `status`,`solution`) VALUES (%s, %s, %s, %s, %s,%s)",(username,email,complaint,suggestion,status,''))
        mysql.connection.commit()
        cur.close()
        # print(complaint,suggestion,username,email)
        flash('Your Complaint was forwarded to Admin ')
        return  redirect(url_for('RegCmplt'))
    return render_template("user/registerCmplt.html",user=user)



@app.route('/user/register',methods=['POST','GET'])
def RegCmplt():
    user = session["user"]
    cur =mysql.connection.cursor()
    user = cur.execute("SELECT * FROM users WHERE username = %s",(user[0][1],))
    user=cur.fetchall()
    username = user[0][1]
    email = user[0][2]
    if request.method == 'POST':
        complaint = request.form['complaint']   
        suggestion = request.form['suggestion'] 
        status = "pending"
        cur.execute("INSERT INTO `complaints` (`username`, `email`, `complaint`, `suggestion`, `status`,`solution`) VALUES (%s, %s, %s, %s, %s,%s)",(username,email,complaint,suggestion,status,''))
        mysql.connection.commit()
        cur.close()
        # print(complaint,suggestion,username,email)
        flash('Your Complaint was forwarded to Admin ')
        return  redirect(url_for('RegCmplt'))
    return render_template("user/registerCmplt.html",user=user)

@app.route('/user/view')
def viewStatus():
    user = session["user"]
    cur =mysql.connection.cursor()
    complaint = cur.execute("SELECT * FROM complaints WHERE username = %s AND email = %s",(user[0][1],user[0][2]))
    complaints=cur.fetchall()
    
    if complaint >0:
        return render_template("user/viewStatus.html",user=user,complaints=complaints,s=1)
    else:
        return render_template("user/viewStatus.html",user=user,complaints=complaints,s=0)

@app.route('/admin/<user>',methods=['GET','POST'])
def AdminPage(user):
    cur =mysql.connection.cursor()
    complaint = cur.execute("SELECT * FROM complaints WHERE status = 'pending'")
    complaints=cur.fetchall()
    if request.method == "POST":
        data = request.form['data']
        return  redirect(url_for('complaintView',data=data,user=user))
        
    return render_template("admin/adminPage.html",complaint=complaints)

@app.route('/admin/<user>/<data>',methods=['GET','POST'])
def complaintView(user,data):
    cur =mysql.connection.cursor()
    complaint = cur.execute("SELECT * FROM complaints WHERE complaint = %s ",(data,))
    complaints=cur.fetchall()
    print(complaints)

    if request.method == "POST":
        sol = request.form['solution']
        status = "checked"
        cur =mysql.connection.cursor()
        cur.execute("UPDATE `complaints` SET status = 'checked'  WHERE username = %s AND email = %s AND complaint = %s ",(complaints[0][1],complaints[0][2],complaints[0][3]))
        mysql.connection.commit()
        cur.execute("UPDATE `complaints` SET solution = %s  WHERE username = %s AND email = %s AND complaint = %s",(sol,complaints[0][1],complaints[0][2],complaints[0][3]))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('AdminPage',user=user))
        # return "done"
    return render_template("admin/ComplaintView.html",data=complaints)


if __name__ == '__main__':
    app.run(debug=True)