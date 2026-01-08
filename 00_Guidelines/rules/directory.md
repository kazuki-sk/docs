# Directory Structure & Naming Convention

## 1. Top Level Structure
レイヤー（階層）と役割（ロール）に基づく分類を行う。

| Directory | Layer | Description |
| :--- | :--- | :--- |
| **00_Guidelines** | Meta | 運用ルール、テンプレート |
| **10_Network** | Physical/L2-L3 | Router, Switch, VLAN, DNS, VPN |
| **20_Virtualization** | Infrastructure | Proxmox, ESXi, Cloud (Azure/AWS), IaC |
| **30_OS_Base** | OS Config | Ubuntu/Debian設定, User, SSH, Hardeninig |
| **40_Middleware** | Middleware | Docker, K8s, DB, WebServer |
| **50_Services** | Application | Minecraft, Monitoring, HomeAssistant, Apps |
| **60_Development** | Dev Tools | VSCode, Git, Dotfiles, Scripts |
| **99_Troubleshooting** | Post-mortem | 特定トピックに属さない汎用的なエラー記録 |

## 2. Topic Directory Structure
各トピック（技術・サービス）は、ディレクトリ単位で情報を完結させる。

```text
[Category]/[Topic_Name]/
├── index.md        # 【正】構築・運用手順の決定版
├── scraps/         # 【副】作業ログ、エラー調査、試行錯誤のメモ
│   └── yyyy-MM-dd-[title].md
└── files/          # 【資材】設定ファイルのサンプル、構成図画像など

```

## 3. Naming Rules

* **ディレクトリ名/ファイル名**:
* 半角英数字 (kebab-case または Snake_Case)。
* 日本語ファイル名は避ける（検索・CLI操作の利便性のため）。


* **Scrapsファイル**:
* `yyyy-MM-dd-[keyword].md`
* 例: `2026-01-08-unbound-error.md`
