# Tagging & Workflow

（現在はドラフト段階。必要に応じて拡張する）

## Tagging
検索性を高めるため、ファイルの先頭（Front matter）にタグを記述することを推奨する。

```yaml
---
tags: [network, unbound, dns, ubuntu]
date: 2026-01-08
status: stable
---

```

## Workflow

1. **Draft**: `scraps/` にメモを作成。
2. **Verify**: 実機で構築・検証。
3. **Document**: `index.md` に清書。
4. **Archive**: 不要になった `scraps` はそのまま残すか、整理して削除。
