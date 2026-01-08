import os
import re
import datetime

# --- 設定 ---
TARGET_FILENAME = "index.md"     # 探すファイル名
OUTPUT_FILENAME = "CATALOG.md"   # 出力するファイル名
IGNORE_DIRS = {".git", ".vscode", "files", "images", "scraps"} # 無視するディレクトリ

# ステータスごとのアイコン定義
STATUS_ICONS = {
    "stable": "🟢",
    "draft": "🟡",
    "deprecated": "🔴",
    "archived": "🔒",
    "wip": "🚧"
}

def clean_text(text):
    """Markdownの装飾を除去してプレーンテキストに近づける"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Bold除去
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # Link除去
    return text.strip()

def extract_description(content):
    """
    優先順位をつけて概要を抽出する
    1. Frontmatterの description
    2. '## Definition' 直下のテキスト (Category Index用)
    3. '**目的**' や '**概要**' (Context) (Project Index用)
    """
    
    # Strategy 1: '## Definition' (主にカテゴリトップ用)
    # ## Definition の次の行から、次の見出し(#)が来るまでの間の文字列を取得
    def_match = re.search(r'^##\s+Definition\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL | re.MULTILINE)
    if def_match:
        desc = def_match.group(1).strip()
        # 空行や箇条書きを適当に処理
        return clean_text(desc.split('\n')[0]) # 最初の1行だけ返す

    # Strategy 2: '**目的**' or '**概要**' or '**Goal**' (箇条書き対応)
    # 行頭の * や - を無視して抽出
    ctx_match = re.search(r'[\*\-]\s*\*\*(?:目的|概要|Goal)\*\*\s*[:：]\s*(.*)', content)
    if ctx_match:
        return clean_text(ctx_match.group(1))

    return "No description"

def parse_md_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Frontmatter
    meta = {"tags": [], "status": "", "date": ""}
    fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    
    if fm_match:
        fm_text = fm_match.group(1)
        tags_match = re.search(r'tags:\s*\[(.*?)\]', fm_text)
        if tags_match:
            meta["tags"] = [t.strip() for t in tags_match.group(1).split(',')]
        
        status_match = re.search(r'status:\s*(\w+)', fm_text)
        if status_match:
            meta["status"] = status_match.group(1).lower()

    # 2. Title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "No Title"

    # 3. Description (改善版)
    summary = extract_description(content)
    
    return {
        "title": title,
        "path": filepath,
        "meta": meta,
        "summary": summary
    }

def generate_catalog():
    catalog_data = {} 

    # ルートディレクトリから走査
    root_dir = "."
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 除外ディレクトリ
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        if TARGET_FILENAME in filenames:
            # カレントディレクトリのindex.mdはカタログ自体(README)なので除外
            if dirpath == ".":
                continue

            full_path = os.path.join(dirpath, TARGET_FILENAME)
            
            # パス分解 (例: 10_Network / Squid / index.md)
            # normpathでOSごとの区切り文字を正規化し、split
            rel_path = os.path.relpath(dirpath, ".")
            parts = rel_path.split(os.sep)

            # カテゴリ決定ロジックの修正
            # 第1階層 (10_Network) を常にカテゴリ名とする
            category = parts[0]
            
            # "10_Network/index.md" 自体は、そのカテゴリの目次ファイルなので
            # CATALOG.md のリストには「含めない」方針にする (重複排除)
            # もし含めたい場合は、この if 文を削除してください
            if len(parts) == 1 and TARGET_FILENAME in filenames:
                continue 

            data = parse_md_file(full_path)

            if category not in catalog_data:
                catalog_data[category] = []
            catalog_data[category].append(data)

    # Markdown生成
    lines = []
    lines.append("# 📚 Document Catalog")
    lines.append(f"\nLast Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("> このリストは `generate_catalog.py` によって自動生成されています。\n")

    for category in sorted(catalog_data.keys()):
        lines.append(f"## {category}\n")
        
        # カテゴリ内にアイテムがない場合 (ルートindexを除外した結果など)
        if not catalog_data[category]:
             lines.append(f"*See [{category}](./{category}/{TARGET_FILENAME}) for details.*\n")
             continue

        lines.append("| Status | Document | Tags | Description |")
        lines.append("| :---: | :--- | :--- | :--- |")
        
        for item in sorted(catalog_data[category], key=lambda x: x['title']):
            stat_str = item['meta']['status']
            icon = STATUS_ICONS.get(stat_str, "⚪")
            
            # Windowsパス対策の置換
            link_path = item['path'].replace("\\", "/")
            link = f"[{item['title']}]({link_path})"
            
            tags_str = " ".join([f"`{t}`" for t in item['meta']['tags']])
            
            lines.append(f"| {icon} {stat_str} | {link} | {tags_str} | {item['summary']} |")
        
        lines.append("\n")

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    
    print(f"✅ Generated {OUTPUT_FILENAME} successfully!")

if __name__ == "__main__":
    generate_catalog()
