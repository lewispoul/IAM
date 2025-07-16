#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template("iam_viewer_connected.html")

@app.route('/test')
def test():
    return jsonify({"status": "OK", "message": "Server is running"})

if __name__ == '__main__':
    print("Starting IAM test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
