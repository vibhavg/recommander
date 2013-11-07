from flask import *
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode
import json
import facebook
import sys
import sqlite3
app = Flask(__name__)

books = [
    {'name': 'The Hunger Games',
     'poster': 'http://upload.wikimedia.org/wikipedia/en/a/ab/Hunger_games.jpg'},
    {'name': 'Ender\'s Game',
     'poster': 'http://media.npr.org/assets/bakertaylor/covers/e/enders-game/9780812550702_custom-14b6b3e2b8be027acc868fa0aba0670be8900168-s6-c30.jpg'}
]

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
MOVIEDB_KEY = '46a4fa7499a15b994b2bd72515a07315'
HEADERS = {'Accept': 'application/json'}

configRequest = Request('http://api.themoviedb.org/3/configuration?api_key=%s' % (MOVIEDB_KEY))
CONFIG = json.loads(urlopen(configRequest).read())

def get_info(name):
    args = {'api_key': MOVIEDB_KEY, 'query': name}
    empty = {'poster': ''}
    try:
        request = Request('http://api.themoviedb.org/3/search/movie?' + urlencode(args), headers=HEADERS)
        response = json.loads(urlopen(request).read())
    except:
        return empty
    if response['total_results'] == 0:
        return empty

    poster = response['results'][0]['poster_path']
    return empty if poster is None else {'poster': CONFIG['images']['base_url'] + 'w154' + poster, 'id': response['results'][0]['id']}

@app.route('/')
def index():
    if not 'key' in session:
        return render_template('index.jinja2', movies=movies, books=books)

    db = sqlite3.connect('movies.db')
    cursor = db.cursor()

    print 'Connecting to Graph API...'
    try:
        graph = facebook.GraphAPI(session['key'])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")
        friend_list = [friend['id'] for friend in friends['data']]
        
    except facebook.GraphAPIError:
        print 'Key failure :('

        session.pop('key')
        return render_template('index.jinja2', movies=movies, books=books)
        
    print 'Connected!'

    query = cursor.execute('SELECT * FROM movies WHERE id = ?', [profile['id']])
    count = 0
    for row in query:
        count += 1

    if count <= 0:
        print 'Querying movies.'

        movie_counts = dict()
        for i in xrange(1, len(friend_list) / 50):
            batch = []
            for friend in friend_list[((i - 1) * 50):(i * 50)]:
                batch.append({'method': 'GET', 'relative_url': friend + '/movies'})
                
            result = graph.request("", post_args={"batch": json.dumps(batch)})[:5]
            for res in result:
                friend_movies = json.loads(res['body'])['data']
                for friend_movie in friend_movies:
                    friend_movie_name = friend_movie['name']
                    if friend_movie_name in movie_counts:
                        movie_counts[friend_movie_name] += 1
                    else:
                        movie_counts[friend_movie_name] = 1
        movie_list = []
        for movie in movie_counts.keys():
            info = get_info(movie)
            if info['poster'] == '':
                continue
            movie_list.append((movie_counts[movie], movie, info['poster'], info['id']))
        movie_list = sorted(movie_list, key=lambda movie_list: movie_list[0])[::-1]
        
        print movie_list
        cursor.execute('INSERT INTO movies VALUES (?, ?)', (profile['id'], json.dumps(movie_list)))
        db.commit()
        

    query = cursor.execute('SELECT * FROM movies WHERE id = "%s"' % profile['id'])
    loadedMovies = map(lambda pair: {'name': pair[1], 'poster': pair[2]}, json.loads(query.fetchone()[1]))
    return render_template('index.jinja2', movies=loadedMovies, books=books)

@app.route('/token')
def token():
    key = request.args.get('key', '')
    if not 'key' in session or key != session['key']:
        session['key'] = key
        return json.dumps({'refresh': True})
    else:
        return json.dumps({'refresh': False})

if __name__ == "__main__":
    app.run(debug=True)
