from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    try:
        return render_template("iam_viewer_connected.html")
    except Exception as e:
        return f"Error loading template: {str(e)}"

@app.route('/test')
def test():
    return jsonify({"status": "OK", "message": "Server running"})

if __name__ == '__main__':
    print("Starting simple server...")
    app.run(host='127.0.0.1', port=5000, debug=True)
