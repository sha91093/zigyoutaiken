# 事務シミュレーション エンジン

自治体職員向け事務シミュレーションの共通エンジンです。  
`scenes.js` を差し替えるだけで、異なる事業のシミュレーションを作成できます。

---

## ファイル構成

```
engine/
  engine.html   共通UIエンジン（基本的に変更不要）
  scenes.js     シナリオデータ（事業ごとに作成する）
  build.py      ビルドスクリプト
.github/
  workflows/
    deploy.yml  GitHub Actions 自動デプロイ設定
dist/
  simulation.html  ビルド成果物（GitHub Pagesで公開される）
```

---

## 新しい事業のシミュレーションを作る手順

### 1. リポジトリを作成する

GitHub で新しいリポジトリを作成します。  
例: `tabata-simulation`（中山間地域等直接支払）

### 2. ファイルをコピーする

以下のファイルを新リポジトリにコピーします。

```
engine/engine.html      → そのままコピー（変更不要）
engine/build.py         → そのままコピー（変更不要）
engine/scenes.js        → 事業内容に合わせて書き換える ★
.github/workflows/deploy.yml → そのままコピー（変更不要）
```

### 3. scenes.js を書き換える

`scenes.js` はシナリオデータの配列です。以下の構造に従って作成します。

```javascript
[
  // ── 読むだけの説明画面（type: 'info'）──
  {
    id: "flow_overview",          // シーン固有のID（他と重複しないこと）
    type: "info",                 // 'info' = 選択肢なし・読んで次へ
    badge: "事務フロー",           // ヘッダーに表示する短いラベル
    title: "年間事務の流れ",        // シーンのタイトル
    progress: 10,                  // 進捗バーの割合（0〜100）
    progressLabel: "事務フロー",   // 進捗バー横のテキスト
    content: `<div>...</div>`,    // 表示するHTML（テンプレートリテラル使用可）
    nextScene: "scene1a"           // 次のシーンID（null で終了）
  },

  // ── 選択問題のシーン ──
  {
    id: "scene1a",
    badge: "シーン１",
    title: "窓口相談（１）",
    progress: 25,
    progressLabel: "窓口相談",
    content: `<div class="dialogue-area">...</div>`,
    question: "どのように対応しますか？",  // 質問文
    choices: [
      {
        text: "選択肢Aのテキスト",
        correct: true,                   // 正解は true、不正解は false
        feedback: {
          title: "正解です！",
          body: "解説文。HTMLタグ使用可。"
        }
      },
      {
        text: "選択肢Bのテキスト",
        correct: false,
        feedback: {
          title: "不正解",
          body: "なぜ不正解かの解説。"
        }
      }
    ],
    nextScene: "scene1b"
  }
]
```

> 💡 **選択肢の並び順はランダム表示されます。** `correct: true` の位置を気にせず書けます。  
> 💡 **戻るボタン・ホームボタン**は自動で表示されます。追加作業不要です。

---

### 4. ホーム画面のチャプターリストを更新する

`engine.html` の以下の部分を事業内容に合わせて書き換えてください。

```html
<!-- engine.html の 432行目あたり -->
<h2>ようこそ、農政課へ</h2>
<p>説明文...</p>
<button class="start-btn" onclick="startSimulation()">最初から始める</button>

<div class="chapter-menu">
  ...チャプターボタンを事業に合わせて追加...
</div>
```

---

### 5. GitHub Pages を有効化する

1. リポジトリの **Settings → Pages** を開く
2. **Source** を `GitHub Actions` に設定
3. `main` ブランチに push すると自動でビルド・デプロイされる
4. `https://[組織名].github.io/[リポジトリ名]/simulation.html` でアクセス可能

---

## ローカルでビルドする

```bash
python3 engine/build.py
# → dist/simulation.html が生成される
```

ブラウザで `dist/simulation.html` を直接開いて動作確認できます（サーバー不要）。

---

## content フィールドで使えるHTMLクラス

| クラス | 用途 |
|--------|------|
| `dialogue-area` | セリフ・ナレーションのエリア |
| `narration` | 状況説明文（緑の左ボーダー付き） |
| `character-block` | キャラクター（アバター＋名前）のブロック |
| `character-avatar` | キャラクターのアイコン（絵文字推奨） |
| `character-name` | キャラクター名のバッジ |
| `speech-bubble` | セリフの吹き出し |
| `speech-bubble player` | プレイヤー自身のセリフ（青背景） |
| `flow-phase` | 事務フロー図のフェーズブロック |
| `flow-steps` | フロー図のステップリスト |
| `flow-step` | 個々のステップ |
