# Craft Coffee & Goods (ECサイト Webアプリケーション)

Python + Django + PostgreSQL を用いた、ポートフォリオ用のECサイトWebアプリケーションです。  
実務を意識した設計方針に基づき、**トランザクション管理によるデータ整合性（在庫の原子性）**、**IDOR防止によるアクセス制御セキュリティ**、**セッションベースのカート**、**厳格な入力バリデーション**、**全自動テストスイート（20件）** を備えています。

---

## 🌟 主な機能一覧

### 1. 商品管理 & カタログ（Products）
- **商品一覧 & 詳細表示**: 画像、価格、在庫数、商品説明の閲覧
- **在庫切れ制御**: 在庫ゼロ時の「SOLD OUT」バッジ表示およびカート追加ボタンの自動非活性化
- **No-Imageフォールバック**: 商品画像が未登録の場合でも崩れないデフォルト画像表示
- **Django Admin管理**: 管理画面からの商品登録・編集・在庫の一括更新（`list_editable`）

### 2. ユーザー認証（Accounts）
- **会員登録（SignUp）**: ユーザー名・メールアドレス（必須）・パスワードによる登録と登録直後の自動ログイン
- **ログイン / ログアウト**: Django標準認証システムと安全なセッション管理
- **ログイン状態に応じたヘッダー表示**: ナビゲーションメニューの動的切り替え

### 3. セッションカート（Orders）
- **DBを圧迫しないセッション管理**: 未ログイン状態でも利用可能なカート機能
- **数量変更 & 削除**: カート内での数量ドロップダウン更新、個別削除
- **ヘッダーバッジ**: コンテキストプロセッサによるカート内合計点数のリアルタイム表示
- **サーバー側在庫上限ガード**: 在庫数を超えるカート追加・数量変更のサーバー側拒否

### 4. チェックアウト & 注文処理（Orders）
- **`transaction.atomic()` によるデータ整合性**:
  - 注文レコード（`Order`）作成
  - 在庫引き落とし（`Product.stock` の減算）
  - 注文明細レコード（`OrderItem`）作成
  - カート内データの完全クリア
  - ※上記を単一トランザクションで実行し、在庫不足等の異常時は完全ロールバック
- **購入時単価スナップショット**: 商品マスタの将来の価格改定に影響されないよう、購入確定時の単価を `OrderItem.price` に独立保持

### 5. 注文履歴 & セキュリティ（Orders）
- **注文履歴一覧**: ログインユーザー本人の過去の注文一覧表示
- **注文詳細画面**: お届け先、購入時スナップショット単価、合計金額、注文番号の確認
- **【IDOR対策】所有者アクセス制御**: 他ユーザーの注文詳細URLに直接アクセス（URLパラメータ改ざん）された場合、存在有無を悟らせず `404 Not Found` を返却

### 6. バリデーション & エラーハンドリング
- **郵便番号バリデーション & 自動正規化**: ハイフンなし7桁入力（`1234567`）を `123-4567` 形式へ自動補完
- **フラッシュメッセージ通知**: 成功（緑）、エラー（赤）、注意（黄）のユーザーフィードバック
- **カスタムエラーページ**: `404 Not Found` および `500 Server Error` 専用のエラーデザイン画面

---

## 🛠 技術スタック

| カテゴリ | 使用技術 |
| :--- | :--- |
| **バックエンド** | Python 3.12, Django 5.x |
| **データベース** | PostgreSQL, `psycopg2-binary` |
| **フロントエンド** | HTML5, Vanilla CSS3 (CSS Grid / Flexbox, レスポンシブ対応), Google Fonts (Noto Sans JP) |
| **環境変数管理** | `python-dotenv` (.env) |
| **画像処理** | Pillow |
| **テストフレームワーク** | Django TestCase (`python manage.py test`) |
| **バージョン管理** | Git / GitHub |

---

## 💡 設計・こだわりのポイント

1. **トランザクション整合性と在庫の排他性**
   - チェックアウト時に `with transaction.atomic():` を適用し、複数商品の在庫引き落としと注文データの保存を一括処理。途中で在庫不足等の例外が発生した場合はすべての変更が自動ロールバックされ、データ不整合を防ぎます。
2. **厳格なアクセス制御（IDOR対策）**
   - 注文詳細ビューにおいて、単なる主キー取得ではなく `get_object_or_404(Order, order_number=order_number, user=request.user)` を実行。URL直接入力による他人の注文情報閲覧を確実にブロックします。
3. **セッションを活用した高効率なカート設計**
   - カート情報をデータベースではなくセッション（Cookie/セッションストレージ）で管理することで、DBアクセスを最小限に抑え、快適なUXを実現しています。
4. **20件の全自動テスト（All Green）**
   - モデルのプロパティ判定から、認証フロー、トランザクション時の在庫減算・ロールバック、IDOR対策に至るまで、全20件のテストケースを実装しコードの品質を担保しています。

---

## 🚀 ローカル環境の立ち上げ手順

### 1. リポジトリのクローン
```bash
git clone <your-repository-url>
cd ecommerce
```

### 2. 仮想環境の作成と有効化
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. 依存ライブラリのインストール
```powershell
pip install -r requirements.txt
```

### 4. 環境変数ファイル（.env）の作成
`.env.example` をコピーして `.env` を作成し、ローカルのPostgreSQL接続情報を設定します。

```ini
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. データベースのセットアップ & マイグレーション
PostgreSQLに `ecommerce_db` を作成後、マイグレーションを実行します。

```powershell
python manage.py migrate
```

### 6. 管理者ユーザーの作成（任意）
```powershell
python manage.py createsuperuser
```

### 7. 自動テストの実行
すべてのテストが正常に通過することを確認します。

```powershell
python manage.py test
```

### 8. 開発サーバーの起動
```powershell
python manage.py runserver
```
ブラウザで `http://127.0.0.1:8000/` を開くとアプリケーションが表示されます。  
管理画面は `http://127.0.0.1:8000/admin/` よりアクセスできます。

---

## 🧪 テスト構成（全20ケース）

- **`products`**:
  - `ProductModelTest`: `__str__` 表記、`is_in_stock` 在庫プロパティ検証
  - `ProductViewTest`: 公開商品の表示、非公開商品（`is_active=False`）の除外、404ハンドリング
- **`accounts`**:
  - `SignUpViewTest`: 正常登録と自動ログイン、メールアドレス必須チェック、パスワード不一致チェック
  - `AuthFlowTest`: ログイン成功・失敗、ログアウト
- **`orders`**:
  - `CartSessionTest`: カート追加・数量更新・削除・合計金額計算
  - `CheckoutTransactionTest`: 認証必須ガード、`transaction.atomic` 在庫引き落とし・価格スナップショット保存、在庫不足時ロールバック
  - `OrderAccessSecurityTest`: 自分の注文のみの履歴表示、**他人の注文番号アクセス時のIDOR防止（404 Not Found）**

---

## 🔮 今後の改善・拡張予定（Future Improvements）
- **厳格な行ロック**: トラフィック増大時に備えた `select_for_update()` の導入
- **外部決済連携**: Stripe等の決済代行サービスAPIとの連携
- **注文ステータス管理**: 発送準備中・発送済み・キャンセルなどの配送ステータス管理
- **商品検索・フィルタリング**: キーワード検索やカテゴリ絞り込み機能の追加
