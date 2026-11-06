// Editorial self-check to organize concerns. It does not determine legal violations.
export const checkQuestions=[
 {id:'wages',category:'賃金',question:'働いた時間の賃金が支払われていないことがある',hint:'準備・片付けの時間なども含め、実際に働いた時間を確認。',weight:4,urgent:true,action:'給与明細と勤務記録、作業の指示を保存し、公的な相談窓口へ。'},
 {id:'break',category:'休憩',question:'6時間を超えて働いても必要な休憩が取れない',hint:'原則として6時間超で45分、8時間超で60分以上の休憩が必要です。',weight:4,urgent:true,action:'実働時間と休憩時間を記録し、相談先へ確認しましょう。'},
 {id:'clock',category:'労働時間',question:'打刻前・打刻後の作業を求められ、勤務時間に反映されない',hint:'指示された作業の内容や実態が重要です。',weight:4,urgent:true,action:'作業内容と開始・終了時刻を記録しましょう。'},
 {id:'schedule',category:'シフト',question:'希望しないシフトを断りづらく、生活に支障が出ている',hint:'契約上の勤務日・時間との違いを確認しましょう。',weight:2,urgent:false,action:'雇用契約書とシフト表、変更の連絡を見比べましょう。'},
 {id:'verbal',category:'人間関係',question:'暴言や侮辱、威圧的な言動が繰り返される',hint:'ハラスメントに該当するかは具体的な状況によります。',weight:4,urgent:true,action:'日時や内容をメモし、社内外の相談先を使いましょう。'},
 {id:'hazard',category:'安全',question:'安全な手順や説明のない危険な作業を任される',hint:'けがのおそれがある場合は安全を最優先してください。',weight:4,urgent:true,action:'危険を避け、状況を記録して安全管理担当者や窓口へ相談。'},
 {id:'terms',category:'労働条件',question:'賃金・仕事内容・勤務場所などの条件がはっきり示されない',hint:'書面等での労働条件の明示が重要です。',weight:3,urgent:false,action:'労働条件通知書を確認し、不明点を具体的に聞きましょう。'},
 {id:'deductions',category:'賃金',question:'ミスなどの費用を説明なく一方的に給与から引かれた',hint:'賃金控除には法令上のルールがあります。',weight:4,urgent:true,action:'給与明細と控除内容の説明を保存して相談しましょう。'},
 {id:'resignation',category:'退職',question:'辞めたいと伝えると罰金や脅しを理由に引き止められる',hint:'退職の扱いは契約形態等によっても異なります。',weight:4,urgent:true,action:'契約書とやりとりを保管し、専門窓口に相談しましょう。'},
 {id:'support',category:'相談',question:'職場の問題を安心して相談できない',hint:'職場で相談できない場合は外部の公的窓口もあります。',weight:2,urgent:false,action:'職場外の公的な窓口に事情を整理して相談しましょう。'}
];
export function evaluateWorkplace(answers){
 if(!Array.isArray(answers)||answers.length!==checkQuestions.length||
    answers.some(a=>!['yes','no','unknown'].includes(a)))throw new RangeError('不正または未完了の回答');
 const flags=checkQuestions.filter((q,i)=>answers[i]==='yes');
 const unknowns=checkQuestions.filter((q,i)=>answers[i]==='unknown');
 const urgentFlags=flags.filter(q=>q.urgent);
 const score=flags.reduce((s,q)=>s+q.weight,0);
 const level=urgentFlags.length?'consult':flags.length>=3?'review':flags.length?'notice':'none';
 const titles={consult:'早めに相談先を確認したい状況です',review:'働く条件や対応を確認しましょう',notice:'気になる点を記録して確認しましょう',none:'今回の回答で選ばれた懸念事項はありません'};
 return {level,title:titles[level],score,flags,unknowns,urgentFlags};
}
