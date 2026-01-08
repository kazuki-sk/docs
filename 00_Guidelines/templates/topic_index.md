# [Title] システム名/作業名

## 1. Context (Why)
## 2. Prerequisites
* OS: Ubuntu 24.04 LTS
* Depends on: Docker, NFS Mount

## 3. Architecture
## 4. Secrets
* `${SERVICE_ADMIN_PASSWORD}`: WebUIログイン用
* `${API_TOKEN}`: 外部連携用

## 5. Steps (How)

### 5.1 Installation
```bash
# コマンド例
echo helloworld
```

### 5.2 Configuration

* File: `/etc/xxx/config.yaml`

```yaml
# 重要な設定箇所のみ抜粋
key: value

```

## 6. Verification

```bash
curl -I http://localhost:8080

```

## 7. Operations & Troubleshooting

## 8. References

* [Official Documentation](https://www.google.com/search?q=url)
