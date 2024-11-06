from inventory import app, request, render_template, redirect, flash, db, User,login_required,login_user,logout_user,add_table,sold_table

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
    db.session.commit()
    return redirect("/home")


@app.route("/soldout",methods = ['POST'])
def updatesold():
    id = request.form.get("p_id")
    qty = request.form.get("p_qty")
    name = request.form.get("p_name")
    new_item = sold_table(id,name,qty)
    db.session.add(new_item)
    db.session.commit()
    return redirect("/home")


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
@app.route("/update")
def update_item():
    return render_template("update.html")
@app.route("/addnew")
def addnew():
    return render_template("add_new.html")
@app.route("/updateexist")
def update_exist():
    return render_template("updateexist.html")

@app.route("/logout")
def logout_page():
    logout_user()
    return render_template("login.html")