import unittest
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class IncomeCalculatorTests(unittest.TestCase):
    def run_js(self, source):
        completed=subprocess.run(["node","--input-type=module","-e",source],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)

    def test_default_weekly_monthly_and_annual(self):
        self.run_js("""
          import assert from 'node:assert/strict';
          import {calculateIncome,defaults} from './src/lib/income-calculator.mjs';
          const x=calculateIncome(defaults);
          assert.equal(x.monthlyWages,78000);
          assert.equal(x.annualWages,936000);
          assert.equal(x.shiftsPerMonth,13);
          assert.equal(x.monthlyHours,65);
          assert.equal(x.estimatedRemainder,78000);
          const y=calculateIncome({...defaults,mode:'monthly',shifts:12});
          assert.equal(y.monthlyWages,72000);
          assert.equal(y.annualWages,864000);
          assert.equal(y.shiftsPerMonth,12);
        """)

    def test_breaks_fares_costs_and_manual_deductions(self):
        self.run_js("""
          import assert from 'node:assert/strict';
          import {calculateIncome,defaults} from './src/lib/income-calculator.mjs';
          const x=calculateIncome({...defaults,mode:'monthly',shifts:10,hours:6,breakMinutes:30,farePerShift:300,costPerShift:100,monthlyDeductions:2000});
          assert.equal(x.paidHours,5.5);
          assert.equal(x.monthlyWages,66000);
          assert.equal(x.monthlyFare,3000);
          assert.equal(x.monthlyCosts,1000);
          assert.equal(x.estimatedRemainder,66000);
        """)

    def test_errors_and_edge_values(self):
        self.run_js("""
          import assert from 'node:assert/strict';
          import {calculateIncome,defaults} from './src/lib/income-calculator.mjs';
          for(const edits of [{hourlyYen:0},{hours:-1},{shifts:8},{breakMinutes:300},{hourlyYen:Infinity},{hours:NaN},{mode:'none'},{monthlyDeductions:-1},{costPerShift:''}]){
            assert.throws(()=>calculateIncome({...defaults,...edits}), JSON.stringify(edits));
          }
          const ok=calculateIncome({...defaults,hours:8,breakMinutes:60,shifts:7});
          assert.equal(ok.paidHours,7);
          assert.equal(ok.monthlyHours,7*7*52/12);
          assert.ok(Number.isInteger(ok.monthlyWages));
        """)

if __name__=="__main__":
    unittest.main()
