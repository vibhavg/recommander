from flask import *
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode
from collections import defaultdict
import urllib
import json
import facebook
import sys
import os
import sqlite3
import operator

app = Flask(__name__)

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

    movie_data = response['results'][0]
    try:
        request = Request('http://api.themoviedb.org/3/movie/%s?%s' % (movie_data['id'], urlencode(args)), headers=HEADERS)
        response = json.loads(urlopen(request).read())
    except:
        return empty

    poster = movie_data['poster_path']
    release_date = movie_data['release_date'][:4]
    genres = map(operator.itemgetter('name'), response['genres'])
    return empty if poster is None else {'poster': CONFIG['images']['base_url'] + 'w154' + poster, 
                                         'id': movie_data['id'], 
                                         'release_date': release_date,
                                         'genres': genres}

@app.route('/')
def index():
    if not 'key' in session:
        return render_template('index.jinja2', movies=[])

    print 'key: %s' % session['key']

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
        return render_template('index.jinja2', movies=[])

    print 'Connected!'

    query = cursor.execute('SELECT * FROM movies WHERE uid = ?', [profile['id']])
    count = 0
    for row in query:
        count += 1

    if (count <= 0):
        print "Querying movies..."
        queryMutual = "select mutual_friend_count,uid,movies from user where uid in \
            (select uid2 from friend where uid1=me()) order by mutual_friend_count desc LIMIT 100"
        params = urllib.urlencode({'q':queryMutual, 'access_token':session['key'] })

        url = "https://graph.facebook.com/fql?" + params
        data = json.loads(urllib.urlopen(url).read())["data"]

        params = urllib.urlencode({'access_token':session['key'] })
        url = "https://graph.facebook.com/me/movies?" + params
        yourdata = json.load(urllib.urlopen(url))
        yourmovies = set([movie['name'] for movie in yourdata['data'] if movie['category']=='Movie'])

        friendWeight = {}
        numFriends = len(friend_list)
        movieWeightConstant = 2
        for friend in data:
            friendsMovies = set(friend['movies'].split(', '))
            numCommon = len(friendsMovies.intersection(yourmovies))
            numTotal = len(friendsMovies.union(yourmovies))
            friendWeight[friend['uid']] = movieWeightConstant * float(numCommon)/(numTotal+1)
            friendWeight[friend['uid']] += float(friend['mutual_friend_count'])/numFriends

        movieRatings = defaultdict(int)
        for friend in data:
            for movie in friend['movies'].split(', '):
                if movie not in yourmovies:
                    movieRatings[movie] += friendWeight[friend['uid']]

        movieRatingsList = [(i, movieRatings[i]) for i in movieRatings.keys()]
        movie_list = sorted(movieRatingsList, key=lambda movieRatingsList: movieRatingsList[1])[::-1]
        movie_list = [name for (name,rating) in movie_list]

        movie_list = movie_list[:75]
        movie_list_final = []
        for movie in movie_list:
            info = get_info(movie)
            if info['poster'] != '':
                if not info['release_date'] > 1930:
                    info['release_date'] = 2000
                movie_list_final.append((movieRatings[movie],movie,info['poster'],info['id'],info['release_date'],info['genres']))

        movie_list = movie_list_final
        cursor.execute('INSERT INTO movies VALUES (?, ?)', (profile['id'], json.dumps(movie_list)))
        db.commit()

    query = cursor.execute('SELECT * FROM movies WHERE uid = "%s"' % profile['id'])
    loadedMovies = map(lambda pair: {'name': pair[1], 'poster': pair[2], 'year': pair[4], 
                                     'rating': pair[0], 'genres': json.dumps(pair[5]), 'url': 'http://themoviedb.org/movie/' + str(pair[3])}, 
                       json.loads(query.fetchone()[1]))
    return render_template('index.jinja2', movies=loadedMovies)

@app.route('/token')
def token():
    key = request.args.get('key', '')
    if not 'key' in session: #or key != session['key']:
        session['key'] = key
        return json.dumps({'refresh': True})
    else:
        return json.dumps({'refresh': False})

if __name__ == "__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
    #app.run(debug=True)

