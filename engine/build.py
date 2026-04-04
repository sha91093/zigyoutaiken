"""
シミュレーションビルドスクリプト
engine.html の /*SCENES_DATA*/ プレースホルダーを scenes.js の内容で置換し、
dist/simulation.html を生成する。
"""

import os
import sys

ENGINE_FILE = os.path.join(os.path.dirname(__file__), 'engine.html')
SCENES_FILE = os.path.join(os.path.dirname(__file__), 'scenes.js')
DIST_DIR    = os.path.join(os.path.dirname(__file__), '..', 'dist')
OUTPUT_FILE = os.path.join(DIST_DIR, 'simulation.html')

PLACEHOLDER = '/*SCENES_DATA*/'


def build():
    # engine.html 読み込み
    if not os.path.exists(ENGINE_FILE):
        print(f'ERROR: {ENGINE_FILE} が見つかりません', file=sys.stderr)
        sys.exit(1)
    with open(ENGINE_FILE, encoding='utf-8') as f:
        engine = f.read()

    if PLACEHOLDER not in engine:
        print(f'ERROR: {PLACEHOLDER} が engine.html に見つかりません', file=sys.stderr)
        sys.exit(1)

    # scenes.js 読み込み
    if not os.path.exists(SCENES_FILE):
        print(f'ERROR: {SCENES_FILE} が見つかりません', file=sys.stderr)
        sys.exit(1)
    with open(SCENES_FILE, encoding='utf-8') as f:
        scenes = f.read().rstrip('\n')  # 末尾の余分な改行を除去

    # プレースホルダー置換
    output = engine.replace(PLACEHOLDER, scenes)

    # dist ディレクトリ作成
    os.makedirs(DIST_DIR, exist_ok=True)

    # simulation.html 出力
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'✅ ビルド完了: {OUTPUT_FILE}')

    # index.html（ルートURLへのリダイレクト）を生成
    index_file = os.path.join(DIST_DIR, 'index.html')
    redirect_html = '<!DOCTYPE html><html><head><meta charset="UTF-8">' \
        '<meta http-equiv="refresh" content="0;url=simulation.html">' \
        '<title>リダイレクト中...</title></head>' \
        '<body><a href="simulation.html">simulation.html へ移動</a></body></html>\n'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(redirect_html)

    print(f'✅ リダイレクト生成: {index_file}')


if __name__ == '__main__':
    build()
