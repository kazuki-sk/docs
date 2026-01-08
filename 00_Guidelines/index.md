# Infrastructure Documentation Guidelines

このリポジトリは、自身のインフラ環境（オンプレミス・クラウド）の構築手順、設計思想、およびトラブルシューティングの記録を管理するものである。

## Core Philosophy
1.  **再現性 (Reproducibility)**
    * 未来の自分が、ドキュメントだけを見て環境を再構築できる状態を目指す。
    * 「何をしたか」だけでなく「なぜそうしたか（Context）」を記録する。
2.  **検索性 (Searchability)**
    * 情報はトピックごとのディレクトリに集約する。
    * 散乱しやすい「試行錯誤のログ」も適切な場所に配置する。
3.  **安全性 (Security)**
    * Credential（パスワード、APIキー等）は絶対にコミットしない。

## Quick Links
* 📂 **[ディレクトリ構成と命名規則](./rules/directory.md)** - ファイルをどこに置くか迷ったらここ。
* 🔒 **[機密情報の管理ルール](./rules/secrets.md)** - パスワードの書き方について。
* 🏷️ **[タグ・運用ルール](./rules/tagging.md)** - 管理フローについて。

## Templates (Copy & Paste)
新しい作業を始めるときは、以下のテンプレートを使用すること。

* 📝 **[手順書テンプレート (index.md)](./templates/topic_index.md)**
    * 構築完了後、清書して残すためのフォーマット。
* 📓 **[スクラップテンプレート (scraps)](./templates/scrap_memo.md)**
    * 作業中のメモ、エラー調査、ログ貼り付け用。
