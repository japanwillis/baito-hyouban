# エックスサーバーへの公開手順（準備版）

**現在は未公開です。** GitHub Actions の `Prepare static release (no deployment)` は、検証用の静的ファイルを作るだけでサーバー接続・公開はしません。

## 前提
- ドメイン: `baito-hyouban.com`
- Astro 静的出力: `dist/`
- エックスサーバーの公開ディレクトリ: 通常 `baito-hyouban.com/public_html/`。実環境で確認するまで固定パスとして使わないこと。
- SSH: 通常ポート `10022`、公開鍵認証。接続先ホスト名・サーバーIDはサーバーパネルで確認。
- HTTPS、ドメイン、DNS、メールへの影響を事前に確認。

## 本番公開の前提条件
1. 運営者情報・お問い合わせ先・プライバシーポリシー・広告掲載方針を確定し、公開ページを完成させる。
2. 記事編集承認、外部リンク検証、画像検品を完了する。
3. GitHub Actions のビルド成功・成果物の確認。
4. エックスサーバーのSSH設定で鍵を登録し、実際の接続先とホスト鍵指紋を検証する。
5. 転送対象・公開ディレクトリの内容とバックアップを確認する。ディレクトリを無差別削除しない。
6. 初回デプロイは手動承認を必須とし、成功後のURL確認まで公開済み扱いにしない。

## GitHubへの秘密情報の取り扱い
- SSH秘密鍵、サーバーパスワードをチャットやGoogleドライブに貼らない。
- GitHub Secretsの設定を行う際は鍵管理者自身がGitHubの管理画面で入力する。
- 公開鍵はサーバーパネルに登録する。公開鍵と秘密鍵を取り違えない。
- リリースワークフローが実装されるまで GitHub Actions は **サーバーに接続しない**。

## 公式マニュアル
- SSH設定: https://www.xserver.ne.jp/manual/man_server_ssh.php
- FTP公開ディレクトリ: https://www.xserver.ne.jp/manual/man_ftp_setting.php
- ドメイン設定: https://www.xserver.ne.jp/manual/man_domain_setting.php
