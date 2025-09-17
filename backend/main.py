import json
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import flash
from flask import Flask, render_template, request, redirect, url_for, session
from flask import session, request, redirect, url_for, render_template, flash
import datetime
from flask import jsonify
from datetime import datetime
DEALS_FILE = 'deals.json'
REQUESTS_FILE = 'requests.json'

# Get the absolute path to the backend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_deals():
    if not os.path.exists(DEALS_FILE):
        return []
    with open(DEALS_FILE, 'r') as f:
        return json.load(f)

def save_deals(deals):
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # For session management

@app.route('/')
def home():
    user = session.get('username', 'Guest')
    top_deals = load_deals()  # Load user-uploaded deals dynamically

    notices = [
        "Need a calculator for physics lab.",
        "Looking for a used ballpoint pen.",
        "Anyone has extra notebooks to share?"
    ]

    show_motto = session.pop('show_motto', False)

    return render_template('home.html',
                           user=user,
                           top_deals=top_deals,
                           notices=notices,
                           show_motto=show_motto)


@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q', '').lower()
    deals = load_deals()

    # Simple filter: find deals whose title contains the query
    results = [d for d in deals if query in d['title'].lower()]

    # Return minimal info for suggestions
    suggestions = [{'id': d['id'], 'title': d['title']} for d in results[:10]]  # limit to 10
    return jsonify(suggestions)


@app.route('/announcements')
def announcements():
    notices = [
        "Need a calculator for physics lab.",
        "Looking for a used ballpoint pen.",
        # etc.
    ]
    requests_list = load_requests()
    return render_template('announcements.html',
                           notices=notices,
                           requests=requests_list,
                           current_user=session.get('username'))

@app.route('/deals')
def deals():
    # supports optional params: search, sort
    search = request.args.get('search', '').lower()
    sort = request.args.get('sort', '')  # e.g., 'oldest' or 'newest'

    deals = load_deals()
    if search:
        deals = [d for d in deals if search in d['title'].lower()]

    if sort == 'oldest':
        deals.sort(key=lambda d: d.get('timestamp', ''), reverse=False)
    elif sort == 'newest':
        deals.sort(key=lambda d: d.get('timestamp', ''), reverse=True)

    deals_by_category = {'All Items': deals}
    return render_template('deals.html',
                           deals_by_category=deals_by_category,
                           current_user=session.get('username'))

@app.route('/delete-deal/<deal_id>', methods=['POST'])
def delete_deal(deal_id):
    if 'username' not in session:
        flash('You must be logged in to remove items.')
        return redirect(url_for('login'))

    deals = load_deals()
    deal_to_delete = next((d for d in deals if d['id'] == deal_id), None)

    if not deal_to_delete:
        flash('Deal not found.')
        return redirect(url_for('deals'))

    if deal_to_delete['creator'] != session['username']:
        flash('You are not authorized to delete this item.')
        return redirect(url_for('deals'))

    deals = [d for d in deals if d['id'] != deal_id]
    save_deals(deals)
    flash('Item removed successfully.')
    return redirect(url_for('deals'))

@app.route('/add_request', methods=['POST'])
def add_request():
    if 'username' not in session:
        return jsonify({'error': 'Login required'}), 401
    
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Empty request text'}), 400

    requests_list = load_requests()
    new_request = {
        'id': str(uuid.uuid4()),
        'text': text,
        'requester': session['username'],
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    requests_list.append(new_request)
    save_requests(requests_list)
    return jsonify({'success': True, 'request': new_request})

@app.route('/delete_request/<request_id>', methods=['POST'])
def delete_request(request_id):
    if 'username' not in session:
        flash('Login required to delete requests.')
        return redirect(url_for('announcements'))

    requests_list = load_requests()
    req = next((r for r in requests_list if r['id'] == request_id), None)

    if not req:
        flash('Request not found.')
        return redirect(url_for('announcements'))

    if req['requester'] != session['username']:
        flash('You are not authorized to delete this request.')
        return redirect(url_for('announcements'))

    requests_list = [r for r in requests_list if r['id'] != request_id]
    save_requests(requests_list)
    flash('Request deleted successfully.')
    return redirect(url_for('announcements'))


@app.route('/sell-item', methods=['GET', 'POST'])
def sell_item():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        
        # Handle file upload
        if 'image' not in request.files:
            flash('No image file uploaded')
            return redirect(request.url)
            
        file = request.files['image']
        
        # If user didn't select a file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            # Save file
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # Create new deal
            new_deal = {
                'id': str(uuid.uuid4()),
                'title': title,
                'description': description,
                'price': float(price),
                'category': category,
                'image': filename,
                'creator': session.get('username'),
                'created_at': datetime.now().isoformat()
            }
            
            # Load existing deals and append new one
            deals = load_deals()
            deals.append(new_deal)
            save_deals(deals)
            
            flash('Item listed successfully!')
            return redirect(url_for('deals'))
            
    return render_template('sell_item.html')

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        email = request.form.get('email', '').strip() or None

        users = load_users()
        if username in users:
            flash('Username already taken, choose another')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        users[username] = {
            'password_hash': password_hash,
            'email': email
        }
        save_users(users)

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        users = load_users()
        user = users.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            session['show_motto'] = True  # Set flag to show motto once
            flash(f'Welcome, {username}!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    return render_template('cart.html')

def load_requests():
    if not os.path.exists(REQUESTS_FILE):
        return []
    with open(REQUESTS_FILE, 'r') as f:
        return json.load(f)

def save_requests(requests):
    with open(REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=2)

app.run(debug=True)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)

