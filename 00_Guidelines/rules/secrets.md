# Secrets Management

**Gitリポジトリには、パスワード・APIキー・秘密鍵を一切含めてはならない。**

## 1. プレースホルダー記法
ドキュメントや設定ファイル例には、以下の形式で変数を記述する。

* Format: `${CATEGORY_VARIABLE_NAME}`
* Rule: 全て大文字、スネークケース、`${}`で囲む。

### Examples
| Type | Bad (NG) | Good (OK) |
| :--- | :--- | :--- |
| Password | `password123` | `${DB_ROOT_PASSWORD}` |
| API Key | `xoxb-1234...` | `${SLACK_API_TOKEN}` |
| IP Address | `192.168.1.10` | `192.168.1.10` (ローカルIPは可とする場合) |

## 2. 実データの管理
実際の値は、パスワードマネージャー（1Password, Bitwarden 等）のセキュアノートで管理する。
ノートのタイトルを `[Github] Path/To/Document` とリンクさせておくと検索しやすい。

## 3. .gitignore Policy
以下のファイルは必ず除外する。

```gitignore
# Secrets
.env
.env.*
*.pem
*.key
id_rsa
kubeconfig

# Logs & Temp
*.log
*.tmp
.DS_Store

```
