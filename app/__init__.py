from flask import Flask


app = Flask(__name__, template_folder='static/templates')


if __name__ == '__main__':
    app.run(debug=True)


from app import routes