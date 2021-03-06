from flask import Flask, json, render_template, request, flash, url_for, redirect, jsonify
from flask_login import login_manager, login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from secrets import token_urlsafe

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '9ca5bead08f09c4c4f70714gefg23807e9a25f60rfb969fd'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# handling user
@login_manager.user_loader
def load_user(mail):

    return User.query.get(mail)

# db Model of the user
class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    mail     = db.Column(db.String(120))
    password = db.Column(db.String(80))
    token    = db.Column(db.String(20))

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

# db Model for the resources the user can create    
class Resource(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(40))
    returns = db.Column(db.String(1000))
    userid  = db.Column(db.Integer)

# Homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    
    return render_template('index.html', user=current_user)


# login page, checking if the email exists as a User in the database and after checking if the hash of the password is coresponding the provided password after hashing it (in sha256)
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


# registering user, checking for username, email and password length then lowercasing the username and the email and saving it as a User
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
            newUser = User(username=username.lower(), mail=mail.lower(), password=generate_password_hash(password, method='sha256'), token=token_urlsafe(20))

            db.session.add(newUser)
            db.session.commit()

            login_user(newUser, remember=True)

            flash('Account created successfuly with the name {} !'.format(username), category='success')

        return redirect(url_for('login'))
    
    return render_template('register.html', user=current_user)

# simply logging out user and sending a flash message
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

# delete resources of user via dashboard, requires a username, a user id and valid user token
@app.route('/u/<string:user>/delete/<int:id>')
@login_required
def delete_resource_via_dashboard(user, id):
    
    user_token = request.args.get('token')
    
    if current_user.username == user and current_user.token == user_token:

        resource = Resource.query.get_or_404(id)
            
        
        try:
            db.session.delete(resource)
            db.session.commit()
            flash('The ressource {} has been successfully deleted'.format(resource.name), category='success')
        except:
            flash('An error occured during deletion', category='error')
        
        return redirect(url_for('dashboard'))
        
    else:
        
        return 'Wrong username or token'


@app.route('/u/<string:user>/resource/delete/<string:resource_name>')
def api_delete_resource(user, resource_name):
    
    user_token = request.args.get('token')
    
    if not user_token:
        'missing token'
        
    else:
        # getting the user by the given username 
        user = User.query.filter_by(username=user).first()
        
        # if the provided token and the requested user token match, it will get the requested resource and delete it
        if user.token == user_token:
            resource = Resource.query.filter_by(userid=user.id, name=resource_name).first()
            
            jsn = {'deleted_resource': resource_name,
                   'requested_by': user.username}
            
            return jsonify(jsn)


# get the resources of the users, requires a username, a resource name and a valid token
@app.route('/u/<string:user>/resource/get/<string:resource_name>')
def api_get_resource(user, resource_name):
    
    # getting the obligatory token from the url arguments
    user_token = request.args.get('token')
    
    if not user_token:
        return 'missing token'
        
    else:
        # getting the user by the given username
        user = User.query.filter_by(username=user).first()
        
        # if the provided token and the requested user token match, it will get the requested resource and return it
        if user.token == user_token:
            resource = Resource.query.filter_by(userid=user.id, name=resource_name).first()
            
            return jsonify(resource.returns)

        else:  
            return 'Wrong token'

# returns account panel page of current_user if the user is logged in 
@app.route('/account')
@login_required
def account():
    
    return render_template('account.html', user=current_user)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)