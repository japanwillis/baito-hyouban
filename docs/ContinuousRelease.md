# 継続公開の手順（2記事目以降）

## 状態と担当

BH-0001は既存公開記事。本文・画像・生成HTMLの変更を今回の継続公開処理では許可しない。
BH-0002以降は、Googleドライブのマスター指示書・公開運営指示書・記事台帳を毎回読み直し、編集承認・画像検品・出典確認が終わった記事だけを最大1件ずつ反映する。
執筆・編集承認・画像制作はそれぞれのWorkが担当する。
初回公開専用 `initial-publish-xserver.yml` は再実行しない。

## 記事の受け取り

1. 台帳から記事ID・編集レビューURL・最終原稿URL・最終画像URL・alt文を確認する。編集待ち／差し戻し／保留なら終了する。
2. 原稿から管理メモを除き、最終稿だけをMarkdownへ移す。画像は1200×630の検品済みWebPを使用する。元の承認済み内容を書き換えない。
3. 公式・公的出典と内部リンクを再確認する。未公開記事へのリンクを出さない。
4. `ops/publication-approvals.json` に記事ID、原稿・レビュー・画像URL、公開パス、確認日、承認状態、画像検品状態、残留条件解消、原稿・画像のSHA256を記録する。
5. 変更をPRにまとめる。`npm ci` → `npm test` → `npm run build` を通す。ビルド前後のゲートは承認記録のない原稿・画像・生成記事を拒否する。下書きは `src/pages` や `public` に置かない。
6. PC／スマホ表示、見出し、タイトル、description、canonical、OG画像、リンク、一覧・サイトマップへの掲載を検品する。PRの差分と台帳を照合してからmainに反映する。

## 本番へ書き込まない差分確認（plan）

GitHub Actionsの **Continuous release (manual plan, deploy, rollback)** を開く。
Use workflow fromは`main`、modeは`plan`、source_shaは現在のmainの完全な40桁SHA。他の入力は空欄。

planは本番ファイルを書き換えない。接続先ホスト鍵を既存の固定指紋と照合し、非公開領域へ候補を転送する。
サーバーのPython3、同一ファイルシステム、バックアップ・切替・途中失敗からの復旧を非公開の使い捨て領域で試験する。
本番全ファイルと候補のSHA256を比較し、追加・変更・維持されるファイル、対象コミット、plan_sha256をActionsのSummaryと`result.json`に出す。
BH-0001のHTML／画像変更、既存HTMLの削除、シンボリックリンク、パス逸脱、未完了の公開処理があれば停止する。

## 差分への手動承認と公開（deploy）

planの結果と、原稿・画像の承認を人が確認する。GitHubリポジトリに書込権限がある人が手動実行する方式であり、二者承認やGitHub Environmentの必須レビューを設定済みという意味ではない。
PrivateリポジトリのEnvironment保護機能は契約により利用条件が異なるため、この方式はその機能に依存しない。

別の実行でmodeを`deploy`、source_shaをplanと同じSHA、plan_sha256を結果の64桁ハッシュにする。
approvalには `DEPLOY <source_sha> <plan_sha256>` を正確に入力する。backup_idは空欄。
mainが進んだ場合は新しいmainでplanからやり直す。plan後の本番ファイル変更や候補ファイル変更でもハッシュが一致せず停止する。

公開前に本番全体を `$HOME/.baito-hyouban-deploy/release-<run_id>-<attempt>/backup` へ保存し、ハッシュ一致を確認する。
非公開の作業ディレクトリで既存ファイルと候補を合成し、既存のサーバー設定・古い参照用アセットを維持する。無差別削除・`rsync --delete`を使用しない。
二回のディレクトリrenameで切り替えるため、二回の間には非常に短い公開ディレクトリ不在の時間がある。完全無停止の原子的交換ではない。
候補内の全静的ファイルをHTTPSで取得し、HTTP 200・リダイレクトなし・バイト列のSHA256一致を検証してから成功を確定する。
HTTPS検証失敗時は直前バックアップへ戻して再検証する。既存ファイルが予期せず変わっていれば、上書き復旧せず停止する。

## 復旧（rollback）

通常の障害は自動で復旧する。プロセス強制終了・タイムアウト・SSH断などで結果不明の場合は、再デプロイせずActionsログとサーバーのpending記録を確認する。
バックアップIDは失敗／成功したdeployの`<run_id>-<attempt>`。planのrun IDではない。
手動復旧はmode=`rollback`、現在のmainのsource_sha、backup_id、approval=`ROLLBACK <backup_id>`を指定する。plan_sha256は不要。
最新の有効公開または未完了処理のバックアップだけを復旧可能とする。バックアップの完全性と本番の差分を再確認し、失敗版も非公開領域に残す。
復旧後に全体のサーバーハッシュと公開ファイルのHTTPSを再検証する。
バックアップと退避版を自動削除しない。容量は運営担当が確認し、保存期限・削除方針は別途決める。

## 成功後の記録

本番記事URL・一覧・サイトマップ・PC／スマホ表示を確認してから、台帳の対象記事の公開状態と公開URLを更新する。
原稿・画像URL、編集判定とレビューURLは他Workの管理情報として維持する。
停止した場合は対象ID、完了工程、エラー、再開手順、Actions URLを台帳の備考へ記録する。Search Console未接続の順位・流入・インデックス状況は記載しない。

## 検証範囲と運用上の制約

- 実装には承認欠落、承認後改変、本番ドリフト、BH-0001変更、HTML削除、バックアップ一致、正常復旧、切替途中失敗、未完了処理、シンボリックリンク、危険なアーカイブを拒否する自動試験がある。
- 本番への初回適用前にplanの成功とサーバー上の復旧リハーサル成功を確認する。ローカル試験を本番試験と呼ばない。
- 承認台帳は公開前にDriveで人／担当Workが確認してGitHubへ転記する。GitHub ActionsがDriveの承認を自動取得する仕組みではない。
- 復旧は直前1回が対象。古い公開版への任意の巻き戻しやHTML削除は別途設計する。
- 公開・復旧以外の手動サーバー編集を同時にしない。GitHubの同一concurrency groupとサーバーロックで本処理の二重起動を防ぐ。

参考：
- https://docs.astro.build/en/guides/markdown-content/
- https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
