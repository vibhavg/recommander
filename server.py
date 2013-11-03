from flask import *
import json
import facebook
import sys
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
    #if 'key' in session:
    if True:
        try:
            graph = facebook.GraphAPI(session['key'])
            friends = graph.get_connections("me", "friends")
            friend_list = [friend['id'] for friend in friends['data']]

        except facebook.GraphAPIError:
            session.pop('key')
            return render_template('index.jinja2', movies=movies, books=books)

        #if not 'movies' in session:
        if True:
            movie_counts = dict()
            for i in xrange(1, len(friend_list) / 50):
                batch = []
                for friend in friend_list[((i - 1) * 50):(i * 50)]:
                    batch.append({'method': 'GET', 'relative_url': friend + '/movies'})
                    
                result = graph.request("", post_args={"batch": json.dumps(batch)})
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
                movie_list.append((movie_counts[movie], movie))
            movie_list = sorted(movie_list, key=lambda movie_list: movie_list[0])[::-1]
            print movie_list
            session['movies'] = movie_list
    
    return render_template('index.jinja2', movies=movies, books=books)

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
