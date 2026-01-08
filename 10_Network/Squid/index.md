---
tags: [network, squid, proxy, ubuntu]
date: 2026-01-08
status: stable
---

# [Network] Squid Proxy Server (Tunnel / Basic Auth / SSL Bumping)

## 1. Context (Why)

* **目的**: LAN内クライアント（Ubuntu Desktop）のHTTP/HTTPS通信を制御・監視するため。
* **段階的構築**:
    1. **Phase 1**: シンプルなフォワードプロキシ（Tunnel）
    2. **Phase 2**: Basic認証の導入
    3. **Phase 3**: SSL Bumping（HTTPS解析）の導入

## 2. Prerequisites

* **Server OS**: Ubuntu Server 24.04.3 LTS
* **Client OS**: Ubuntu Desktop 24.04 LTS
* **Network**:
  * Server IP: `10.0.20.2` (Port: 3128)
  * Allowed Network: `10.0.0.0/16` (`192.168.xx.0/24`等、環境に合わせて調整)
* **Depends on**:
  * `squid` (Phase 1-2)
  * `squid-openssl` (Phase 3)
  * `apache2-utils` (For htpasswd)

## 3. Architecture

* **Config Strategy**:
  * メイン設定: `/etc/squid/squid.conf` (共通設定、include定義のみ)
  * 個別設定: `/etc/squid/conf.d/local.conf` (ACL, Port, Auth, SSL設定など)
* **Files Mapping**:
  * Repository: `./files/` -> Server: `/etc/squid/`

## 4. Secrets

* `/etc/squid/passwd`: Basic認証用ユーザー/パスワードハッシュ
* `/etc/squid/squid-ca-key.pem`: SSL Bumping用オレオレ認証局秘密鍵

## 5. Steps (How)

### 5.1 Installation (Base)

```bash
sudo apt update
sudo apt install squid -y

# 動作確認
systemctl status squid

```

> [!NOTE]
> 今後 SSL Bumping を実装する予定がある場合は、最初から `squid-openssl` をインストールすることを推奨する。

### 5.2 Phase 1: Simple Tunnel Configuration

デフォルト設定を退避し、リポジトリ内の設定ファイルを適用する。

**1. 設定ファイルの作成**

```bash
# デフォルト設定のバックアップ
sudo mv /etc/squid/squid.conf /etc/squid/squid.conf.default

```

* **Main Config**: `/etc/squid/squid.conf`
* 以下のリンク先の内容で上書きする:
* [./files/squid.conf](./files/squid.conf)

* **Local Config**: `/etc/squid/conf.d/local.conf`
* 以下のリンク先の内容で新規作成（または上書き）する:
* [./files/local.conf](./files/local.conf)

**2. 適用**

```bash
# 構文チェック
squid -k parse
# 適用
sudo systemctl restart squid.service

```

### 5.3 Phase 2: Basic Authentication

**1. 認証ツールのインストールとユーザー作成**

```bash
sudo apt install apache2-utils -y
# ユーザー作成 (初回は -c オプション付き)
sudo htpasswd -c /etc/squid/passwd user01

```

**2. 設定ファイルの更新**

Basic Auth対応の設定ファイルに書き換える。

* **Main Config**: `/etc/squid/squid.conf`
* 以下のリンク先の内容で上書きする:
* [./files/squid_basic_auth.conf](./files/squid_basic_auth.conf)

* **Local Config**: `/etc/squid/conf.d/local.conf`
* 以下のリンク先の内容で上書きする:
* [./files/local_basic_auth.conf](./files/local_basic_auth.conf)

**3. 適用**

```bash
squid -k parse
sudo systemctl restart squid

```

### 5.4 Phase 3: SSL Bumping

**1. SSL対応パッケージのインストール**

```bash
sudo apt update
sudo apt install squid-openssl -y

```

**2. オレオレ認証局 (CA) の作成**

```bash
cd /etc/squid
# 証明書作成 (有効期限10年)
sudo openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
  -keyout squid-ca-key.pem -out squid-ca-cert.pem \
  -subj "/C=JP/ST=Tokyo/L=Minato/O=HomeLab/OU=Proxy/CN=SquidCA"

# 権限設定 (proxyユーザー所有とする)
sudo chmod 600 squid-ca-key.pem
sudo chown proxy:proxy squid-ca-key.pem

```

**3. SSLキャッシュDBの初期化**

```bash
# DB再作成(おまじない)
sudo rm -rf /var/lib/squid/ssl_db
# ディレクトリ作成
sudo mkdir -p /var/lib/squid/

sudo /usr/lib/squid/security_file_certgen -c -s /var/lib/squid/ssl_db -M 4MB

# 権限設定
sudo chown -R proxy:proxy /var/lib/squid/ssl_db

```

**4. 設定ファイルの更新**

SSL Bumping対応の設定ファイルに書き換える。
※ `local.conf` は Phase 2 の状態（Basic Auth設定済み）を引き継ぐ想定のため、変更不要。

* **Main Config**: `/etc/squid/squid.conf`
* 以下のリンク先の内容で上書きする:
* [./files/squid_ssl_bumping.conf](./files/squid_ssl_bumping.conf)

**5. 適用**

```bash
# 証明書読み込み権限が必要なためsudo推奨
sudo squid -k parse
sudo systemctl restart squid

```

### 5.5 Client Configuration (Ubuntu Desktop)

**1. CA証明書のインポート (Phase 3)**

```bash
# Serverから証明書を取得
scp user@10.0.20.2:/etc/squid/squid-ca-cert.pem .

# システムへのインストール
sudo cp ./squid-ca-cert.pem /usr/local/share/ca-certificates/squid-ca-cert.crt
sudo update-ca-certificates

```

**2. プロキシ設定 (GNOME)**

```bash
# ホスト・ポート設定
gsettings set org.gnome.system.proxy.http host '10.0.20.2'
gsettings set org.gnome.system.proxy.http port 3128
gsettings set org.gnome.system.proxy.https host '10.0.20.2'
gsettings set org.gnome.system.proxy.https port 3128
gsettings set org.gnome.system.proxy ignore-hosts "['localhost', '127.0.0.0/8', '10.0.0.0/16', '::1']"

# 認証設定 (Phase 2以降)
gsettings set org.gnome.system.proxy.http use-authentication true
gsettings set org.gnome.system.proxy.http authentication-user 'username'
gsettings set org.gnome.system.proxy.http authentication-password 'password'

# 有効化
gsettings set org.gnome.system.proxy mode 'manual'

```

![GNOME Proxy Settings](./images/gnome_proxy_settings.png)

**3. APT設定**

File: `/etc/apt/apt.conf.d/90proxy`

```text
Acquire::http::Proxy "http://{username}:{password}@10.0.20.2:3128/";
Acquire::https::Proxy "http://{username}:{password}@10.0.20.2:3128/";

```

**4. 環境変数設定**

File: `/etc/environment` (追記)

```bash
http_proxy="http://{username}:{password}@10.0.20.2:3128/"
https_proxy="http://{username}:{password}@10.0.20.2:3128/"
no_proxy="localhost,127.0.0.1,::1,10.0.0.0/16"
HTTP_PROXY="http://{username}:{password}@10.0.20.2:3128/"
HTTPS_PROXY="http://{username}:{password}@10.0.20.2:3128/"
NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/16"

```

## 6. Verification

* **サービス状態**: `systemctl status squid`
  * Active (running) となっていることを確認する。
    ![Service Status](./images/service_status_active.png)

* **アクセスログ**: `sudo tail -f /var/log/squid/access.log`
  * 接続先ホストやメソッド（CONNECT/GET）が記録されていることを確認する。
    ![Access Log](./files/access_log_sample.jpg)

* **クライアント疎通確認**:
  * ブラウザでアクセスした際、認証ダイアログが表示されるか確認する。Basic Authが効いてるかの確認
    ![Auth Dialog](./images/browser_auth_dialog.png)

* **動作ログ**: `sudo tail -f /var/log/squid/cache.log`
* **クライアント疎通確認 (curl)**:

```bash
# Basic Auth + SSL Chain Check
curl -x http://{username}:{password}@10.0.20.2:3128 -I [https://www.google.com](https://www.google.com) -v

```

## 7. Operations & Troubleshooting

* **設定変更時の構文チェック**
設定ファイルを変更した際は、再起動前に必ず構文チェックを行うこと。
以下は設定ミス（IPアドレスの記述ミス）がある場合のエラー出力例。`FATAL` や `Bungled` と表示され、該当の行番号（line 4）が指摘される。

```bash
squid -k parse
```

![Error Syntax Check](./images/error_syntax_check.png)

* **Firefoxの証明書エラー**:
* FirefoxはOSの証明書ストアを参照しない場合がある。証明書（.crt）をブラウザ設定から手動インポートするか、`about:config` で `security.enterprise_roots.enabled` を `true` に設定する。

* **SSL DBエラー**:
* `FATAL: Cannot generate certificates` が出る場合、`/var/lib/squid/ssl_db` の所有者がSquid実行ユーザー（proxy）になっているか確認する。

## 8. References

* [Ubuntu 24.04 で Squid プロキシサーバーを設定する](https://www.server-world.info/query?os=Ubuntu_24.04&p=squid&f=2)
* [Squid Config Examples](https://wiki.squid-cache.org/ConfigExamples/)
* [SquidでSSL Bump(HTTPSデコード)設定](https://qiita.com/zukizukizukizuki/items/e71cddc73f626a7393d9)
