import sqlite3
import os

# Remove existing database if it exists
if os.path.exists('users.db'):
 os.remove('users.db')
# Create and setup database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
# Create users table
cursor.execute('''
CREATE TABLE users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE NOT NULL,
 password TEXT NOT NULL,
 email TEXT NOT NULL,
 is_admin INTEGER DEFAULT 0
)
''')
# Create products table
cursor.execute('''
CREATE TABLE products (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 price REAL NOT NULL,
 description TEXT
)
''')
# Insert sample users
users = [
 ('admin', 'adminStationery', 'admin@brainboxstatonery.com', 1),
 ('Santos', 'santosStationery', 'santos@brainboxstatonery.com', 0),
 ('Alex', 'alexStationery', 'alex@brainboxstatonery.com', 0),
 ('Bryan', 'bryanStationery', 'bryan@brainboxstatonery.com', 0)
]


cursor.executemany(
 'INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)',
 users
)
# Insert sample products
products = [
 ('Exercise Books', 9.99, 'A5 size exercise books'),
 ('Geometry Sets', 19.99, 'Complete geometry set'),
 ('Sellotape', 7.99, 'Clear adhesive tape roll'),
 ('Envelope', 20.99, 'Pack of 50 standard envelopes')
]
cursor.executemany(
 'INSERT INTO products (name, price, description) VALUES (?, ?, ?)',
 products
)
# Create a secret table with sensitive data
cursor.execute('''
CREATE TABLE secret_data (
 id INTEGER PRIMARY KEY,
 secret_key TEXT,
 credit_card TEXT,
 personal_notes TEXT
)
''')
secret_data = [
 (1, 'COMPANY_SECRET_KEY_12345', '4532-1234-5678-9012', 'Confidential project details'),
 (2, 'API_KEY_XYZ789', '5111-2222-3333-4444', 'Employee personal information')
]
cursor.executemany('INSERT INTO secret_data (id, secret_key, credit_card, personal_notes) VALUES (?,?, ?, ?)', secret_data)

conn.commit()
conn.close()
print("Database setup completed successfully!")
print("Created tables: users, products, secret_data")
print("Sample users created:")
print(" admin/adminStationery (admin user)")
print(" Santos/santosStationery")
print(" Alex/alexStationery")
print(" Bryan/bryanStationery")