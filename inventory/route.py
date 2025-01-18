from inventory import app, request, render_template, redirect, flash, db, User,login_required,login_user,logout_user,add_table,sold_table
from sqlalchemy import event,func
from flask import flash

# Process registration route
@app.route("/process_registration", methods=["POST"])
def Process_reg():
    mail = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('con_password')

    # Check if passwords match
    if password != confirm:
        flash('Passwords do not match', 'danger')
        return redirect("/reg")
     
    # Check if the user already exists
    existing_user = User.query.filter_by(email=mail).first()
    if existing_user:
        flash('User already exists, choose a different email', 'danger')
        return redirect("/reg")
    
    # Create a new user and save to the database
    new_user = User(mail, password)
    login_user(new_user)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful!', 'success')
    return redirect("/home")

@app.route("/addnew",methods = ['POST'])
def appendnew():
    id = request.form.get("pr_id")
    name = request.form.get("pr_name")
    qty = request.form.get("pr_qty")
    price= request.form.get("pr_price")
    new_item = add_table(id,name,qty,price)
    db.session.add(new_item)
    try:
        if int(price) < 0:
            db.session.rollback()
            return render_template('error.html')
        db.session.commit()
        flash("Item added successfully!", "success")
    except ValueError as e:
        db.session.rollback()
        return render_template('error.html')
    return redirect("/home")
@app.route("/updateproduct",methods=['POST'])
def updateproduct():
    id = request.form.get("p_id")
    qty = int(request.form.get("p_qty"))
    row = add_table.query.filter(add_table.product_id == id).first()
    row.qty += qty
    db.session.commit()
    return redirect("/home")
@app.route("/updateprice",methods =['POST'])
def updateprice():
    id = request.form.get("p_id")
    pr = request.form.get("n_price") 
    result = add_table.query.filter(add_table.product_id == id).update({add_table.price: pr})
    db.session.commit()
    return redirect("/home")

@event.listens_for(add_table, 'before_insert')
def prevent_duplicate_product_id(mapper, connection, target):
    print("working")
    # Use target.product_id instead of id
    exists = db.session.query(add_table).filter_by(product_id=target.product_id).first()
    if exists:
        if exists.price <=0:
            raise ValueError("Duplicate product_id detected. Insertion aborted.")

@app.route("/soldout",methods = ['POST'])
def updatesold():
    id = request.form.get("p_id")
    qty = request.form.get("p_qty")
    name = request.form.get("p_name")
    exist = add_table.query.filter_by(product_id=id).first()
    if exist:
        new_item = sold_table(id,name,qty)
        db.session.add(new_item)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("productnotfound.html")
@app.route("/avail")
def get_available_items():
    # Query to calculate available stock for each product
       # Query to calculate available stock for each product using a subquery
    subquery = db.session.query(
        add_table.product_id,
        add_table.name,
        (add_table.qty - func.coalesce(func.sum(sold_table.qty), 0)).label('available_qty')
    ).outerjoin(sold_table, add_table.product_id == sold_table.product_id) \
     .group_by(add_table.product_id, add_table.name) \
     .subquery()

    # Filter for products with available_qty > 0
    results = db.session.query(subquery.c.product_id, subquery.c.name, subquery.c.available_qty) \
        .filter(subquery.c.available_qty > 0) \
        .all()

    # Return the result as a list of dictionaries
    available_items = [{'product_id': result.product_id, 'name': result.name, 'available_qty': result.available_qty} for result in results]
    return render_template("available_items.html",items=available_items)
# Process login route
@app.route("/login", methods=['POST'])
def Process_login():
    mail = request.form.get('email')
    password = request.form.get('password')
    
    # Check if the user exists
    existing_user = User.query.filter_by(email=mail).first()
    if existing_user:
        # Check if the password is correct
        if existing_user.check_password(password):
            login_user(existing_user)
            flash('Login successful!', 'success')
            return redirect("/home")
        else:
            flash('Invalid password', 'danger')
    else:
        flash('User does not exist', 'danger')
    
    return redirect("/")
@app.before_request
def create_tables():
    db.create_all()
@app.route("/")
def firstpage():
    return render_template("login.html")
@app.route("/reg")
def register():
    return render_template("register.html")
@app.route("/home")
@login_required
def home():
    return render_template("home.html")
@app.route("/add")
def add_item():
    return render_template("add.html")
@app.route("/sold")
def sold_item():
    return render_template("sold.html")
@app.route ("/availableitems")
def availableitems():
    return render_template("available_items.html")
@app.route("/update")
def update_item():
    return render_template("update.html")
@app.route("/addnew")
def addnew():
    return render_template("add_new.html")
@app.route("/updateexist")
def update_exist():
    return render_template("updateexist.html")
@app.route("/history")
def history():
    sold_items = sold_table.query.all()
    return render_template("history.html",history = sold_items)
@app.route("/stats")
def stats():
    return render_template("stats.html")
@app.route("/logout")
def logout_page():
    logout_user()
    return render_template("login.html")
@app.route("/most_sold")
def most_sold_page():
    result = db.session.query(
        sold_table.product_id,
        sold_table.name,
        func.sum(sold_table.qty).label('total_quantity'),
        func.sum(sold_table.qty * add_table.price).label('total_price')  # Calculate total price
    ).join(
        add_table, sold_table.product_id == add_table.product_id
    ).group_by(
        sold_table.product_id, sold_table.name
    ).order_by(
        func.sum(sold_table.qty).desc()  # Sort by total_quantity in descending order
    ).all()
    
    # Pass results to the template
    return render_template("most_sold.html", result=result)

@app.route("/most_profitable")
def most_profit_page():
    result = db.session.query(
        sold_table.product_id,
        sold_table.name,
        func.sum(sold_table.qty).label('total_quantity'),
        func.sum(sold_table.qty * add_table.price).label('total_price')  # Calculate total price
    ).join(
        add_table, sold_table.product_id == add_table.product_id
    ).group_by(
        sold_table.product_id, sold_table.name
    ).order_by(
        func.sum(sold_table.qty*add_table.price).desc()  # Sort by total_profit in descending order
    ).all()
    
    # Pass results to the template
    return render_template("most_profitable.html",result=result)