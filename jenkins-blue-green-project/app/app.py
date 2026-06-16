from flask import Flask
import os

app = Flask(__name__)
VERSION = os.environ.get('APP_VERSION', '2.0')
COLOR = os.environ.get('APP_COLOR', 'blue')

@app.route('/')
def hello()
    return f"""
    <body style="background-color: {COLOR}; color: white; text-align: center; padding-top: 100px; font-family: sans-serif;">
        <h1>Application Version {VERSION}</h1>
        <p>This is the <strong>{COLOR.upper()}</strong> environment.</p>
    </body>
    """

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
