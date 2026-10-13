import json, os, threading, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT=int(os.getenv('PORT','8080'))
APP_VERSION=os.getenv('APP_VERSION','v1')
lock=threading.Lock()
tasks=[{'id':'demo-1','title':'Deploy the app to Kubernetes','done':False,'created_at':'demo'}]
INDEX='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kubernetes TaskBoard</title><style>body{font:16px system-ui;background:#f4f7fb;color:#17253d;margin:0}main{max-width:760px;margin:50px auto;padding:24px}section{background:white;border-radius:16px;padding:28px;box-shadow:0 5px 24px #dce4ee}h1{margin-top:0}form{display:flex;gap:10px}input{flex:1;padding:13px;border:1px solid #c8d3e0;border-radius:8px;font:inherit}button{border:0;border-radius:8px;padding:12px 16px;background:#2459d3;color:white;cursor:pointer}li{display:flex;align-items:center;gap:12px;border-bottom:1px solid #eee;padding:14px 0}li span{flex:1}li.done span{text-decoration:line-through;color:#888}li button{background:#a53642}small{color:#67788e}#error{color:#b02d36}</style></head><body><main><section><h1>☸ Kubernetes TaskBoard</h1><p>Practice a real task API on Kubernetes. Add, complete, and delete tasks.</p><form id="f"><input id="title" placeholder="Enter a task" required maxlength="120"><button>Add task</button></form><p id="error" role="alert"></p><ul id="list" style="padding:0;list-style:none"></ul><small id="meta"></small></section></main><script>const list=document.getElementById('list'),err=document.getElementById('error');async function request(url,opts){const r=await fetch(url,opts);const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');return d}async function refresh(){try{const d=await request('/api/tasks');list.replaceChildren();for(const t of d.tasks){const li=document.createElement('li');if(t.done)li.className='done';const cb=document.createElement('input');cb.type='checkbox';cb.checked=t.done;cb.onchange=async()=>{await request('/api/tasks/'+encodeURIComponent(t.id),{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({done:cb.checked})});refresh()};const span=document.createElement('span');span.textContent=t.title;const del=document.createElement('button');del.textContent='Delete';del.onclick=async()=>{await request('/api/tasks/'+encodeURIComponent(t.id),{method:'DELETE'});refresh()};li.append(cb,span,del);list.append(li)}document.getElementById('meta').textContent=d.count+' task(s) • '+d.version+' • pod: '+d.hostname;err.textContent=''}catch(e){err.textContent=e.message}}document.getElementById('f').onsubmit=async e=>{e.preventDefault();try{await request('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:document.getElementById('title').value})});document.getElementById('title').value='';refresh()}catch(x){err.textContent=x.message}};refresh()</script></body></html>'''
class Handler(BaseHTTPRequestHandler):
 def respond(self,status,data,content_type='application/json; charset=utf-8'):
  body=(json.dumps(data).encode() if not isinstance(data,bytes) else data)
  self.send_response(status);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def payload(self):
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>4096 or n<1:raise ValueError('Body must be 1–4096 bytes')
   obj=json.loads(self.rfile.read(n));
   if not isinstance(obj,dict):raise ValueError('JSON object required')
   return obj
  except (ValueError,json.JSONDecodeError) as e:raise ValueError(str(e))
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/':return self.respond(200,INDEX.encode(),'text/html; charset=utf-8')
  if p in ('/health','/ready') :return self.respond(200,{'status':'UP','version':APP_VERSION})
  if p=='/api/tasks':
   with lock: snapshot=[dict(t) for t in tasks]
   return self.respond(200,{'tasks':snapshot,'count':len(snapshot),'version':APP_VERSION,'hostname':os.getenv('HOSTNAME','local')})
  return self.respond(404,{'error':'Not found'})
 def do_POST(self):
  if urlparse(self.path).path!='/api/tasks':return self.respond(404,{'error':'Not found'})
  try:
   data=self.payload();title=data.get('title')
   if not isinstance(title,str) or not 1<=len(title.strip())<=120:raise ValueError('title must contain 1–120 characters')
  except ValueError as e:return self.respond(400,{'error':str(e)})
  task={'id':str(uuid.uuid4()),'title':title.strip(),'done':False,'created_at':datetime.now(timezone.utc).isoformat()}
  with lock:tasks.append(task)
  return self.respond(201,task)
 def do_PATCH(self):
  p=urlparse(self.path).path
  if not p.startswith('/api/tasks/'):return self.respond(404,{'error':'Not found'})
  try:
   data=self.payload()
   if type(data.get('done')) is not bool:raise ValueError('done must be true or false')
  except ValueError as e:return self.respond(400,{'error':str(e)})
  with lock:
   for t in tasks:
    if t['id']==p.rsplit('/',1)[-1]:t['done']=data['done'];return self.respond(200,dict(t))
  return self.respond(404,{'error':'Task not found'})
 def do_DELETE(self):
  p=urlparse(self.path).path
  if not p.startswith('/api/tasks/'):return self.respond(404,{'error':'Not found'})
  with lock:
   for i,t in enumerate(tasks):
    if t['id']==p.rsplit('/',1)[-1]:tasks.pop(i);return self.respond(200,{'deleted':True})
  return self.respond(404,{'error':'Task not found'})
if __name__=='__main__':
 print(f'TaskBoard {APP_VERSION} listening on {PORT}',flush=True)
 ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
