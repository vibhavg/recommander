from flask import *
import json
app = Flask(__name__)

movies = [
    {'name': 'Gravity',
     'poster': 'http://www.thecoolector.com/wp-content/uploads/2013/07/gravity-poster.jpg'},
    {'name': 'Star Trek Into Darkness',
     'poster': 'http://oyster.ignimgs.com/wordpress/stg.ign.com/2012/12/star-trek-into-darkness-teaser-poster1-610x903.jpg'}
]

books = [
    {'name': 'The Hunger Games',
     'poster': 'http://upload.wikimedia.org/wikipedia/en/a/ab/Hunger_games.jpg'},
    {'name': 'Ender\'s Game',
     'poster': 'http://media.npr.org/assets/bakertaylor/covers/e/enders-game/9780812550702_custom-14b6b3e2b8be027acc868fa0aba0670be8900168-s6-c30.jpg'}
]

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def index():
    if 'key' in session:
        pass

    return render_template('index.jinja2', movies=movies, books=books)

@app.route('/token')
def token():
    if not 'key' in session:
        session['key'] = request.args.get('key', '')
        return json.dumps({'refresh': True})
    else:
        return json.dumps({'refresh': False})

if __name__ == "__main__":
    app.run(debug=True)
