# [WIP] Squid Proxy 構築作業ログ

* Date: 2026-01-09
* OS: Ubuntu server 24.04.3
* Clinet: Ubuntu Desktop 24.04 


## 1. 方針
* **配置**: `10_Network/Squid`
* **インストール**: `apt install squid-openssl` (SSL対応が必要か要検討)
* **要件**:
    * Port: 3128
    * 対象ネットワーク: 192.168.xx.0/24 からのみ許可
    * ログ: /var/log/squid/access.log

## 2. 作業ログ (時系列)

### 2.1 インストール
```bash
sudo apt update
sudo apt install squid -y
```

いれたSquid
`squid/noble-updates,noble-security 6.13-0ubuntu0.24.04.3 amd64`

動いてるか確認
``` bash
systemctl status squid
```

下記マンドでコンフィグディレクトリが使える確認
```bash
sudo cat /etc/squid/squid.conf | grep include
```

config file作成
```bash
sudo touch /etc/squid/conf.d/local.conf
```

[config file](./files/local.conf)
`/etc/squid/conf.d/local.conf`ここに貼り付け

デフォルト設定ではいろいろ許可されすぎているのでdefaultzファイルとして保存。(設定の説明があるので残しておくと便利そう)
```bash
sudo mv /etc/squid/squid.conf /etc/squid/squid.conf.default
```

新規でconfig fileを作成する。(共通設定用、個別の設定は/etc/squid/conf.d/以下に書く)
```bash
sudo touch /etc/squid/squid.conf
```

[config file](./files/squid.conf)
`/etc/squid/squid.conf`ここに貼り付け

やってることは`/etc/squid/conf.d/`以下の`.conf`ファイルのインクルード

config fileの検証
```bash
squid -k parse
```

設定適用
```bash
sudo systemctl restart squid.service
```

Client側でproxyを設定

```bash
#GUI側の設定
# HTTPプロキシの設定
gsettings set org.gnome.system.proxy.http host '10.0.20.2'
gsettings set org.gnome.system.proxy.http port 3128

# HTTPSプロキシの設定
gsettings set org.gnome.system.proxy.https host '10.0.20.2'
gsettings set org.gnome.system.proxy.https port 3128

# 除外設定（localhostなど）
gsettings set org.gnome.system.proxy ignore-hosts "['localhost', '127.0.0.0/8', '10.0.0.0/16', '::1']"

# 設定を有効化（手動モード）
gsettings set org.gnome.system.proxy mode 'manual'

# APT側
cat <<EOF | sudo tee /etc/apt/apt.conf.d/90proxy
Acquire::http::Proxy "http://10.0.20.2:3128/";
Acquire::https::Proxy "http://10.0.20.2:3128/";
EOF

# 環境変数
# 現在の設定のバックアップ
sudo cp /etc/environment /etc/environment.bak

# 設定を追記（tee -a で追記モード）
cat <<EOF | sudo tee -a /etc/environment

# Proxy Settings
http_proxy="http://10.0.20.2:3128/"
https_proxy="http://10.0.20.2:3128/"
ftp_proxy="http://10.0.20.2:3128/"
no_proxy="localhost,127.0.0.1,::1,10.0.0.0/16"
HTTP_PROXY="http://10.0.20.2:3128/"
HTTPS_PROXY="http://10.0.20.2:3128/"
FTP_PROXY="http://10.0.20.2:3128/"
NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/16"
EOF
```

再起動
```bash
sudo reboot
```

ブラウザ等で適当なWebサイトにアクセスしてみる

Proxyのアクセスログを見てみる
```bash
sudo cat /var/log/squid/access.log
```

ログを見るとTimestamp形式で時刻が入ってる

## basic Authをいれる

パスワードを暗号化して保存するために apache2-utils パッケージが必要
```bash
sudo apt update
sudo apt install apache2-utils -y
```

basic auth用のUser Pass

```bash
sudo htpasswd -c /etc/squid/passwd user01
```

Squidの設定書き換え

まずはメインの設定から
[config file](./files/squid_basic_auth.conf)
`/etc/squid/squid.conf`ここに上書き

※下記があることを確認すること lsとかで存在確認できるはず
- /usr/lib/squid/basic_ncsa_auth
- /etc/squid/passwd

次にlocalの方
[config file](./files/local_basic_auth.conf)
`/etc/squid/conf.d/local.conf`ここに上書き

構文チェック
```bash
squid -k parse
```

OKだったら適用
```bash
sudo systemctl restart squid
```

Client側でproxyを設定
Basic Authの形に変更するだけ
`example:) http://{username}:{password}@10.0.20.2:3128/`

gsettingsだけはbasic Authの形式じゃなくて追加で下記コマンドを実行する

```bash
# 認証が必要なことを設定
gsettings set org.gnome.system.proxy.http use-authentication true

# ユーザー名とパスワードを設定
gsettings set org.gnome.system.proxy.http authentication-user 'username'
gsettings set org.gnome.system.proxy.http authentication-password 'password'
```

Log見て通ってたらOK
```bash
sudo cat /var/log/squid/cache.log
```

## SSL Bumpingをする

squid-opensslが必要なのでインストールする
念のため設定ファイルはバックアップしておく
多分消えないからやらなくてもいい(私の環境では消えなかった)
```bash
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.backup
```

```bash
sudo apt update
sudo apt install squid-openssl -y
```

作業しやすいようにsquidのディレクトリに移動しておく
```bash
cd /etc/squid
```

自己証明書が必要なので作る+権限を整える
今回は適当に10年
```bash
sudo openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
  -keyout squid-ca-key.pem -out squid-ca-cert.pem \
  -subj "/C=JP/ST=Tokyo/L=Minato/O=HomeLab/OU=Proxy/CN=SquidCA"
sudo chmod 600 squid-ca-key.pem
sudo chown {basic Authの時に作ったユーザー}:{basic Authの時に作ったユーザー} squid-ca-key.pem
```

作った偽造証明書をキッシュするためのDB＋権限設定
```bash
sudo rm -rf /var/lib/squid/ssl_db
sudo mkdir /var/lib/squid/
sudo /usr/lib/squid/security_file_certgen -c -s /var/lib/squid/ssl_db -M 4MB
sudo chown -R {basic Authの時に作ったユーザー}:{basic Authの時に作ったユーザー} /var/lib/squid/ssl_db
```


Squidの設定書き換え

メインの設定
[config file](./files/squid_ssl_bumping.conf)
`/etc/squid/squid.conf`ここに上書き

構文チェック
証明書みるからちゃんとrootでやろう
```bash
sudo squid -k parse
```

squid再起動
```bash
sudo systemctl restart squid
```

## Squidの証明書を信頼させる
証明書をとってくる
※ローカルPCからscpでとってくる方法を書いてるけど、catとかでやってもいい
```bash
scp {Server User Name}@10.0.20.2:/etc/squid/squid-ca-cert.pem ~ 
```

Clientの/usr/local/share/ca-certificates/に証明書を入れる
```bash
sudo cp ./squid-ca-cert.pem /usr/local/share/ca-certificates/squid-ca-cert.crt
```

ストアを更新

```bash
sudo update-ca-certificates
```

firefox等で試して証明書エラーが出る場合はcurlでも試してみる
```bash
curl -x http://{SquidのBasic AuthのUsername}:{SquidのBasic AuthのPassword}@10.0.20.2:3128 -I https://www.google.com -v
```

これで証明書エラーが出ない場合はOSへの証明書インストールはできているけれどfirefox等が読めていないだけの可能性が高いのでブラウザ画面から証明書をインポートする(.crt形式が好ましい)


これで問題なく通信できる場合これでOK

参考；
https://qiita.com/zukizukizukizuki/items/e71cddc73f626a7393d9
https://www.server-world.info/query?os=Ubuntu_24.04&p=squid&f=2
https://wiki.squid-cache.org/ConfigExamples/