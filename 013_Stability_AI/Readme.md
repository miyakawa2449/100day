# 日本語プロンプト対応画像生成スクリプト (Stability AI & OpenAI)

このプロジェクトは、日本語で入力されたプロンプトをOpenAI APIで英語に翻訳し、その翻訳結果を用いてStability AI APIで画像を生成するPythonスクリプトです。

## 概要

ユーザーが日本語で画像の内容を指示すると、スクリプト内部で以下の処理が行われます。
1.  OpenAI API (GPT-3.5 Turboなど) を利用して、入力された日本語プロンプトを英語に翻訳します。
2.  翻訳された英語プロンプトを元に、Stability AI API (Stable Diffusionなど) を利用して画像を生成します。
3.  生成された画像はローカルに保存されます。

これにより、英語のプロンプト作成に不慣れなユーザーでも、日本語で直感的に画像生成を試すことができます。

## 機能

* 日本語によるプロンプト入力
* OpenAI APIを利用したリアルタイム翻訳 (日本語 → 英語)
* Stability AI APIを利用したテキストからの画像生成
* APIキーの安全な管理 (.envファイル利用)
* 生成画像のローカル保存

## 必要なもの

### ソフトウェア
* Python 3.7 以降

### APIキー
* **Stability AI APIキー**: Stability AIプラットフォームから取得してください。
* **OpenAI APIキー**: OpenAIプラットフォームから取得してください。

### Pythonライブラリ
以下のPythonライブラリが必要です。
* `requests`
* `Pillow`
* `python-dotenv`
* `openai` (v1.0.0 以降)

これらのライブラリは、`requirements.txt`ファイルを使って一度にインストールできます（後述）。

## セットアップ

1.  **スクリプトの準備:**
    このリポジトリをクローンするか、提供されたPythonスクリプト（例: `generate_image_jp_openai.py`）をローカルディレクトリに保存します。

2.  **ライブラリのインストール:**
    ターミナルまたはコマンドプロンプトで、スクリプトがあるディレクトリに移動し、以下のコマンドを実行して必要なライブラリをインストールします。
    ```bash
    pip install requests Pillow python-dotenv openai
    ```
    または、以下の内容で `requirements.txt` ファイルを作成し、
    ```
    requests
    Pillow
    python-dotenv
    openai>=1.0.0
    ```
    次のコマンドでインストールすることも可能です。
    ```bash
    pip install -r requirements.txt
    ```

3.  **APIキーの設定 (.envファイル):**
    スクリプトと同じディレクトリに `.env` という名前のファイルを作成し、以下のようにご自身のAPIキーを記述します。

    ```env
    STABILITY_API_KEY=sk-your_stability_ai_api_key_here
    OPENAI_API_KEY=sk-your_openai_api_key_here
    ```
    **注意:** `.env` ファイルは機密情報を含むため、Gitリポジトリにコミットしないように `.gitignore` ファイルに `.env` を追加してください。

    `.gitignore` ファイルの例:
    ```
    .env
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
    ```

## 使い方

1.  ターミナルまたはコマンドプロンプトで、スクリプトが保存されているディレクトリに移動します。
2.  以下のコマンドを実行します（スクリプト名が `generate_image_jp_openai.py` の場合）。
    ```bash
    python generate_image_jp_openai.py
    ```
3.  実行すると、「生成したい画像のイメージを日本語で入力してください: 」というプロンプトが表示されるので、日本語で指示を入力し、Enterキーを押します。
4.  スクリプトが日本語プロンプトを英語に翻訳し、その結果を表示します。
5.  次に、翻訳された英語プロンプトを使ってStability AI APIで画像を生成します。
6.  成功すると、`generated_image_jp_en_1.png` のようなファイル名で画像がスクリプトと同じディレクトリに保存されます。

## コードのポイント (Pythonスクリプト内)

* **`load_dotenv()`**: `.env`ファイルから環境変数を読み込みます。
* **`client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)`**: OpenAI APIクライアントを初期化します。
* **`translate_to_english_with_openai(japanese_text)` 関数**:
    * 日本語のテキストを受け取り、OpenAIのChat Completions API (例: `gpt-3.5-turbo`) を使って英語に翻訳します。
    * 翻訳の品質を考慮し、システムプロンプトや`temperature`パラメータを設定しています。
* **`generate_image_with_stabilityai(english_prompt)` 関数**:
    * 翻訳済みの英語プロンプトを受け取り、Stability AI APIを呼び出して画像を生成します。
    * ペイロードには、プロンプトの他にネガティブプロンプトや各種生成パラメータ（`cfg_scale`, `steps`など）が含まれます。
    * 返された画像データ（base64形式）をデコードし、PNGファイルとして保存します。
* **エラーハンドリング**: 各API呼び出し部分には、基本的なエラーハンドリングが含まれています。

## 注意事項

* **APIキーの管理**: APIキーは機密情報です。絶対に公開リポジトリなどに直接書き込まないでください。`.env`ファイルと`.gitignore`を適切に使用して管理してください。
* **API利用料金**: OpenAI APIおよびStability AI APIの利用には、それぞれのサービスプロバイダが定める料金が発生する場合があります。無料枠や利用上限に注意してください。
* **翻訳の精度**: LLMによる翻訳は非常に高精度ですが、常に完璧とは限りません。特に画像生成のニュアンスが重要な場合、翻訳結果が意図通りか確認することが望ましいです。
* **エラーと制限**: ネットワークの問題、APIのレート制限、サーバー側のエラーなどにより、処理が失敗することがあります。スクリプトには基本的なエラーハンドリングが含まれていますが、より堅牢なアプリケーションを開発する場合は詳細なエラー処理が必要です。
* **生成時間**: 翻訳と画像生成の2つのAPI呼び出しがあるため、結果が得られるまでに多少時間がかかることがあります。

## ライセンス

このプロジェクトは [MITライセンス](LICENSE) の下で公開されています。（もしライセンスファイルを含める場合）
または、
このスクリプトはご自由にお使いいただけますが、利用は自己責任でお願いします。