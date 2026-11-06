import unittest
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorryNavigatorTests(unittest.TestCase):
 def js(self,source):
  r=subprocess.run(["node","--input-type=module","-e",source],cwd=ROOT,capture_output=True,text=True,timeout=20)
  self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_search_and_categories(self):
  self.js("""
  import assert from 'node:assert/strict';
  import {worries,worryCategories,filterWorries} from './src/lib/first-job-worries.mjs';
  assert.equal(worries.length,12);
  assert.equal(new Set(worries.map(w=>w.id)).size,12);
  assert.deepEqual(filterWorries().map(x=>x.id),worries.map(x=>x.id));
  assert.ok(filterWorries({query:'面接'}).some(w=>w.id==='interview'));
  assert.ok(filterWorries({query:'シフト'}).some(w=>w.id==='shift'));
  for(const category of worryCategories)assert.ok(filterWorries({category}).length>0);
  assert.throws(()=>filterWorries({category:'invalid'}));
  assert.throws(()=>filterWorries({query:null}));
  """)
 def test_advice_content_and_live_links(self):
  self.js("""
  import assert from 'node:assert/strict';
  import {existsSync} from 'node:fs';
  import {worries} from './src/lib/first-job-worries.mjs';
  for(const w of worries){
   assert.equal(w.steps.length,3,w.id);
   assert.ok(w.steps.every(x=>x.length>=8),w.id);
   assert.ok(w.question.length>=10,w.id);
   assert.ok(w.link.startsWith('/'),w.id);
   const base='src/pages'+w.link.slice(0,-1);
   assert.ok(existsSync(base+'.md')||existsSync(base+'.astro')||existsSync(base+'/index.astro'),w.link);
  }
  """)
if __name__=='__main__':unittest.main()
