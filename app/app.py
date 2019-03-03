import bottle, pymongo, json, copy
from bottle import get, post, request, response, template, static_file
from pymongo import MongoClient
from bson.json_util import dumps
from gevent import pywsgi
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

app = bottle.default_app()
mongo_host = "mongodb"
mongo_port = 27017
mongo_user = "root"
mongo_pass = "example"

def set_wsocket(ws):
  global wsocket
  wsocket = ws

def get_wsocket():
  global wsocket
  return wsocket  

client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_pass)
db = client['portals']
collection = db['kpis']

def route_url(route_name):
  return '{}://{}{}'.format(request.urlparts.scheme, request.urlparts.netloc, app.get_url(route_name))

@get('/static/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root='static')

@get('/api/v1/ping')
def ping():
  response.content_type = 'text/plain'
  return 'ok'

@get('/api/v1/info')
def info():
  response.content_type = 'application/json'
  return dumps(client.server_info(), indent=4)

@post('/api/v1/kpi')
def insert_doc():
  document = request.json
  #document['_id'] = id
  try:
    id = '{}'.format(collection.insert_one(document).inserted_id)
  except Exception as e:
    print('MongoDB connection error: {}'.format(e))
  try:
    wsocket = get_wsocket()    
    wsocket.send(get_doc())
  except Exception as e:
    print("no websocket connection established")  
  response.content_type = 'application/json'
  return dumps({"id":id})

@get('/api/v1/kpi/<id>')
def get_doc(id):
  response.content_type = 'application/json'
  return dumps('{}'.format(collection.find_one({"_id": id})), indent=4)

@get('/api/v1/kpi/latest', name="kpi_latest")
def get_doc():
  response.content_type = 'application/json'
  return dumps(collection.find_one(sort=[('_id', pymongo.DESCENDING )]), indent=4)


@get('/dashboard')
def dashboard():
  data = json.loads(get_doc())
  response.content_type = 'text/html; charset=UTF8'
  return template('dashboard', data=data)


@get('/websocket')
def handle_websocket():
  wsock = request.environ.get('wsgi.websocket')
  if not wsock:
    abort(400, 'Expected WebSocket request.')      
  set_wsocket(wsock)
  while True:
    try:
      wsock.receive()
    except WebSocketError:
      break
