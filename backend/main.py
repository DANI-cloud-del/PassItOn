from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # For session management

@app.route('/')
def home():
    user = session.get('username', 'Guest')
    top_deals = [
        {"title": "Exclusive Textbooks Sale", "description": "Get up to 50% off on last year's textbooks.", "icon": "book", "color": "#4fbbd6"},
        {"title": "Stationery Pack Deal", "description": "Bundle of pens, notebooks, and highlighters.", "icon": "pen", "color": "#8e44ad"},
        {"title": "Hot Kitchen Gadgets", "description": "Essential kitchen utensils for your hostel room.", "icon": "utensils", "color": "#e74c3c"},
        {"title": "Tech Accessories", "description": "Chargers, lamps and smart gadgets at low prices.", "icon": "laptop", "color": "#2ecc71"},
    ]
    notices = [
        "Need a calculator for physics lab.",
        "Looking for a used ballpoint pen.",
        "Anyone has extra notebooks to share?"
    ]
    
    return render_template('home.html', user=user, top_deals=top_deals, notices=notices)

@app.route('/announcements')
def announcements():
    # Example announcements - replace with DB or storage as needed
    notices = [
        "Need a calculator for physics lab.",
        "Looking for a used ballpoint pen.",
        "Anyone has extra notebooks to share?",
        "Request: Extension cord for phone charger."
    ]
    return render_template('announcements.html', notices=notices)

@app.route('/deals')
def deals():
    # Sample deals grouped by category
    deals_by_category = {
        "Calculators": [
            {"title": "Scientific Calculator", "price": 450, "image": "calc1.jpg", "description": "Good condition, Casio fx-991EX"},
            {"title": "Basic Calculator", "price": 150, "image": "calc2.jpg", "description": "Simple model, battery operated"}
        ],
        "Books": [
            {"title": "Data Structures Textbook", "price": 400, "image": "book1.jpg", "description": "Used condition, 3rd edition"},
            {"title": "Linear Algebra Guide", "price": 350, "image": "book2.jpg", "description": "Almost new, hardcover"}
        ],
        # Add other categories similarly
    }
    return render_template('deals.html', deals_by_category=deals_by_category)

@app.route('/sell-item', methods=['GET', 'POST'])
def sell_item():
    if request.method == 'POST':
        # Process form data here, save new item & image, redirect or show confirmation
        # For now, just redirect back to deals page
        return redirect(url_for('deals'))
    return render_template('sell_item.html')

@app.route('/add-to-cart')
def add_to_cart():
    item_name = request.args.get('item')
    # Handle adding item to user's cart logic here
    # For now, simple confirmation
    return f"Added <b>{item_name}</b> to cart! (Implement cart logic)"


app.run(debug=True)