# Google Colab と Flask/ngrok で動かすLLMチャットボット

このGoogle Colabノートブックは、大規模言語モデル（LLM）を使ったチャットボットを、WebサーバーフレームワークのFlask上で動作させ、さらにngrokを使って外部（インターネット）からアクセス可能にするサンプルプログラムです。

個人的な「ローカルLLM 100日チャレンジ」の4日目の成果物として作成しました。特に、前日（3日目）に試したローカルマシンでの実行と比較して、Google Colabの高性能GPU環境でどれだけ応答速度が改善するかを確認することを目的としていました。

## 主な機能

* Hugging Faceで公開されている様々なLLM（大規模言語モデル）を指定して利用可能（デフォルトは `rinna/llama-3-youko-8b` を使用）。
* シンプルなWebチャットインターフェースをFlaskで提供。
* ngrokを利用し、Colab上で実行しているチャットボットに外部からアクセスするための公開URLを生成。
* （任意）Google Driveをモデルのキャッシュ（一時保存場所）として利用し、2回目以降の起動時間を短縮。
* モデル名、キャッシュディレクトリ、ngrok設定などを変更可能。
* 基本的なエラーハンドリングとログ出力機能。

## 必要なもの

* **Google Colab:** Googleアカウントが必要です。大規模モデルを快適に動かすには、十分なGPUメモリを持つColab Pro（例: A100 GPU）の利用を推奨しますが、モデルサイズや設定によっては無料版でも動作する可能性があります。
* **ngrok アカウント:** **必須**です。無料プランで構いませんが、アカウント登録を行い、**認証トークン (Authtoken)** を取得する必要があります。
    * アカウント作成: [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
* **Google Drive (任意・推奨):** ダウンロードしたモデルを保存しておくキャッシュ機能を利用する場合に必要です。

## セットアップ手順

1.  **ngrok 認証トークンの取得:**
    * ngrokダッシュボードにログインします: [https://dashboard.ngrok.com/login](https://dashboard.ngrok.com/login)
    * 左側のメニューから「Your Authtoken」（または「Getting Started」>「Your Authtoken」）を選択し、表示された認証トークンをコピーします。

2.  **Colab シークレットの設定:**
    * このColabノートブックを開きます。
    * 左側のサイドバーにある**鍵のアイコン (🔑 Secrets)** をクリックします。
    * 「**+ 新しいシークレットを追加**」をクリックします。
    * **名前**（Name）に `NGROK_AUTHTOKEN` と入力します（コード内でこの名前を使用しています）。
    * **値**（Value）に、先ほどコピーしたngrok認証トークンを貼り付けます。
    * **ノートブックのアクセス権**（Notebook access）のトグルスイッチを**オン**にします。
    * 「**保存**」をクリックします。

3.  **Google Drive へのアクセス許可 (キャッシュ利用時):**
    * キャッシュ機能 (`USE_GOOGLE_DRIVE_CACHE = True`) を有効にしてセル3を実行すると、ColabからGoogle Driveへのアクセス許可を求めるポップアップが表示されます。画面の指示に従って許可してください。
    * ノートブックは、設定されたキャッシュディレクトリ (`MODEL_DIR`) が存在しない場合、自動的に作成しようとします。

## 設定項目

ノートブックを実行する前に、必要に応じて **セル2** の設定項目を調整してください。

* `MODEL_NAME`: 使用するHugging Faceモデルの名前を指定します（例: `"elyza/ELYZA-japanese-Llama-2-7b-instruct"`）。モデルによって推奨されるプロンプト形式が異なる場合があるのでご注意ください。
* `MODEL_DIR`: モデルキャッシュを保存するGoogle Drive内のパスを指定します。
* `NGROK_SECRET_NAME`: Colabシークレットに登録した認証トークンの名前 (`"NGROK_AUTHTOKEN"`)。
* `FLASK_PORT`: Flaskサーバーが使用するポート番号（ngrokはこのポートへのトンネルを作成します）。
* `USE_GOOGLE_DRIVE_CACHE`: Google Driveキャッシュを使用する場合は `True`、しない場合は `False` に設定します。

## 実行方法

ノートブックのセルを**上から順番に**実行してください。

1.  **セル1: ライブラリのインストール:** 必要なPythonライブラリをインストールします。
2.  **セル2: インポートと設定:** モジュールをインポートし、設定変数を読み込みます。
3.  **セル3: Google Driveのマウント:** Google Driveをマウントします（キャッシュ利用時）。初回実行時には認証が必要です。
4.  **セル4: ngrok認証トークンの設定:** Colabシークレットからトークンを読み込み、ngrokに設定します。
5.  **セル5: モデルとトークナイザーの準備:** 指定されたモデルとトークナイザーをHugging Face Hubからダウンロード、またはGoogle Driveキャッシュからロードします。**（注意：初回ダウンロードや大規模モデルの場合、完了までに時間がかかることがあります）**
6.  **セル6: Flaskアプリの定義:** Webサーバーのルート（`/` と `/chat`）を定義します。
7.  **セル7: ngrok起動 & Flask実行:**
    * ngrokトンネルを起動します。ログに **公開URL**（例: `https://xxxx-xxxx-xxxx.ngrok-free.app`）が出力されるのを待ちます。
    * Flaskウェブサーバーを起動します。
    * **（重要）このセルはウェブサーバーが動作している間、実行が完了せず「実行中」の状態が続きます。** ログに `* Serving Flask app '__main__'` と表示されれば、サーバーは正常に起動しています。
  * 
## チャットボットへのアクセス方法

1.  セル7の実行ログに表示された **ngrokの公開URL** (`https://...`) をコピーします。
2.  お使いのWebブラウザ（Chrome、Firefox、Edgeなど）で新しいタブを開き、コピーしたURLをアドレスバーに貼り付けてアクセスします。
3.  チャットインターフェースが表示されたら、メッセージを入力してAIとの対話を開始できます。

## サーバーの停止方法

チャットボットの利用が終わったら、以下の方法でサーバーを停止してください。

1.  Colabノートブックに戻ります。
2.  実行中の **セル7 の左側にある停止ボタン (■)** をクリックします。
3.  または、Colabの上部メニューから「**ランタイム**」>「**実行を中断**」を選択します。
4.  これにより、Flaskサーバーが停止し、ngrokトンネルも切断されます。

## 注意点・トラブルシューティング

* **GPUメモリ不足:** 大規模モデル（8Bパラメータなど）は多くのGPUメモリ（VRAM）を必要とします。セル5で「Out of Memory」エラーが発生する場合は、より小さいモデルに変更するか、量子化（セル5のコメントアウト部分参照）を試す、あるいはColab Proなどのより高性能な環境を利用することを検討してください。
* **ライブラリの依存関係:** Colab環境では、ライブラリ間のバージョン互換性問題が発生することがあります。インストール後に予期せぬエラー（`AttributeError`, `ImportError`など）が発生した場合は、一度「ランタイム」>「ランタイムを再起動」を実行し、セル1から全てのセルを再実行してみてください。場合によっては、セル1でライブラリのバージョンを明示的に指定する必要があるかもしれません。
* **モデルの応答:** LLMの応答は、モデルや入力によって不安定になることがあります。繰り返しが多い、無関係な内容を話す、などの場合は、セル6の `model.generate()` のパラメータ（`temperature`, `repetition_penalty` など）を調整したり、システムプロンプトを追加したりすることで改善する可能性があります。
* **ngrok無料プラン:** 無料版のngrokには、URLが毎回変わる、同時接続数に制限があるなどの制約があります。

## 作成者・文脈

このノートブックは、「宮川」が "100 Day LLM Challenge" の一環として作成しました。[https://miyakawai.com/2025/05/03/colab-gpu-llm-day4/ - MIYAKAWA AI]

## ライセンス

MIT License
