from logging import captureWarnings, error, log
from operator import contains
from flask import Flask, json, render_template, request, flash, url_for, redirect, jsonify
from flask_login import login_manager, login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '9ca5bead08f09c4c4f70714gefg23807e9a25f60rfb969fd'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(mail):

    return User.query.get(mail)

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    mail     = db.Column(db.String(120))
    password = db.Column(db.String(80))

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
    
class Resource(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(40))
    returns = db.Column(db.String(1000))
    userid  = db.Column(db.Integer)

# Homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    
    return render_template('index.html', user=current_user)


# Page de login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        mail     = request.form['mail']
        password = request.form['password']

        user = User.query.filter_by(mail=mail).first()

        if user:
            if check_password_hash(user.password, password):
                flash('You logged in successfuly !', category='success')
                login_user(user, remember=True)

                return redirect(url_for('index'))

            else:
                flash('Wrong password or inexisting user.', category='error')
        else:
            flash('Mail address does not exist.', category='error')

    return render_template('login.html', user=current_user)


# Page de register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        mail     = request.form['mail']

        user = User.query.filter_by(mail=mail).first()

        if user:
            flash('The mail address already exists.', category='error')
            return redirect(url_for('register'))

        elif len(username) < 3:
            flash('The username must be at least 2 characters.', category='error')
            return redirect(url_for('register'))

        elif len(password) < 8:
            flash('The password must be at least 8 characters long.', category='error')
            return redirect(url_for('register'))
            
        elif len(mail) < 4:
            flash('The mail address must be at least than 3 characters long.', category='error')
            return redirect(url_for('register'))

        else:
            newUser = User(username=username.lower(), mail=mail.lower(), password=generate_password_hash(password, method='sha256'))

            db.session.add(newUser)
            db.session.commit()

            login_user(newUser, remember=True)

            flash('Account created successfuly with the name {} !'.format(username), category='success')

        return redirect(url_for('login'))
    
    return render_template('register.html', user=current_user)

@app.route('/logout')
def lougout():
    
    logout_user()
    
    flash('You logged out !', category='else')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    if request.method == 'POST':
        
        resource_name     = request.form['resource_name']
        resource_returns  = request.form['resource_returns']
        
        if len(resource_name) < 2 or ' ' in resource_name:
            flash('The name must be at least 2 characters long and not contain spaces', category='error')
            return redirect(url_for('dashboard'))
        else: 
            resource_userid = current_user.id
        
            resource = Resource(name=resource_name, returns=resource_returns, userid=resource_userid)
            
            db.session.add(resource)
            db.session.commit()
            
            flash('Name: {} | Returns: {}'.format(resource.name, resource_returns, resource_userid), category='else')
            
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard.html', user=current_user, resources=Resource.query.filter_by(userid=current_user.id))


@app.route('/u/<string:user>/delete/<int:id>')
@login_required
def delete_resource(user, id):
    
    if current_user.username == user:
    
        resource = Resource.query.get_or_404(id)
        
        try:
            db.session.delete(resource)
            db.session.commit()
            flash('The ressource {} has been successfully deleted'.format(resource.name), category='success')
        except:
            flash('An error occured during deletion', category='error')
        
        return redirect(url_for('dashboard'))
        
    else:
        
        return '404'

@app.route('/u/<string:user>/resource/<string:resource_name>')
def get_resource(user, resource_name):
    
    user = User.query.filter_by(username=user).first()
    resource = Resource.query.filter_by(userid=user.id, name=resource_name).first()
    
    return jsonify(resource.returns)

@app.route('/account')
@login_required
def account():
    
    return render_template('account.html', user=current_user)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)