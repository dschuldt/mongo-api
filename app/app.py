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

@post('/api/v1/kpi/<id>')
def insert_doc(id):
  document = request.json
  document['_id'] = id
  try:
    collection.insert_one(document).inserted_id
  except Exception as e:
    print('MongoDB connection error: {}'.format(e))
    response.content_type = 'application/json'
    return dumps({"error":"an error occurred during insert"})
  try:
    wsocket = get_wsocket()    
    wsocket.send(get_doc())
  except Exception as e:
    print("no websocket connection established")  
  response.content_type = 'application/json'
  return dumps({"id":id})

@get('/api/v1/kpi/<id>')
def get_doc(id):
  if (request.query.callback):
    response.content_type = "application/javascript"
    return dumps('{}({})'.format(request.query.callback, collection.find_one({"_id": id}))).strip('\"')
  else:
    response.content_type = 'application/json'
  return dumps(collection.find_one({"_id": id}))

@get('/api/v1/kpi/latest', name="kpi_latest")
def get_doc():
  response.content_type = 'application/json'
  return dumps(collection.find_one(sort=[('_id', pymongo.DESCENDING )]))


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
