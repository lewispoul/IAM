#!/usr/bin/env python3

print("Testing basic Python functionality...")

try:
    import sys
    print(f"Python version: {sys.version}")
    
    import flask
    print(f"Flask version: {flask.__version__}")
    
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello World!"
    
    print("Flask app created successfully!")
    print("If you see this, the basic setup works.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
