// Editorial examples, not employer-wide survey results or numeric rankings.
// Workload, customer interaction, and shifts vary by establishment and job posting.
export const comparisonFields = [
  {key:'tasks',label:'主な仕事内容'},
  {key:'customer',label:'接客・会話の場面'},
  {key:'physical',label:'体を動かす場面'},
  {key:'busy',label:'忙しくなりやすい場面'},
  {key:'training',label:'覚えること・研修'},
  {key:'shifts',label:'勤務時間・シフト'},
  {key:'check',label:'応募前に確認したいこと'}
];
export const comparisonJobs = [
 {id:'convenience',name:'コンビニ',emoji:'🏪',tag:'販売・サービス',tasks:'レジ、品出し、清掃、各種受付。店舗によって店内調理も。',customer:'レジ対応や問い合わせがある。',physical:'立ち仕事、品出しや清掃など。',busy:'来店が集中する時間帯や納品時。',training:'会計操作に加え、宅配・公共料金などの手順を学ぶことがある。',shifts:'早朝から深夜まで募集枠は店舗によりさまざま。',check:'実際の担当業務、研修時給、何人体制か、深夜勤務の有無。',link:'/job/convenience-store-jobs/',linkLabel:'コンビニの仕事内容を見る'},
 {id:'cafe',name:'カフェ',emoji:'☕',tag:'飲食・接客',tasks:'注文受付、ドリンク・軽食の準備、配膳や清掃など。',customer:'注文や受け渡しの対話がある。',physical:'立ち仕事、食器・材料の運搬がある場合も。',busy:'通勤・通学前、昼や休日など店舗の立地次第。',training:'メニューや器具、衛生手順、注文対応を覚える。',shifts:'朝・昼・夕方など。営業時間と募集枠を確認。',check:'ホールと調理の分担、覚えるメニュー、研修、ピーク時の配置。',link:'/company/starbucks/',linkLabel:'カフェ系チェーンの記事を見る'},
 {id:'family-restaurant',name:'ファミレス',emoji:'🍽️',tag:'飲食・接客',tasks:'ホールの案内・配膳・会計、またはキッチン調理・洗浄など。',customer:'ホールは接客が中心。キッチンは担当分担による。',physical:'立ち仕事や食器運搬、厨房作業など。',busy:'ランチ・夕食、土日祝など。',training:'ホールとキッチンで作業や習得内容が異なる。',shifts:'ランチ、夕方、夜間など。店舗による。',check:'ホール・キッチンの区分、混雑時の応援、清掃、終業時刻。',link:'/company/saizeriya/',linkLabel:'ファミレスの評判記事を見る'},
 {id:'supermarket',name:'スーパー',emoji:'🛒',tag:'販売・品出し',tasks:'レジ、商品補充、値付け、売り場整理。部門によって生鮮加工も。',customer:'レジや売り場で質問に答える場面がある。',physical:'品出しや立ち仕事。荷物の重さは部門による。',busy:'夕方の買い物時間帯、特売日など。',training:'レジ、商品・鮮度管理、部門固有のルールを学ぶ。',shifts:'開店前の品出し、日中、夕方などの募集がある。',check:'レジか品出しか、重い物の有無、部門と勤務時間。',link:'/guide/part-time-job-choosing/',linkLabel:'仕事の比較方法を見る'},
 {id:'warehouse',name:'倉庫・仕分け',emoji:'📦',tag:'軽作業・物流',tasks:'商品の仕分け、検品、梱包、棚入れなど。',customer:'一般客への接客は少ないことが多いが、チーム連携は必要。',physical:'立ち作業、歩行、荷物の移動など。',busy:'出荷締切前や繁忙期など。',training:'安全ルール、仕分け方法、端末操作を確認。',shifts:'日勤・夜勤・短期など募集先によって異なる。',check:'荷物の最大重量、作業環境、休憩、通勤手段、ノルマ。',link:'/guide/part-time-job-choosing/',linkLabel:'職場選びの確認項目を見る'},
 {id:'cleaning',name:'清掃',emoji:'🧹',tag:'施設・サービス',tasks:'床、設備、共用部などの清掃と備品補充。',customer:'利用者への挨拶や連絡が必要な場合がある。',physical:'歩き回る、かがむ、道具を運ぶなど。',busy:'開店前・閉店後や定められた清掃時間。',training:'道具・洗剤の安全な使用方法と清掃範囲。',shifts:'早朝や短時間など施設による。',check:'清掃場所、薬剤の扱い、単独作業か、移動と安全対策。',link:'/guide/part-time-job-choosing/',linkLabel:'応募前の比較表を見る'},
 {id:'office',name:'事務・データ入力',emoji:'💻',tag:'オフィス',tasks:'データ入力、書類整理、確認作業、電話補助など。',customer:'社内連絡や電話対応が含まれる募集もある。',physical:'座り作業が中心の募集もあるが、書類運搬なども。',busy:'締切前や処理件数が増える時期。',training:'入力システムや情報管理、事務手順を学ぶ。',shifts:'平日日中が中心の募集も。勤務先を確認。',check:'必要PCスキル、電話の有無、勤務形態、個人情報の扱い。',link:'/guide/part-time-job-choosing/',linkLabel:'求人の選び方を見る'},
 {id:'tutor',name:'塾講師・学習支援',emoji:'📚',tag:'教育',tasks:'授業・質問対応、学習の進捗確認や準備など。',customer:'生徒・保護者・教室担当者との説明や連絡がある。',physical:'座り授業・立ち授業など形態による。',busy:'試験前、講習期間、授業前後の準備時。',training:'担当科目、教材、授業の進め方を確認。',shifts:'夕方・夜や講習期など、担当コマによる。',check:'応募条件、準備・報告の賃金、担当学年、固定シフト。',link:'/guide/part-time-job-choosing/',linkLabel:'働く条件の比較方法を見る'},
 {id:'event',name:'イベントスタッフ',emoji:'🎪',tag:'イベント・短期',tasks:'受付、誘導、会場設営・撤収など案件によって異なる。',customer:'来場者への案内やスタッフとの連携がある。',physical:'長時間立つ、歩く、運ぶ作業が含まれる場合も。',busy:'開場・終演前後など。',training:'集合時に手順や安全・緊急対応を確認することがある。',shifts:'単発・週末・長時間の案件など。',check:'集合場所、実働と休憩、交通費、持ち物、撤収時間。',link:'/guide/part-time-job-choosing/',linkLabel:'求人比較のポイントを見る'}
];
export function selectComparison(ids) {
 if (!Array.isArray(ids) || ids.length < 2 || ids.length > 3 || new Set(ids).size !== ids.length) throw new RangeError('比較対象は異なる2〜3職種を選択');
 return ids.map(id => {
  const job = comparisonJobs.find(j=>j.id===id);
  if(!job)throw new RangeError('未定義の職種');
  return job;
 });
}
