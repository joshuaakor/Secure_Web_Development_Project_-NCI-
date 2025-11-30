from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3
import os
import re
app = Flask(__name__)
app.secret_key = 'secure_secret_key_@%*45!!8120**&'

#HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<htm l>
<head>
    <title>Login - BrainBox Stationery (Secure Version)</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
        input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>BrainBox Stationery (Secure Version)</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}
    {% if message %}
        <div class="success">{{ message }}</div>
    {% endif %}
</body>
</html>
'''
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - BrainBox Stationery (Vulnerable Version)</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .user-info { background: #f0f0f0; padding: 15px; margin: 10px 0; }
        .search-box { background: #e8f4fd; padding: 15px; margin: 10px 0; }
        .products { margin: 20px 0; }
        .product { border: 1px solid #ddd; padding: 10px; margin: 5px 0; }
        .admin { background: #fffacd; padding: 10px; margin: 10px 0; }
    </style>
<head>
<body>
    <h1>Welcome, {{ username }}!</h1>

    <div class="user-info">
        <h3>User Information</h3>
        <p><strong>Username:</strong> {{ username }}</p>
        <p><strong>Email:</strong> {{ email }}</p>
        <p><strong>Admin:</strong> {{ is_admin }}</p>
    </div>
    <div class="search-box">
        <h3>Search Products</h3>
        <form method="GET" action="/search">
            <input type="text" name="query" placeholder="Enter product name..." value="{{ query }}" required>
        <button type="submit">Search</button>
    </form>
    {% if search_error %}
        <div style="color: red;">{{ search_error }}</div>
    {% endif %}
</div>

{% if products %}
<div class="products">
    <h3>Search Results:</h3>
    {% for product in products %}
        <div class="product">
            <strong>{{ product[1] }}</strong> - ${{ product[2] }}<br>
            <em>{{ product[3] }}</em>
 </div>
    {% endfor %}
</div>
{% endif %}

{% if is_admin == 'Yes' %}
    <div class="admin">
        <h3>Admin Functions</h3>
            <p style="background: #ffeb3b; padding: 12px; border-radius: 8px; font-size: 18px;">
                <strong>→ <a href="/admin/products" style="color: #d32f2f; text-decoration: underline;">Manage Products (Full CRUD)</a></strong>
            </p>
        <form method="POST" action="/admin-search">
        <h4>User Lookup</h4>
        <input type="text" name="user_query" placeholder="Enter username or email" required>
        <button type="submit">Lookup User</button>
    </form>

    {% if admin_results %}
        <h4>Lookup Results:</h4>
        <pre>{{ admin_results }}</pre>
    {% endif %}
    </div>
 {% endif %}
 <br>
<a href="/logout">Logout</a>
</body>
</html>
'''

ADMIN_HTML = '''
    <div class="admin">
        <h3>Manage Products (Admin)</h3>
        
        <h4>Add New Product</h4>
        <form method="POST" action="/admin/add-product">
            <input type="text" name="name" placeholder="Product Name" required><br><br>
            <input type="number" step="0.01" name="price" placeholder="Price (e.g. 29.99)" required><br><br>
            <textarea name="description" placeholder="Description" required></textarea><br><br>
            <button type="submit">Add Product</button>
        </form>
        <hr>
        <h4>All Products</h4>
        {% if message %}<p style="color:green;">{{ message }}</p>{% endif %}
        {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
        <table border="1" cellpadding="10" cellspacing="0">
            <tr><th>ID</th><th>Name</th><th>Price</th><th>Description</th><th>Actions</th></tr>
            {% for p in products %}
            <tr>
                <td>{{ p[0] }}</td>
                <td>{{ p[1] }}</td>
                <td>${{ p[2] }}</td>
                <td>{{ p[3] }}</td>
                <td>
                    <a href="/admin/edit-product/{{ p[0] }}">Edit</a> |
                    <a href="/admin/delete-product/{{ p[0] }}" style="color:red;" 
                       onclick="return confirm('Delete this product?')">Delete</a>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5">No products found.</td></tr>
            {% endfor %}
        </table>
        <br><a href="/dashboard">← Back to Dashboard</a>
    </div>
'''

# Input validation function
def is_input_valid(user_input):
    #Allow only alphanumeric characters, spaces, and basic punctuation
    if not re.match(r'^[a-zA-Z0-9\s\.\-\@\_]+$', user_input):
        return False
    
    sql_keywords = ['union', 'select', 'insert', 'delete', 'update', 'drop', '--', ';', "'", '"']
    for keyword in sql_keywords:
        if keyword in user_input.lower():
            return False
    return True

@app.route('/')
def home():
 if 'username' in session:
    return redirect('/dashboard')
 return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

     # Secure Input Validation
        if not is_input_valid(username) or not is_input_valid(password):
            return render_template_string(LOGIN_TEMPLATE, error="Invalid characters in input!")
        
        #Secure Query using parameterized statements
        query = "SELECT * FROM users WHERE username = ? AND password = ?"

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                session['username'] = user[1]
                session['email'] = user[3]
                session['is_admin'] = 'Yes' if user[4] == 1 else 'No'
                conn.close()
                return redirect('/dashboard')
            else:
                conn.close()
                return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials!")

        except Exception as e:
            conn.close()
            # Error logged internally, generic message shown to user
            return render_template_string(LOGIN_TEMPLATE, error="An error occurred. Please try again.")
    
    return render_template_string(LOGIN_TEMPLATE)
 

@app.route('/dashboard')
def dashboard():
        if 'username' not in session:
            return redirect('/login')

        return render_template_string(
            DASHBOARD_TEMPLATE,
            username=session['username'],
            email=session['email'],
            is_admin=session['is_admin'])

@app.route('/search')
def search_products():
 if 'username' not in session:
    return redirect('/login')

 query = request.args.get('query', '')
 products = []
 search_error = None
 
 if query:
    # Implement secure input validation
    if not is_input_valid(query):
        search_error = "Invalid characters in search query!"
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

    # Implement parameterized query to prevent SQL injection
 
    search_query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
    
    search_param = f"%{query}%"

    try:
        cursor.execute(search_query, (search_param, search_param))
        products = cursor.fetchall()
    except Exception as e:
        search_error = "Search error occurred"

        conn.close

    return render_template_string(
        DASHBOARD_TEMPLATE,
        username=session['username'],
        email=session['email'],
        is_admin=session['is_admin'],
        query=query,
        products=products,
        search_error=search_error)
 


@app.route('/admin-search', methods=['POST'])
def admin_search():
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    user_query = request.form['user_query']
    results = ""

    #Secure Input Validation
    if not is_input_valid(user_query):
        results = "Invalid characters in input!"
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

# Secure Query using parameterized statements
    admin_query = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"
    search_param = f"%{user_query}%"

    try:
        cursor.execute(admin_query, (search_param, search_param))
        users = cursor.fetchall()

        if users:
            results = "User Lookup Results:\n"
            for user in users:
                # Display user info excluding password
                results += f"ID: {user[0]}, Username: {user[1]}, Email: {user[3]}, Admin: {user[4]}\n"

        else:
            results = "No users found."

    except Exception as e:
        results = "An error occurred during user lookup."

        conn.close()

    return render_template_string(
        DASHBOARD_TEMPLATE,
        username=session['username'],
        email=session['email'],
        is_admin=session['is_admin'],
        admin_results=results)



@app.route('/logout')
def logout():   
    session.clear()
    return redirect('/login')   


@app.route('/admin/products')
def admin_products():
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Vulnerable but works: list all products
    cursor.execute("SELECT id, name, price, description FROM products")
    all_products = cursor.fetchall()

    # HTML for admin product management (inline, vulnerable style)
    

    return render_template_string(
        DASHBOARD_TEMPLATE + ADMIN_HTML,
        username=session['username'],
        email=session['email'],
        is_admin=session['is_admin'],
        products=all_products,
        message=request.args.get('message'),
        error=request.args.get('error')
    )

# ==================== ADMIN CRUD FOR PRODUCTS (VULNERABLE VERSION) ====================
# 2. Add new product (POST) - VULNERABLE TO SQL INJECTION
@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    name = request.form['name']
    price = request.form['price']
    description = request.form['description']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # INTENTIONALLY VULNERABLE: Direct string interpolation
    query = f"INSERT INTO products (name, price, description) VALUES ('{name}', {price}, '{description}')"

    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return redirect('/admin/products?message=Product+added+successfully')
    except Exception as e:
        conn.close()
        return redirect(f'/admin/products?error=Error: {str(e)}')


# 3. Edit product form (GET)
@app.route('/admin/edit-product/<int:product_id>')
def admin_edit_product_form(product_id):
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, price, description FROM products WHERE id = {product_id}")
    product = cursor.fetchone()
    conn.close()

    if not product:
        return redirect('/admin/products?error=Product+not+found')

    EDIT_HTML = f'''
    <div class="admin">
        <h3>Edit Product ID: {product[0]}</h3>
        <form method="POST" action="/admin/update-product/{product[0]}">
            <p><strong>Name:</strong><br>
            <input type="text" name="name" value="{product[1]}" required style="width:100%"></p>
            
            <p><strong>Price:</strong><br>
            <input type="number" step="0.01" name="price" value="{product[2]}" required style="width:100%"></p>
            
            <p><strong>Description:</strong><br>
            <textarea name="description" style="width:100%; height:100px;" required>{product[3]}</textarea></p>
            
            <button type="submit">Update Product</button> | 
            <a href="/admin/products">Cancel</a>
        </form>
    </div>
    '''

    return render_template_string(
        DASHBOARD_TEMPLATE + EDIT_HTML,
        username=session['username'],
        email=session['email'],
        is_admin=session['is_admin']
    )


# 4. Update product (POST) - VULNERABLE TO SQL INJECTION
@app.route('/admin/update-product/<int:product_id>', methods=['POST'])
def admin_update_product(product_id):
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    name = request.form['name']
    price = request.form['price']
    description = request.form['description']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # INTENTIONALLY VULNERABLE
    query = f"UPDATE products SET name = '{name}', price = {price}, description = '{description}' WHERE id = {product_id}"

    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return redirect('/admin/products?message=Product+updated+successfully')
    except Exception as e:
        conn.close()
        return redirect(f'/admin/products?error=Update+failed: {str(e)}')


# 5. Delete product - VULNERABLE TO SQL INJECTION via URL
@app.route('/admin/delete-product/<int:product_id>')
def admin_delete_product(product_id):
    if 'username' not in session or session['is_admin'] != 'Yes':
        return redirect('/dashboard')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # INTENTIONALLY VULNERABLE: No sanitization of product_id
    cursor.execute(f"DELETE FROM products WHERE id = {product_id}")
    conn.commit()
    conn.close()

    return redirect('/admin/products?message=Product+deleted')



if __name__ == '__main__':
 print("VULNERABLE APPLICATION STARTING")
 print("Access at: http://localhost:5001")
 print("Default credentials: admin/admin123")
 print("WARNING: This app contains intentional SQL Injection vulnerabilities")
 app.run(debug=True, port=5001)


