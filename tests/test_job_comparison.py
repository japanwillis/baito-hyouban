import unittest
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class JobComparisonTests(unittest.TestCase):
    def js(self, source):
        p=subprocess.run(["node","--input-type=module","-e",source],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_two_and_three_distinct_jobs(self):
        self.js("""
          import assert from 'node:assert/strict';
          import {comparisonJobs,comparisonFields,selectComparison} from './src/lib/job-comparison.mjs';
          assert.ok(comparisonJobs.length>=9);
          assert.equal(new Set(comparisonJobs.map(j=>j.id)).size,comparisonJobs.length);
          assert.equal(selectComparison(['cafe','convenience']).length,2);
          const selection=selectComparison(['warehouse','cafe','office']);
          assert.deepEqual(selection.map(j=>j.id),['warehouse','cafe','office']);
          assert.ok(selection.every(job=>comparisonFields.every(field=>typeof job[field.key]==='string'&&job[field.key].length>5)));
        """)

    def test_invalid_selection_rejected(self):
        self.js("""
          import assert from 'node:assert/strict';
          import {selectComparison} from './src/lib/job-comparison.mjs';
          for(const ids of [[],['cafe'],['cafe','cafe'],['bad','cafe'],['cafe','office','warehouse','event'],null,'cafe']){
            assert.throws(()=>selectComparison(ids));
          }
        """)

    def test_article_links_exist(self):
        self.js("""
          import assert from 'node:assert/strict';
          import {existsSync} from 'node:fs';
          import {comparisonJobs} from './src/lib/job-comparison.mjs';
          for(const job of comparisonJobs){
            assert.ok(job.link.startsWith('/'));
            const base='src/pages'+job.link.slice(0,-1);
            assert.ok(existsSync(base+'.md')||existsSync(base+'.astro')||existsSync(base+'/index.astro'),job.id);
          }
        """)

if __name__=='__main__':
    unittest.main()
