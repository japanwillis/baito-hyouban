// Editorial navigation data, not a clinical assessment or individual employment advice.
export const worries=[
 {id:'interview',category:'応募前',icon:'💬',title:'面接でうまく話せるか不安',summary:'回答を丸暗記するより、応募理由・勤務できる日時を自分の言葉で整理。',steps:['応募理由を一文で書き、希望する曜日・時間帯をメモする','聞き返してもよいことを覚えておく','逆質問を1〜2つ用意する'],question:'初めてのアルバイトです。最初に担当する仕事や研修の進め方を教えていただけますか。',link:'/guide/part-time-job-interview/',label:'面接の質問と回答例'},
 {id:'mistakes',category:'働き始め',icon:'📝',title:'仕事でミスをしたらどうしよう',summary:'最初から全部覚える前提でなく、確認する相手と手順を知っておく。',steps:['まず報告する相手と連絡方法を確認する','わからない作業は自己判断せず質問する','よく使う手順をメモし、職場のルールに沿って見直す'],question:'まだ慣れていない作業で迷ったときは、どなたに確認すればよいですか。',link:'/guide/part-time-job-first-day/',label:'初日の準備と注意点'},
 {id:'remember',category:'働き始め',icon:'📚',title:'覚えることが多そうで心配',summary:'仕事を段階的に学べるか、研修内容と質問できる体制を確認。',steps:['初回に担当する仕事を質問する','研修の期間・担当者・マニュアルの有無を確認する','習得順序をメモし、優先度の高い作業から復習する'],question:'初めの数回は、どんな順番で仕事を教えていただけますか。',link:'/job/convenience-store-jobs/',label:'コンビニの仕事と研修'},
 {id:'people',category:'人間関係',icon:'🤝',title:'先輩や店長とうまくやれるか不安',summary:'職場に慣れるまでの連絡方法や、新人へのフォローを見ておく。',steps:['業務上の報告・相談先を確認する','困った場面で質問できる人がいるか確認する','深刻な言動が続く場合は記録して外部相談も検討する'],question:'新人が仕事で困ったときは、どなたに相談できますか。',link:'/workplace-check/',label:'職場環境の気になる点を確認'},
 {id:'customers',category:'仕事内容',icon:'🧑‍💼',title:'接客や知らない人との会話が苦手',summary:'「接客あり・なし」だけでなく、担当する場面とフォロー体制で比較。',steps:['レジ・案内・問い合わせのどの業務があるか確かめる','困った質問の引き継ぎ先を確認する','接客と裏方の割合を職種ごとに比較する'],question:'接客で判断に迷ったとき、どのように社員の方へ引き継ぎますか。',link:'/job-comparison/',label:'接客の場面を職種で比較'},
 {id:'busy',category:'仕事内容',icon:'⏱️',title:'忙しい時間に対応できるか不安',summary:'ピークの時間帯と、そのときの役割分担を確認する。',steps:['混雑する時間帯を質問する','忙しいときの優先順位と応援方法を聞く','一度に任される仕事の範囲を確認する'],question:'混雑している時間は、どのように業務を分担していますか。',link:'/job-comparison/',label:'忙しくなる場面を比較'},
 {id:'shift',category:'学校・生活',icon:'📅',title:'学校や試験とシフトを両立できるか不安',summary:'「週2日から」と希望曜日が通るかは別。提出・確定・変更のルールを確認。',steps:['授業や試験で勤務できない日を先に整理する','希望の提出期限と確定日を聞く','急な変更が必要なときの連絡手段を確認する'],question:'試験期間はシフト希望を調整できますか。いつまでにお伝えすればよいでしょうか。',link:'/guide/part-time-job-shift/',label:'シフトの確認ポイント'},
 {id:'firstday',category:'働き始め',icon:'🎒',title:'初日に何を持っていけばいい？',summary:'集合場所・時刻・担当者・服装・指定の持ち物を確認。',steps:['初日の案内を読み直す','集合時刻、入口、担当者の連絡先を確認する','指定された持ち物と交通経路を用意する'],question:'初日の集合場所、服装、持ち物を改めて確認してもよろしいですか。',link:'/guide/part-time-job-first-day/',label:'初日の持ち物と挨拶'},
 {id:'pay',category:'お金',icon:'💴',title:'月にいくら稼げるか見当がつかない',summary:'時給と実働時間・勤務日数から税引前の収入を見積もる。',steps:['求人の時給と研修期間の条件を確かめる','実働時間と無給休憩を分ける','月収シミュレーターで複数のシフトを比較する'],question:'研修中の時給と交通費、休憩時間の扱いを教えてください。',link:'/salary-calculator/',label:'月収シミュレーター'},
 {id:'choose',category:'応募前',icon:'🔎',title:'どんなバイトを選べばいいかわからない',summary:'向き不向きを決めつけず、仕事内容・通勤・時間帯から候補を絞る。',steps:['譲れない条件を先に書き出す','気になる職種を2〜3件比較する','希望と仕事内容が合うか求人票で確認する'],question:'最初に担当する仕事内容と、シフトの条件を詳しく伺えますか。',link:'/diagnosis/',label:'向いているバイト診断'},
 {id:'health',category:'学校・生活',icon:'🌿',title:'体力的に続けられるか心配',summary:'立ち仕事や荷物運びの量・休憩の取り方は職場と担当次第。',steps:['長時間の立ち作業や重い物の有無を確認する','働ける日数と休息日を無理のない範囲で決める','体調や安全上の不安があれば相談する'],question:'立ち作業の時間や荷物の重さ、休憩の取り方について教えてください。',link:'/job-comparison/',label:'仕事ごとの作業の違い'},
 {id:'terms',category:'お金',icon:'📄',title:'契約書や給料のルールがわからない',summary:'時給・勤務場所・業務・支払日などを、労働条件通知書で確認。',steps:['求人票の条件を保存する','労働条件通知書や契約内容を確認する','不明点をまとめ、必要なら相談窓口も利用する'],question:'労働条件通知書で、賃金と勤務時間を確認できますか。',link:'/guide/labor-conditions-notice/',label:'労働条件通知書の見方'}
];
export const worryCategories=['すべて','応募前','仕事内容','働き始め','人間関係','学校・生活','お金'];
export function filterWorries({category='すべて',query=''}={}){
 if(!worryCategories.includes(category)||typeof query!=='string')throw new RangeError('Invalid filter');
 const needle=query.trim().normalize('NFKC').toLocaleLowerCase('ja');
 return worries.filter(w=>(category==='すべて'||w.category===category)&&(!needle||[w.title,w.summary,w.category,...w.steps].join(' ').normalize('NFKC').toLocaleLowerCase('ja').includes(needle)));
}
