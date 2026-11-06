import unittest
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorkplaceCheckTests(unittest.TestCase):
    def execute(self,js):
        p=subprocess.run(["node","--input-type=module","-e",js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def test_complete_and_safe_defaults(self):
        self.execute("""
        import assert from 'node:assert/strict';
        import {checkQuestions,evaluateWorkplace} from './src/lib/workplace-check.mjs';
        assert.equal(checkQuestions.length,10);
        assert.equal(new Set(checkQuestions.map(q=>q.id)).size,10);
        const r=evaluateWorkplace(Array(10).fill('no'));
        assert.equal(r.level,'none');
        assert.equal(r.flags.length,0);
        assert.equal(r.unknowns.length,0);
        """)
    def test_single_serious_concern_triggers_consult(self):
        self.execute("""
        import assert from 'node:assert/strict';
        import {evaluateWorkplace} from './src/lib/workplace-check.mjs';
        const answers=Array(10).fill('no');answers[0]='yes';
        const r=evaluateWorkplace(answers);
        assert.equal(r.level,'consult');
        assert.equal(r.urgentFlags.length,1);
        const other=Array(10).fill('unknown');
        assert.equal(evaluateWorkplace(other).unknowns.length,10);
        """)
    def test_invalid_answers_fail(self):
        self.execute("""
        import assert from 'node:assert/strict';
        import {evaluateWorkplace} from './src/lib/workplace-check.mjs';
        for(const a of [[],null,Array(10).fill('maybe'),Array(9).fill('no')]) assert.throws(()=>evaluateWorkplace(a));
        """)
if __name__=='__main__':unittest.main()
