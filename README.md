# 自治体職員向け 事務シミュレーション

農林水産省の日本型直接支払制度をはじめとする補助金・交付金事業の担当者向けに、  
実際の業務フローをロールプレイ形式で体験できる研修シミュレーションです。

---

## このリポジトリに含まれるもの

| ファイル / フォルダ | 内容 |
|-------------------|------|
| `simulation.html` | **環境保全型農業直接支払交付金** の研修シミュレーション本体 |
| `engine/` | 他の事業でも使える共通エンジン一式 |
| `.github/workflows/deploy.yml` | GitHub Pages 自動デプロイ設定 |

---

## シミュレーションを使う（研修を受ける）

### ブラウザで開くだけ（サーバー不要）

`simulation.html` をダウンロードしてブラウザで開くと、すぐに使えます。

```
simulation.html をダブルクリック → ブラウザで開く → 研修開始
```

### GitHub Pages で公開している場合

```
https://[組織名].github.io/[リポジトリ名]/simulation.html
```

---

## シミュレーションの内容（環境保全型農業直接支払交付金）

全 **8シーン・18問** のロールプレイ形式です。  
市役所農政課の新任担当者として、窓口相談から交付金支払いまでを体験します。

| シーン | 内容 | 形式 |
|--------|------|------|
| 事務フロー | 年間11ステップの事務の流れを確認 | 読むだけ |
| シーン１ | 農業者が窓口相談に来る（要件確認・組織要件） | 問題４問 |
| シーン２ | 書類受付・不備チェック・期限対応 | 問題３問 |
| シーン３ | 取組区分の確認・交付金額の計算 | 問題３問 |
| シーン４ | 審査中の判断事例（重複申請・組織要件・予算減額） | 問題３問 |
| シーン５ | 計画書提出から交付決定までの流れ | 読むだけ |
| シーン６ | 現地確認の実施・取組に問題があった場合の対応 | 問題２問 |
| シーン７ | 実施状況報告・証拠書類の確認・概算払いの流れ | 問題２問 |
| シーン８ | 支払証明の受理・実績報告書の県への提出 | 問題１問 |

### 主な機能

- **選択肢はランダム表示**：毎回違う順番で出題されます
- **全選択肢の解説を確認可能**：回答後、他の選択肢をクリックすると解説を読めます
- **前のシーンに戻れる**：各シーンのヘッダーから前へ戻れます
- **ホームにいつでも戻れる**：ヘッダーの「🏠 ホーム」ボタンから戻れます
- **チャプタージャンプ**：ホーム画面から特定のシーンへ直接移動できます
- **参考資料パネル**：交付単価表・申請要件・年間事務フロー表を常時参照できます

---

## 別の事業でシミュレーションを作る

### 仕組み

```
engine/scenes.js    ← シナリオデータ（事業ごとに差し替える）
      +
engine/engine.html  ← 共通UIエンジン（基本的に変更不要）
      ↓ build.py
dist/simulation.html ← 完成品（GitHub Pages で公開）
```

### 新しい事業のリポジトリを作る手順

#### 1. GitHub で新リポジトリを作成

例：`tabata-simulation`（中山間地域等直接支払）

#### 2. 以下のファイルをコピー

| コピー元（このリポジトリ） | コピー先（新リポジトリ） | 備考 |
|------------------------|---------------------|------|
| `engine/engine.html` | `engine/engine.html` | 変更不要 |
| `engine/build.py` | `engine/build.py` | 変更不要 |
| `.github/workflows/deploy.yml` | `.github/workflows/deploy.yml` | 変更不要 |
| `engine/scenes.js` | `engine/scenes.js` | **事業内容に書き換える** |

#### 3. scenes.js を事業内容で書き換える

`scenes.js` はシナリオデータの配列です。以下のテンプレートを参考に作成してください。

```javascript
[
  // ── 読むだけの説明画面 ──
  {
    id: "flow_overview",        // シーン固有ID（他と重複しないこと）
    type: "info",               // 'info' = 選択肢なし・「理解しました」ボタンのみ
    badge: "事務フロー",         // ヘッダーの短いラベル（10文字以内推奨）
    title: "年間事務の流れ",      // シーンのタイトル
    progress: 10,               // 進捗バーの割合（0〜100）
    progressLabel: "事務フロー", // 進捗バー横のテキスト
    content: `<div class="dialogue-area">
      <div class="narration">説明文...</div>
    </div>`,
    nextScene: "scene1a"        // 次のシーンID（最後のシーンは null）
  },

  // ── 選択問題のシーン ──
  {
    id: "scene1a",
    badge: "シーン１",
    title: "窓口相談（１）",
    progress: 25,
    progressLabel: "窓口相談",
    content: `<div class="dialogue-area">
      <div class="narration">状況説明...</div>
      <div class="character-block">
        <div class="character-avatar">👨‍🌾</div>
        <div class="character-info">
          <span class="character-name">農業者・田中さん</span>
        </div>
      </div>
      <div class="speech-bubble">「相談内容...」</div>
    </div>`,
    question: "どのように対応しますか？",
    choices: [
      {
        text: "選択肢Aのテキスト",
        correct: true,                  // 正解
        feedback: { title: "正解です！", body: "解説文..." }
      },
      {
        text: "選択肢Bのテキスト",
        correct: false,                 // 不正解
        feedback: { title: "不正解", body: "なぜ不正解かの解説..." }
      },
      {
        text: "選択肢Cのテキスト",
        correct: false,
        feedback: { title: "惜しい！", body: "解説..." }
      }
    ],
    nextScene: "scene1b"
  }
]
```

> **ポイント：**
> - `correct: true` の位置は先頭でも末尾でも構いません。表示はランダムになります
> - 選択肢は２〜４個が推奨です
> - `content` 内で使えるCSSクラスは下記「デザインクラス一覧」を参照

#### 4. ホーム画面のタイトル・チャプターリストを更新する

`engine/engine.html` の以下の箇所を事業に合わせて書き換えます。

```html
<!-- タイトル（約420行目） -->
<h2>ようこそ、農政課へ</h2>
<p>説明文...</p>

<!-- チャプターリスト（約443行目） -->
<div class="chapter-list">
  <button class="chapter-btn" onclick="jumpTo('flow_overview')">
    <span class="ch-badge info-badge">事務フロー</span>年間事務の流れを確認する
  </button>
  <button class="chapter-btn" onclick="jumpTo('scene1a')">
    <span class="ch-badge">シーン１</span>シーンのタイトル
  </button>
  <!-- 必要なシーン分だけ追加 -->
</div>
```

#### 5. ローカルでビルド・確認する

```bash
# ビルド実行
python3 engine/build.py
# → dist/simulation.html が生成される

# ブラウザで確認（サーバー不要）
# dist/simulation.html をダブルクリックして開く
```

#### 6. GitHub Pages を有効化する

1. リポジトリの **Settings → Pages** を開く
2. **Source** を `GitHub Actions` に設定する
3. `main` ブランチに push すると自動でビルド＆デプロイされる
4. デプロイ先URL： `https://[組織名].github.io/[リポジトリ名]/simulation.html`

---

## デザインクラス一覧

`content` フィールドで使えるCSSクラスです。

| クラス | 用途 | 例 |
|--------|------|---|
| `dialogue-area` | セリフ・ナレーション全体のラッパー | `<div class="dialogue-area">` |
| `narration` | 状況説明文（緑の左ボーダー） | `<div class="narration">令和７年４月...</div>` |
| `character-block` | キャラクター表示エリア | アバター＋名前をまとめる |
| `character-avatar` | キャラクターアイコン（絵文字推奨） | `<div class="character-avatar">👨‍🌾</div>` |
| `character-name` | キャラクター名バッジ | `<span class="character-name">田中さん</span>` |
| `character-role` | キャラクターの役職・説明 | `<span class="character-role">水稲農家</span>` |
| `speech-bubble` | セリフの吹き出し（白背景） | `<div class="speech-bubble">「...」</div>` |
| `speech-bubble player` | プレイヤーの思考（青背景） | `<div class="speech-bubble player">（確認すると...）</div>` |
| `flow-phase` | 事務フロー図のフェーズ区切り | `<div class="flow-phase">` |
| `flow-phase-label` | フェーズのラベル | 色クラスと組み合わせる |
| `phase-apply` | 申請フェーズの色（緑） | `<div class="flow-phase-label phase-apply">申請</div>` |
| `phase-report` | 報告フェーズの色（黄） | `phase-report` |
| `phase-result` | 精算フェーズの色（赤） | `phase-result` |
| `flow-steps` | フロー図のステップ群 | |
| `flow-step` | 個々のステップ行 | |
| `flow-step-num` | ステップ番号（丸バッジ） | `<div class="flow-step-num">1</div>` |
| `flow-step-title` | ステップのタイトル | |
| `flow-step-route` | 書類の流れ（矢印） | `農家 → 市 → 県` |
| `flow-step-note` | 期限などの注記（黄背景） | `⏰ ６月末まで` |
| `flow-step-desc` | ステップの説明文 | |

---

## ライセンス・利用について

本システムは自治体内部研修用として作成されています。  
制度の詳細・最新情報は農林水産省の公式資料をご確認ください。

- [環境保全型農業直接支払交付金（農林水産省）](https://www.maff.go.jp/j/seisan/kankyo/kakyou_chokubarai/mainp.html)
