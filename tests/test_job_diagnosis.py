import unittest
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class JobDiagnosisTests(unittest.TestCase):
    def run_node(self, code):
        result = subprocess.run(["node", "--input-type=module", "-e", code], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_answer_combinations_have_five_unique_results(self):
        self.run_node("""
          import assert from 'node:assert/strict';
          import { questions, jobProfiles, rankJobs } from './src/lib/job-diagnosis.mjs';
          assert.equal(questions.length,10);
          assert.ok(jobProfiles.length>=5);
          for(let k=0;k<3;k++){
            const answers=questions.map(q=>Math.min(k,q.options.length-1));
            const result=rankJobs(answers);
            assert.equal(result.length,jobProfiles.length);
            assert.equal(new Set(result.map(x=>x.id)).size,jobProfiles.length);
            assert.ok(result.every(x=>Number.isFinite(x.score)&&x.reason&&x.link.startsWith('/')));
            assert.ok(result.every((x,i)=>i===0||result[i-1].score>=x.score));
            assert.deepEqual(result,rankJobs(answers));
          }
        """)

    def test_bad_input_is_rejected(self):
        self.run_node("""
          import assert from 'node:assert/strict';
          import {rankJobs} from './src/lib/job-diagnosis.mjs';
          assert.throws(()=>rankJobs([]));
          assert.throws(()=>rankJobs(Array(10).fill(999)));
          assert.throws(()=>rankJobs(Array(10).fill(0).map((x,i)=>i===0?NaN:x)));
        """)

    def test_linked_articles_exist(self):
        self.run_node("""
          import assert from 'node:assert/strict';
          import {existsSync} from 'node:fs';
          import {jobProfiles} from './src/lib/job-diagnosis.mjs';
          for(const job of jobProfiles){
            const base='src/pages'+job.link.slice(0,-1);
            assert.ok(existsSync(base+'.md')||existsSync(base+'.astro')||existsSync(base+'/index.astro'),job.link);
          }
        """)

if __name__ == '__main__':
    unittest.main()
