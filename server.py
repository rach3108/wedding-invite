#!/usr/bin/env python3
"""
Wedding RSVP Backend Server
Stores RSVPs in a JSON file and serves the invitation + admin dashboard.
"""

import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

RSVP_FILE = os.path.join(os.path.dirname(__file__), 'rsvps.json')


def load_rsvps():
    if not os.path.exists(RSVP_FILE):
        return []
    with open(RSVP_FILE, 'r') as f:
        return json.load(f)


def save_rsvps(rsvps):
    with open(RSVP_FILE, 'w') as f:
        json.dump(rsvps, f, indent=2)


# ─── Submit RSVP ─────────────────────────────────────────────────────────────
@app.route('/api/rsvp', methods=['POST'])
def submit_rsvp():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    attendance = data.get('attendance', '').strip()
    notes = data.get('notes', '').strip()

    if not name or not attendance:
        return jsonify({'error': 'Name and attendance are required'}), 400

    rsvps = load_rsvps()
    entry = {
        'id': len(rsvps) + 1,
        'name': name,
        'email': email,
        'attendance': attendance,
        'notes': notes,
        'submitted_at': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    rsvps.append(entry)
    save_rsvps(rsvps)

    return jsonify({'success': True, 'message': 'RSVP received!'})


# ─── Admin: get all RSVPs ─────────────────────────────────────────────────────
@app.route('/api/rsvps', methods=['GET'])
def get_rsvps():
    rsvps = load_rsvps()
    accepting = [r for r in rsvps if r['attendance'] == 'accepts']
    declining = [r for r in rsvps if r['attendance'] == 'declines']
    return jsonify({
        'total_responses': len(rsvps),
        'accepting': len(accepting),
        'declining': len(declining),
        'rsvps': rsvps
    })


# ─── Serve static files ───────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/rsvp')
def rsvp_page():
    return send_from_directory('.', 'rsvp.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
