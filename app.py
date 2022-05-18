from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h2>Hello World 2</h2>'


if __name__ == '__main__':
   app.run("127.0.0.1",5050,debug=True)








