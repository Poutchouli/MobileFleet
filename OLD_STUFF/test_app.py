# test_app.py
# Simple test version of the app to verify templates work
import os
from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Simulate logged in session
    session['username'] = 'admin'
    return render_template('admin/dashboard.html')

@app.route('/admin/phones')
def admin_phones():
    session['username'] = 'admin'
    return render_template('admin/phones.html')

@app.route('/admin/sims')
def admin_sims():
    session['username'] = 'admin'
    return render_template('admin/sims.html')

@app.route('/admin/workers')
def admin_workers():
    session['username'] = 'admin'
    return render_template('admin/workers.html')

@app.route('/admin/users')
def admin_users():
    session['username'] = 'admin'
    return render_template('admin/users.html')

@app.route('/manager/dashboard')
def manager_dashboard():
    session['username'] = 'manager'
    return render_template('manager/dashboard.html')

@app.route('/manager/create-ticket')
def manager_create_ticket():
    session['username'] = 'manager'
    return render_template('manager/create_ticket.html')

@app.route('/support/helpdesk')
def support_helpdesk():
    session['username'] = 'support'
    return render_template('support/helpdesk.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
