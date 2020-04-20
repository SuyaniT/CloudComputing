from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from pprint import pprint
import json
import requests

cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()
app = Flask(__name__)

@app.route('/')
def hello():
	name = request.args.get("name")
	return ('<h1>Hello, {}, check out the top 100 songs!</h1>'.format(name))

@app.route('/top100', methods=['GET'])
def top100():
	rows = session.execute("""Select * From top100.stats""")
	results=[]

	for r in rows:
		results.append({"title":r.title,"artist":r.artist})
	return jsonify(results)

@app.route('/popular', methods=['GET'])
def popular():
	rows = session.execute("""SELECT * FROM top100.stats WHERE popularity>75 ALLOW FILTERING""")
	results=[]

	for r in rows:
		results.append({"title":r.title,"artist":r.artist})
	return jsonify(results)

@app.route('/top100/<year>', methods=['GET'])
def pick_year(year):
	rows = session.execute("""SELECT * FROM top100.stats where year={} ALLOW FILTERING""".format(year))

	for r in rows:
		return('<h1>{} was released in {}!</h1>'.format(r.title,year))

	return('<h1>No songs of that year in database.</h1>')

@app.route('/top100/genre/<title>', methods=['GET'])
def find_genre(title):
	rows = session.execute("""SELECT * FROM top100.stats where title='{}' ALLOW FILTERING""".format(title))

	for r in rows:
		return('<h1>{} is of the genre <em>{}</em>!</h1>'.format(title,r.genre))

	return('<h1>That song is not in the database.</h1>')

@app.route('/lyrics/', methods=['GET'])
def lyrics():
	lyric_url_template = 'https://lyric-api.herokuapp.com/api/find/{artist}/{title}'

	my_artist = 'John Lennon'
	my_song = 'Imagine'

	lyric_url = lyric_url_template.format(artist = my_artist, title = my_song)

	resp = requests.get(lyric_url)
	if resp.ok:
		return resp.json()
	else:
		print(resp.reason)

@app.route('/lyrics/<artist>/<title>', methods=['GET'])
def customlyrics(artist, title):
	lyric_url_template = 'https://lyric-api.herokuapp.com/api/find/{band}/{song}'

	my_artist = artist
	my_song = title

	lyric_url = lyric_url_template.format(band = artist, song = title)

	resp = requests.get(lyric_url)
	if resp.ok:
		return resp.json()
	else:
		print(resp.reason)

@app.route('/top100', methods=['POST'])
def create():
	session.execute("""INSERT INTO top100.stats(title) VALUES ('{}')""".format(request.json['title']))
	return jsonify ({'message':'created: /top100/{}'.format(request.json['title'])})

@app.route('/top100', methods=['DELETE'])
def delete():
	session.execute("""DELETE FROM top100.stats WHERE title='{}'""".format(request.json['title']))
	return jsonify ({'message':'removed: /top100/{}'.format(request.json['title'])})

@app.route('/top100', methods=['PUT'])
def update():
	session.execute("""UPDATE top100.stats SET year={},genre='{}' WHERE title='{}'""".format(int(request.json['year']),request.json['genre'],request.json['title']))
	return jsonify ({'message':'updated: /top100/{}'.format(request.json['title'])})

if __name__=='__main__':
	app.run(host='0.0.0.0',port=80)
