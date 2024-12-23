from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = 'some_secret_key_for_sessions'

DEVICES_FILE = 'devices.json'

# A simple user store for demonstration.
USERS = {
    'admin': 'password123'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("You must be logged in to view this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_devices():
    if not os.path.exists(DEVICES_FILE):
        return []
    with open(DEVICES_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            # Redirect to landing page with some default device parameters
            return redirect(url_for('landing', deviceIP='192.168.1.10', deviceType='relay', channel='0'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/landing/<deviceIP>/<deviceType>/<channel>')
@login_required
def landing(deviceIP, deviceType, channel):
    devices = load_devices()
    return render_template('landing.html', deviceIP=deviceIP, deviceType=deviceType, channel=channel, devices=devices)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        device_ip = request.form.get('device_ip')
        device_type = request.form.get('device_type')
        device_channel = request.form.get('device_channel')

        devices = load_devices()
        devices.append({
            'name': device_name,
            'ip': device_ip,
            'type': device_type,
            'channel': device_channel
        })
        save_devices(devices)

        flash('Device added successfully!')
        return redirect(url_for('landing', deviceIP=device_ip, deviceType=device_type, channel=device_channel))
    return render_template('add.html')

@app.route('/edit/<device_ip>', methods=['GET', 'POST'])
@login_required
def edit(device_ip):
    devices = load_devices()
    device = next((d for d in devices if d['ip'] == device_ip), None)
    if not device:
        flash('Device not found.')
        return redirect(url_for('landing', deviceIP='192.168.1.10', deviceType='relay', channel='0'))

    if request.method == 'POST':
        new_name = request.form.get('device_name')
        new_ip = request.form.get('device_ip')
        new_type = request.form.get('device_type')
        new_channel = request.form.get('device_channel')

        # Update the device
        device['name'] = new_name
        device['ip'] = new_ip
        device['type'] = new_type
        device['channel'] = new_channel

        save_devices(devices)
        flash('Device updated successfully!')
        return redirect(url_for('landing', deviceIP=new_ip, deviceType=new_type, channel=new_channel))

    return render_template('edit.html', device=device)

if __name__ == '__main__':
    # If you have certificates:
    # app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

