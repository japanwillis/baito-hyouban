// Editorial heuristic only: transparent preference matching, not a psychometric assessment.
// The scores are not measured job outcomes, hiring prospects, or popularity rankings.
export const jobProfiles = [
 {id:'convenience',name:'コンビニスタッフ',link:'/job/convenience-store-jobs/',check:'レジ・品出し・清掃などの担当範囲と、新人が質問できる人員体制',traits:{people:2,pace:2,movement:1,routine:1,quiet:0,flexible:2,learn:2}},
 {id:'supermarket',name:'スーパーの品出し・販売',link:'/job/',check:'品出しとレジの比率、荷物の重さ、朝・夕方などのシフト',traits:{people:1,pace:1,movement:2,routine:2,quiet:1,flexible:1,learn:1}},
 {id:'cafe',name:'カフェ・飲食店スタッフ',link:'/company/starbucks/',check:'ピーク時の忙しさ、接客と調理の分担、研修時間',traits:{people:3,pace:3,movement:2,routine:0,quiet:0,flexible:1,learn:3}},
 {id:'restaurant',name:'ファミレス・飲食店スタッフ',link:'/company/saizeriya/',check:'ホールとキッチンの募集区分、ランチ・夕食時間の混雑',traits:{people:2,pace:3,movement:2,routine:1,quiet:0,flexible:2,learn:2}},
 {id:'warehouse',name:'倉庫の仕分け・軽作業',link:'/job/',check:'取り扱う荷物の重量、立ち作業の時間、作業ノルマや安全指導',traits:{people:0,pace:2,movement:3,routine:3,quiet:2,flexible:1,learn:1}},
 {id:'cleaning',name:'清掃スタッフ',link:'/job/',check:'清掃場所・使う薬剤、体力負担、一人作業かチーム作業か',traits:{people:0,pace:1,movement:3,routine:3,quiet:3,flexible:1,learn:0}},
 {id:'office',name:'データ入力・事務補助',link:'/guide/part-time-job-choosing/',check:'PCスキルの要件、入力以外の電話対応、募集条件',traits:{people:0,pace:1,movement:0,routine:3,quiet:3,flexible:0,learn:1}},
 {id:'tutor',name:'塾講師・学習サポート',link:'/guide/part-time-job-choosing/',check:'担当学年・科目・採用条件、授業準備や研修時間の賃金',traits:{people:3,pace:1,movement:0,routine:1,quiet:1,flexible:0,learn:3}},
 {id:'event',name:'イベント運営スタッフ',link:'/guide/part-time-job-choosing/',check:'集合場所、長時間の立ち仕事、勤務日と持ち物、移動費',traits:{people:3,pace:3,movement:3,routine:0,quiet:0,flexible:3,learn:1}},
 {id:'stock',name:'書店・雑貨店スタッフ',link:'/guide/part-time-job-choosing/',check:'品出しとレジの割合、繁忙期、取り扱い商品の重さ',traits:{people:2,pace:1,movement:1,routine:2,quiet:1,flexible:1,learn:2}}
];

// Each response adds 0-3 preference points for each dimension.
// All scores start at zero. The same form always yields the same result.
export const questions = [
 {text:'知らない人と話す仕事は、どのくらい好き？',options:[
  {text:'人と話すのは好き',points:{people:3}},
  {text:'必要なら普通にできる',points:{people:2,quiet:1}},
  {text:'できれば会話が少ない方がいい',points:{quiet:3,routine:1}}
 ]},
 {text:'忙しい時間帯に次々と作業するのは？',options:[
  {text:'活気があって楽しそう',points:{pace:3}},
  {text:'慣れれば大丈夫そう',points:{pace:2,routine:1}},
  {text:'落ち着いて進めたい',points:{quiet:2,routine:3}}
 ]},
 {text:'働いている間の体の動かし方は？',options:[
  {text:'たくさん動きたい',points:{movement:3}},
  {text:'立ったり座ったりできるとよい',points:{movement:1,people:1}},
  {text:'なるべく座って作業したい',points:{quiet:2,movement:0}}
 ]},
 {text:'どんな作業を続けやすそう？',options:[
  {text:'毎日違うことがある仕事',points:{pace:2,learn:3}},
  {text:'慣れた手順で進められる仕事',points:{routine:3,quiet:1}},
  {text:'どちらもほどよくある仕事',points:{routine:1,learn:2}}
 ]},
 {text:'覚えることが多い仕事については？',options:[
  {text:'新しいことを覚えるのが好き',points:{learn:3}},
  {text:'少しずつなら覚えたい',points:{learn:2,routine:1}},
  {text:'シンプルな手順から始めたい',points:{routine:3,quiet:1}}
 ]},
 {text:'バイトで特にうれしいのは？',options:[
  {text:'誰かにありがとうと言われる',points:{people:3,learn:1}},
  {text:'作業がきっちり終わる',points:{routine:3,quiet:1}},
  {text:'仲間と協力して達成する',points:{people:2,pace:2,movement:1}}
 ]},
 {text:'希望の勤務スタイルは？',options:[
  {text:'短いシフトや単発も選びたい',points:{flexible:3}},
  {text:'毎週おおむね同じ時間がいい',points:{routine:2,flexible:0}},
  {text:'条件が合えばどちらでもいい',points:{flexible:2,learn:1}}
 ]},
 {text:'職場で集中しやすいのは？',options:[
  {text:'にぎやかな環境',points:{people:2,pace:2}},
  {text:'ある程度人がいる環境',points:{people:1,pace:1,routine:1}},
  {text:'静かな環境',points:{quiet:3,routine:1}}
 ]},
 {text:'誰かに教えたり説明したりすることは？',options:[
  {text:'好き、得意な方',points:{people:3,learn:3}},
  {text:'少しならやってみたい',points:{people:1,learn:2}},
  {text:'説明より手を動かす方が好き',points:{routine:2,movement:2,quiet:1}}
 ]},
 {text:'はじめての仕事で重視するのは？',options:[
  {text:'接客などで経験を広げたい',points:{people:2,learn:3}},
  {text:'体を動かしながら働きたい',points:{movement:3,pace:1}},
  {text:'自分のペースで手順を覚えたい',points:{quiet:2,routine:3}}
 ]}
];

export function rankJobs(answers){
 if(!Array.isArray(answers)||answers.length!==questions.length||answers.some((v,i)=>!Number.isInteger(v)||v<0||v>=questions[i].options.length))throw new Error('Invalid or incomplete answers');
 const pref={people:0,pace:0,movement:0,routine:0,quiet:0,flexible:0,learn:0};
 questions.forEach((q,i)=>Object.entries(q.options[answers[i]].points).forEach(([key,n])=>{pref[key]+=n;}));
 const sum=Object.values(pref).reduce((a,b)=>a+b,0)||1;
 return jobProfiles.map(job=>{
   // A job fit score is preference-weighted, normalized for comparable rank ordering.
   const raw=Object.entries(pref).reduce((acc,[key,value])=>acc+value*job.traits[key],0);
   const score=raw/sum;
   const strengths=Object.entries(pref).filter(([,n])=>n>0).sort((a,b)=>b[1]-a[1]).slice(0,2).map(([key])=>({
     people:'人と関わること',pace:'活気のある環境',movement:'体を動かすこと',
     routine:'決まった手順で進めること',quiet:'落ち着いて集中すること',
     flexible:'働く日の柔軟さ',learn:'新しいことを覚えること'
   })[key]);
   return {...job,score,reason:'あなたが重視する「'+strengths.join('」「')+'」と、この仕事にある作業の特徴を照らし合わせた候補です。'};
 }).sort((a,b)=>b.score-a.score||a.name.localeCompare(b.name,'ja'));
}
