from flask import Flask, request, redirect, url_for, render_template, session, escape, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import pdb, os, uuid

app = Flask(__name__)
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
cwd = os.getcwd()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/site.db' % cwd
UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.isfile(app.config['UPLOAD_FOLDER']):
	os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	usertodos = db.relationship('Todo', lazy='dynamic')
	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		self.password = password
	def __repr__(self):
		return self.username

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	do = db.Column(db.String(100))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	image = db.Column(db.String(200))
	def __init__(self, do, user_id, image):
		self.do = do
		self.user_id = user_id
		self.image = image
	def __repr__(self):
		return '%r' % self.do

def is_authenticated():
	if 'usersession' in session:
		check = User.query.get(session['usersession'])
		if check:
			return True	
	return False

def allowed_user(tasknum):
	check = Todo.query.get(tasknum)	
	if check:
		if check.user_id == session['usersession']:
			return True
	return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/login", methods=['POST','GET'])
def login():
	if request.method == 'POST':
		find = User.query.filter_by(username=request.form['user']).first()
		if find: 
			if request.form['user'] == find.username and request.form['pass'] == find.password :
				usersessionid = User.query.filter_by(username=request.form['user']).first()
				session['usersession'] = usersessionid.id
				return redirect(url_for('list'))
		return render_template('login.html', check=is_authenticated())
	if is_authenticated():
		return render_template('login.html', check=is_authenticated())
	return render_template('login.html', check=is_authenticated())	
		
@app.route("/registration", methods=['POST','GET'])
def registration():
	if request.method == 'POST':
		checkuser = User.query.filter((User.username == request.form['user']) | (User.email == request.form['mail'])).first()
		if checkuser is None and request.form['user'] and request.form['mail']:
			if request.form['password'] == request.form['passconfirm']:
				newuser = User(request.form['user'], request.form['mail'], request.form['password'])
				db.session.add(newuser)
				db.session.commit()			
				session['usersession'] = newuser.id
				return redirect(url_for('list'))
	return render_template('registration.html', check=is_authenticated())

@app.route("/add", methods=['POST','GET'])
def add():
	if is_authenticated():
		if request.method == 'POST': 
			addtask = Todo(request.form['task'],session['usersession'],None)
			db.session.add(addtask)
			db.session.commit()
			return redirect(url_for("list"))
		return render_template('add.html')
	return redirect(url_for('login'))

@app.route("/image/<taskid>", methods=['POST','GET'])
def image(taskid):
	if is_authenticated():		
		if request.method == 'POST':
			if 'image' not in request.files:
				flash('No file part')
				return render_template('image.html',image=taskid)
			imagefile = request.files['image']
			if imagefile.filename == '':
				flash('No selected file')
				return render_template('image.html',image=taskid)
			filename = imagefile.filename
			file_ext = filename.split('.')
			if Todo.query.filter_by(image=filename).first():
				filename = str(uuid.uuid4().hex) + '.' + file_ext[1]
			if filename and allowed_file(imagefile.filename):
				filename = secure_filename(filename)
				imagefile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				todoimage = Todo.query.get(int(taskid))
				if todoimage.image:
					imagecheck = app.config['UPLOAD_FOLDER']+'/'+todoimage.image
					if os.path.isfile(imagecheck):
						os.remove(imagecheck)
				todoimage.image = filename
				db.session.commit()
				return redirect(url_for("list"))
		return render_template('image.html',image=taskid)	
	return redirect(url_for('login'))
	
@app.route("/list")
def list():
	if is_authenticated():
		useresc = escape(session['usersession'])
		records = Todo.query.filter(Todo.user_id==useresc).all()
		name = User.query.get(useresc)
		return render_template('list.html', todos = records, user = name)
	return redirect(url_for('login'))

@app.route("/display/<image>")
def uploaded_file(image):
	if is_authenticated():
		return send_from_directory(app.config['UPLOAD_FOLDER'],image)
	return redirect(url_for('login'))	

@app.route("/edit/<taskid>", methods=['POST','GET'])
def edit(taskid):
	if is_authenticated():
		if allowed_user(taskid):
			taskedited = Todo.query.get(int(taskid))
			taskeditedsend = taskedited.do.replace("'","")
			if request.method == "GET":
				return render_template('edit.html',edit=taskid, task=taskeditedsend)
			taskedited.do = request.form['task']
			db.session.commit()
		return redirect(url_for("list"))
	return redirect(url_for('login'))
	
@app.route("/remove/<taskid>")
def remove(taskid):
	if is_authenticated():
		if allowed_user(taskid):
			imagedel = Todo.query.get(int(taskid)).image
			if imagedel:
				imagecheck = app.config['UPLOAD_FOLDER'] +'/'+imagedel	
				if os.path.isfile(imagecheck):
					os.remove(imagecheck)
			db.session.delete(Todo.query.get(int(taskid)))
			db.session.commit()
		return redirect(url_for("list"))
	return redirect(url_for('login'))

secvar = os.urandom(15)
app.secret_key = secvar
if __name__ == "__main__":
	app.run()


