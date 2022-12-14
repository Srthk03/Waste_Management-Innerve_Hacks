from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import aiml 
import os




app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique = True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('index.html')
    return render_template('first.css')



@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/citizen', methods=['GET', 'POST'])
@login_required
def citizen():
    return render_template('citizen.html')

@app.route('/collector', methods=['GET', 'POST'])
@login_required
def collector():
    return render_template('collector.html')

@app.route('/citizenreqform', methods=['GET', 'POST'])
@login_required
def citizenreqform():
    return render_template('citizenreqform.html')


@app.route('/feedbackForm', methods=['GET', 'POST'])
@login_required
def feedbackForm():
    return render_template('feedbackForm.html')

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    return render_template('payment.html')



#ChatBot
@app.route("/chat")
@login_required
def chat():
    return render_template('chat.html')

@app.route("/ask", methods=['GET','POST'])
@login_required
def ask():
  message = request.form['messageText'].encode('utf-8').strip()

  kernel = aiml.Kernel()

  if os.path.isfile("bot_brain.brn"):
      kernel.bootstrap(brainFile = "bot_brain.brn")
  else:
      kernel.bootstrap(learnFiles = os.path.abspath("aiml/std-startup.xml"), commands = "load aiml b")
      kernel.saveBrain("bot_brain.brn")

  
  while True:
      if message == "quit":
          exit()
      elif message == "save":
          kernel.saveBrain("bot_brain.brn")
      else:
          bot_response = kernel.respond(message)
          
          return jsonify({'status':'OK','answer':bot_response})


if __name__ == '__main__':
    app.run(debug=True)   
    

