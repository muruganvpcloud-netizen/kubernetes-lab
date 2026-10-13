import json, subprocess, sys, time, unittest, urllib.request, urllib.error
from pathlib import Path
class APITest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve().parents[1]/'app/server.py')],env=__import__('os').environ|{'PORT':'18080'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(40):
   try:urllib.request.urlopen('http://127.0.0.1:18080/health',timeout=.2);break
   except Exception:time.sleep(.1)
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait(timeout=5)
 def req(self,path,method='GET',data=None):
  raw=json.dumps(data).encode() if data is not None else None
  r=urllib.request.Request('http://127.0.0.1:18080'+path,data=raw,method=method,headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(r) as res:return res.status,json.load(res)
 def test_health(self):self.assertEqual(self.req('/health')[1]['status'],'UP')
 def test_crud(self):
  status,item=self.req('/api/tasks','POST',{'title':'Test Kubernetes'});self.assertEqual(status,201)
  id=item['id'];self.assertFalse(item['done'])
  self.assertTrue(any(t['id']==id for t in self.req('/api/tasks')[1]['tasks']))
  self.assertTrue(self.req('/api/tasks/'+id,'PATCH',{'done':True})[1]['done'])
  self.assertTrue(self.req('/api/tasks/'+id,'DELETE')[1]['deleted'])
  self.assertFalse(any(t['id']==id for t in self.req('/api/tasks')[1]['tasks']))
 def test_invalid_title(self):
  with self.assertRaises(urllib.error.HTTPError) as ctx:self.req('/api/tasks','POST',{'title':' '})
  self.assertEqual(ctx.exception.code,400)
if __name__=='__main__':unittest.main()
