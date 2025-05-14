import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import os

# --- アプリケーション設定 ---
API_URL = "http://127.0.0.1:7860"  # Stable Diffusion Web UI のアドレスとポート
IMG2IMG_ENDPOINT = f"{API_URL}/sdapi/v1/img2img"

# --- スタイル定義 ---
STYLES = {
    "水彩画風": {
        "base_prompt": "masterpiece, best quality, beautiful watercolor painting, soft lighting, vibrant colors, artistic, dreamy",
        "negative_prompt_suffix": "photo, realistic, 3d, ugly",
        "requires_lora": False,
        "default_denoising_strength": 0.7,
        "default_steps": 30,
        "default_cfg_scale": 7.0,
    },
    "ドラゴンボール風": {
        "base_prompt": "masterpiece, best quality, dynamic action pose, vibrant colors, bold outlines, manga style, anime screencap",
        "negative_prompt_suffix": "photorealistic, realistic, 3d render, watermark, signature",
        "requires_lora": True,
        "lora_suggestion": {"name": "DragonBall.safetensors", "trigger": "Dragon Ball style", "weight": 0.8}, # LoRA名は例です
        "default_denoising_strength": 0.70,
        "default_steps": 35,
        "default_cfg_scale": 7.5,
    },
    "油絵風": {
        "base_prompt": "masterpiece, best quality, beautiful oil painting, textured brush strokes, rich impasto, classical art",
        "negative_prompt_suffix": "anime, cartoon, photorealistic, blurry",
        "requires_lora": False,
        "default_denoising_strength": 0.65,
        "default_steps": 40,
        "default_cfg_scale": 7.0,
    },
    "アニメスケッチ風": {
        "base_prompt": "masterpiece, best quality, anime sketch, monochrome, detailed lines, rough sketch, concept art, dynamic lines",
        "negative_prompt_suffix": "color, painting, photorealistic, 3d",
        "requires_lora": False,
        "default_denoising_strength": 0.75,
        "default_steps": 25,
        "default_cfg_scale": 6.5,
    },
    "写真風リアリスティック": {
        "base_prompt": "photorealistic, ultra realistic, masterpiece, best quality, detailed skin texture, sharp focus, 8k uhd, professional photography, natural lighting",
        "negative_prompt_suffix": "anime, cartoon, painting, illustration, blurry, lowres, watermark, signature, ugly, deformed",
        "requires_lora": False, # 高品質なリアル系ベースモデルの使用を推奨
        "default_denoising_strength": 0.35, # 元の画像の特徴を強く残す
        "default_steps": 30,
        "default_cfg_scale": 7.0,
    },
    "サイバーパンク風": {
        "base_prompt": "masterpiece, best quality, cyberpunk city, neon lights, futuristic, dystopian, techwear, cinematic lighting",
        "negative_prompt_suffix": "fantasy, historical, ugly, deformed",
        "requires_lora": False,
        "default_denoising_strength": 0.7,
        "default_steps": 35,
        "default_cfg_scale": 7.0,
    }
}

# --- サンプラー定義 ---
SAMPLERS_INFO = [
    {"name": "Euler a", "description": "高速。創造的で多様な結果。ステップ数が少なくても機能。ややソフトな仕上がり。"},
    {"name": "Euler", "description": "Euler aよりプロンプトに忠実。ステップ増でディテール向上。"},
    {"name": "LMS", "description": "Eulerと似ているが良い結果が得られることも。"},
    {"name": "Heun", "description": "Eulerより高品質だが遅い。高ステップ数で効果的。"},
    {"name": "DPM2", "description": "LMSより高品質でHeunより速いことがある。"},
    {"name": "DPM2 a", "description": "Euler aに似た特性を持つが、より高品質な場合がある。"},
    {"name": "DPM++ 2S a", "description": "高品質。'a' (ancestral) は創造性が高め。ステップ数がある程度必要。"},
    {"name": "DPM++ 2M", "description": "非常に人気。高品質で安定した結果を出すことが多い。"},
    {"name": "DPM++ SDE", "description": "非常に高品質だが計算コスト高。ランダム性が高い。"},
    {"name": "DPM fast", "description": "高速生成向け。品質は他のDPM系より劣る場合がある。"},
    # {"name": "DPM adaptive", "description": "ステップ数を自動調整しようとする。結果は不安定なことも。"}, # 環境によりない場合も
    {"name": "LMS Karras", "description": "LMSにKarrasノイズスケジュールを適用。品質向上に寄与。"},
    {"name": "DPM2 Karras", "description": "DPM2にKarrasノイズスケジュールを適用。"},
    {"name": "DPM2 a Karras", "description": "DPM2 aにKarrasノイズスケジュールを適用。"},
    {"name": "DPM++ 2S a Karras", "description": "DPM++ 2S aにKarrasノイズスケジュールを適用。非常に高品質。"},
    {"name": "DPM++ 2M Karras", "description": "DPM++ 2MにKarrasノイズスケジュールを適用。定番かつ高品質。"},
    {"name": "DPM++ SDE Karras", "description": "DPM++ SDEにKarrasノイズスケジュールを適用。最高品質を狙えるが重い。"},
    {"name": "DDIM", "description": "高速で安定。ステップ数が少なくても機能。同じシードで同じ結果。"},
    # {"name": "PLMS", "description": "DDIMの旧版のような位置づけ。現在はDDIMが主流。"}, # 環境によりない場合も
    {"name": "UniPC", "description": "比較的新しい。少ないステップ数で高品質な画像を生成できるとされる。"},
]
AVAILABLE_SAMPLER_NAMES = [s["name"] for s in SAMPLERS_INFO]

# --- API通信と画像処理関数 ---
def encode_image_to_base64_streamlit(uploaded_file):
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            return base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            st.error(f"エラー: 画像のエンコード中に問題が発生しました: {e}")
            return None
    return None

def decode_base64_to_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        st.error(f"エラー: 画像のデコード中に問題が発生しました: {e}")
        return None

def convert_image_style_api(init_image_base64, prompt, negative_prompt="", denoising_strength=0.75,
                            sampler_name="Euler a", steps=30, cfg_scale=7, seed=-1,
                            width=None, height=None):
    payload = {
        "init_images": [init_image_base64],
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength,
        "sampler_name": sampler_name,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "width": width,
        "height": height,
    }
    # st.write("--- 送信するペイロード (デバッグ用) ---")
    # st.json(payload)
    # st.write("------------------------")

    api_response_object = None
    try:
        api_response_object = requests.post(IMG2IMG_ENDPOINT, json=payload, timeout=300) # タイムアウトを長めに設定
        api_response_object.raise_for_status()
        r = api_response_object.json()
        if 'images' in r and r['images']:
            return r['images'][0]
        else:
            st.error(f"エラー: APIレスポンスに画像データがありません。レスポンス: {r}")
            return None
    except requests.exceptions.Timeout:
        st.error(f"エラー: APIリクエストがタイムアウトしました (接続先: {IMG2IMG_ENDPOINT})。サーバーの処理に時間がかかっているか、応答がありません。")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"エラー: API接続/リクエスト失敗 (接続先: {IMG2IMG_ENDPOINT}): {e}")
        if api_response_object is not None:
            st.error(f"ステータスコード: {api_response_object.status_code}")
            try:
                st.error(f"エラー詳細: {api_response_object.json()}")
            except json.JSONDecodeError:
                st.error(f"エラー詳細 (非JSON): {api_response_object.text}")
        else:
            st.error("APIサーバーへの接続自体に失敗した可能性があります。Stable Diffusion Web UIが起動しているか、API設定、ポート番号が正しいか確認してください。")
        return None
    except Exception as e:
        st.error(f"予期せぬAPIエラー: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="画像スタイル変換 v1.0")

st.title("🎨 画像スタイル変換 v1.0")
st.caption("ローカルのStable Diffusion Web UIを使って、アップロードした画像を様々なスタイルに変換します。")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 詳細パラメータ設定")
    # api_url_input = st.text_input("API URL (変更する場合)", value=API_URL) # 上部の定数を参照
    # IMG2IMG_ENDPOINT = f"{api_url_input}/sdapi/v1/img2img" # 動的に変更したい場合

    # スタイル選択に応じてデフォルト値を変更するため、ここでは定義のみ
    # 実際の値設定はメインコンテンツのスタイル選択後に行う
    steps_default = 30
    cfg_scale_default = 7.0

    # スタイルが選択されたら、そのデフォルト値を反映できるようにするため、
    # keyを設定して、メイン処理でst.session_state経由で更新することを検討
    # または、スタイル選択後にこれらのウィジェットを描画する
    # ここではまず固定のデフォルトで表示し、スタイルデータで上書きする例はメインコンテンツ側で行う

    steps = st.slider("ステップ数 (Steps)", 10, 150, steps_default, 5,
                    help="画像生成時のノイズ除去ステップ数。多いほど細かく描画されますが時間もかかります。通常20～50程度。スタイルによって推奨値が変わることがあります。")
    cfg_scale = st.slider("CFGスケール (CFG Scale)", 1.0, 30.0, cfg_scale_default, 0.5,
                        help="プロンプトへの忠実度。値が高いほどプロンプトに厳密に従いますが、高すぎると色が濃すぎたり破綻することがあります。通常7～12程度。")
    seed = st.number_input("シード値 (Seed)", value=-1, step=1,
                        help="画像生成の乱数シード。-1でランダム。同じシード値と同じパラメータなら同じ画像が（ほぼ）生成されます。")

    selected_sampler_name_sidebar = st.selectbox("サンプラー (Sampler)",
                                        options=AVAILABLE_SAMPLER_NAMES,
                                        index=AVAILABLE_SAMPLER_NAMES.index("DPM++ 2M Karras") if "DPM++ 2M Karras" in AVAILABLE_SAMPLER_NAMES else 0,
                                        help="画像生成のノイズ除去アルゴリズム。品質や生成速度、絵のタッチに影響します。")

    for sampler_info in SAMPLERS_INFO:
        if sampler_info["name"] == selected_sampler_name_sidebar:
            st.caption(f"**{selected_sampler_name_sidebar}**: {sampler_info['description']}")
            break

# --- メインコンテンツエリア ---
col1, col2 = st.columns(2)

with col1:
    st.header("🖼️ 入力画像とスタイル設定")
    uploaded_file = st.file_uploader("1. 変換したい画像をアップロード", type=["png", "jpg", "jpeg", "webp"])

    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)
        st.image(input_image, caption="アップロードされた画像", use_column_width=True)
        original_width, original_height = input_image.size
        st.write(f"元画像のサイズ: {original_width}x{original_height}")

        st.subheader("2. スタイルを選択")
        style_name = st.selectbox("適用するスタイル", options=list(STYLES.keys()), key="style_selector")
        selected_style_data = STYLES[style_name]

        st.subheader("3. プロンプトとスタイルの強さを調整")
        subject_prompt = st.text_input("被写体の説明 (例: 'a cute cat', 'a beautiful mountain landscape')",
                                    key=f"subject_{style_name}")

        base_prompt_default = selected_style_data.get("base_prompt", "")
        base_prompt_user_edit = st.text_area("基本プロンプト (編集可)",
                                            value=base_prompt_default, height=100, key=f"base_prompt_{style_name}")

        full_prompt = f"{subject_prompt}, {base_prompt_user_edit}" if subject_prompt else base_prompt_user_edit

        common_negative_prompt = "worst quality, low quality, normal quality, blurry, ugly, deformed, text, watermark, signature, extra limbs, disfigured, malformed_hands, bad_anatomy"
        style_negative_suffix = selected_style_data.get("negative_prompt_suffix", "")
        full_negative_prompt_default = f"{common_negative_prompt}, {style_negative_suffix}".strip(", ")
        negative_prompt = st.text_area("ネガティブプロンプト (編集可)",
                                    value=full_negative_prompt_default, height=100,  key=f"neg_prompt_{style_name}")

        # Denoising Strength (スタイルごとのデフォルト値を設定)
        # サイドバーの Steps, CFG Scale もスタイルに応じてデフォルトを変えたい場合は同様のロジックが必要
        default_denoising = selected_style_data.get("default_denoising_strength", 0.75)
        denoising_strength = st.slider("Denoising Strength (スタイルの強さ)", 0.0, 1.0, default_denoising, 0.05, key=f"denoising_{style_name}",
                                    help="値が高いほどプロンプトやスタイルの影響が強くなり、元の画像から大きく変化します。低いと元の画像の特徴が多く残ります。")

        # スタイル特有の入力 (LoRAが必要な場合)
        if selected_style_data.get("requires_lora"):
            st.info(f"このスタイル「{style_name}」はLoRAモデルの使用を推奨します。")
            lora_suggestion = selected_style_data.get("lora_suggestion", {})
            lora_name = st.text_input("LoRAファイル名 (例: your_lora.safetensors)",
                                    value=lora_suggestion.get("name", ""), key=f"lora_name_{style_name}",
                                    help="Stable Diffusion Web UIの models/Lora フォルダ内にあるファイル名を指定してください。")
            lora_trigger_word = st.text_input("LoRAトリガーワード (LoRA使用時の起動呪文)",
                                            value=lora_suggestion.get("trigger", ""), key=f"lora_trigger_{style_name}")
            lora_weight_default = lora_suggestion.get("weight", 0.8)
            lora_weight = st.slider("LoRAの重み", 0.0, 2.0, lora_weight_default, 0.1, key=f"lora_weight_{style_name}")

            if lora_name and lora_trigger_word: # LoRA名とトリガーワードが入力されたらプロンプトに追加
                lora_prompt_name = os.path.splitext(lora_name)[0] # 拡張子なし
                full_prompt += f", {lora_trigger_word}, <lora:{lora_prompt_name}:{lora_weight}>"
            elif lora_name and not lora_trigger_word:
                st.warning("LoRAファイル名が入力されていますが、トリガーワードが空です。LoRAが正しく適用されない可能性があります。")


        st.subheader("4. 変換実行")
        if st.button("🎨 スタイル変換実行！", type="primary", use_container_width=True):
            base64_image = encode_image_to_base64_streamlit(uploaded_file)
            if base64_image:
                with st.spinner("画像を変換中です...しばらくお待ちください..."):
                    # サイドバーで設定されたパラメータを使用
                    current_steps = steps # サイドバーのst.sliderから最新の値を取得
                    current_cfg_scale = cfg_scale
                    current_seed = seed
                    current_sampler_name = selected_sampler_name_sidebar

                    # スタイル定義にデフォルトのstepsやcfg_scaleがあればそれを使う（オプション）
                    # current_steps = selected_style_data.get("default_steps", steps)
                    # current_cfg_scale = selected_style_data.get("default_cfg_scale", cfg_scale)


                    generated_image_base64 = convert_image_style_api(
                        base64_image,
                        full_prompt,
                        negative_prompt=negative_prompt,
                        denoising_strength=denoising_strength,
                        sampler_name=current_sampler_name,
                        steps=current_steps,
                        cfg_scale=current_cfg_scale,
                        seed=current_seed,
                        width=original_width,
                        height=original_height
                    )

                if generated_image_base64:
                    st.session_state.generated_image_base64 = generated_image_base64
                    st.session_state.download_image_bytes = decode_base64_to_image(generated_image_base64) # Pillow Imageとして保持
                    st.success("画像変換が完了しました！右側に結果が表示されます。")
                else:
                    st.error("画像変換に失敗しました。エラーメッセージを確認してください。")
            else:
                st.warning("まず画像をアップロードしてください。")
    else:
        st.info("左側で画像をアップロードし、スタイルを選択してください。")


with col2:
    st.header("✨ 生成結果")
    if 'generated_image_base64' in st.session_state and st.session_state.generated_image_base64:
        if 'download_image_bytes' in st.session_state and st.session_state.download_image_bytes:
            result_image_pil = st.session_state.download_image_bytes # Pillow Imageオブジェクト
            st.image(result_image_pil, caption="生成された画像", use_column_width=True)

            buf = io.BytesIO()
            result_image_pil.save(buf, format="PNG") # PNG形式で保存
            byte_im = buf.getvalue()

            st.download_button(
                label="画像をダウンロード (PNG)",
                data=byte_im,
                file_name=f"converted_image_{st.session_state.get('style_selector', 'style')}.png", # スタイル名を含むファイル名
                mime="image/png",
                use_container_width=True
            )
    else:
        st.info("ここに変換後の画像が表示されます。")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit and Stable Diffusion Web UI API")