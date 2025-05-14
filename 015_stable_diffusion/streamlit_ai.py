import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import os

# --- アプリケーション設定 ---
API_URL = "http://127.0.0.1:7860"  # Stable Diffusion Web UI のアドレスとポート (適宜変更してください)
IMG2IMG_ENDPOINT = f"{API_URL}/sdapi/v1/img2img"

# --- スタイル定義 ---
STYLES = {
    "水彩画風": {
        "base_prompt": "masterpiece, best quality, beautiful watercolor painting, soft lighting, vibrant colors, artistic, dreamy",
        "negative_prompt_suffix": "photo, realistic, 3d, ugly, deformed",
        "requires_lora": False,
        "default_denoising_strength": 0.7,
        "default_steps": 30,
        "default_cfg_scale": 7.0,
    },
    "ドラゴンボール風": {
        "base_prompt": "masterpiece, best quality, dynamic action pose, vibrant colors, bold outlines, manga style, anime screencap",
        "negative_prompt_suffix": "photorealistic, realistic, 3d render, watermark, signature, deformed",
        "requires_lora": True,
        "lora_suggestion": {"name": "DragonBall.safetensors", "trigger": "Dragon Ball style", "weight": 0.8}, # LoRA名はご自身のファイル名に合わせてください
        "default_denoising_strength": 0.70,
        "default_steps": 35,
        "default_cfg_scale": 7.5,
    },
    "油絵風": {
        "base_prompt": "masterpiece, best quality, beautiful oil painting, textured brush strokes, rich impasto, classical art",
        "negative_prompt_suffix": "anime, cartoon, photorealistic, blurry, ugly",
        "requires_lora": False,
        "default_denoising_strength": 0.65,
        "default_steps": 40,
        "default_cfg_scale": 7.0,
    },
    "アニメスケッチ風": {
        "base_prompt": "masterpiece, best quality, anime sketch, monochrome, detailed lines, rough sketch, concept art, dynamic lines",
        "negative_prompt_suffix": "color, painting, photorealistic, 3d, ugly",
        "requires_lora": False,
        "default_denoising_strength": 0.75,
        "default_steps": 25,
        "default_cfg_scale": 6.5,
    },
    "写真風リアリスティック": {
        "base_prompt": "photorealistic, ultra realistic, masterpiece, best quality, detailed skin texture, sharp focus, 8k uhd, professional photography, natural lighting",
        "negative_prompt_suffix": "anime, cartoon, painting, illustration, blurry, lowres, watermark, signature, ugly, deformed",
        "requires_lora": False,
        "default_denoising_strength": 0.35,
        "default_steps": 30,
        "default_cfg_scale": 7.0,
    },
    "サイバーパンク風": {
        "base_prompt": "masterpiece, best quality, cyberpunk city, neon lights, futuristic, dystopian, techwear, cinematic lighting",
        "negative_prompt_suffix": "fantasy, historical, ugly, deformed, painting",
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
    {"name": "LMS Karras", "description": "LMSにKarrasノイズスケジュールを適用。品質向上に寄与。"},
    {"name": "DPM2 Karras", "description": "DPM2にKarrasノイズスケジュールを適用。"},
    {"name": "DPM2 a Karras", "description": "DPM2 aにKarrasノイズスケジュールを適用。"},
    {"name": "DPM++ 2S a Karras", "description": "DPM++ 2S aにKarrasノイズスケジュールを適用。非常に高品質。"},
    {"name": "DPM++ 2M Karras", "description": "DPM++ 2MにKarrasノイズスケジュールを適用。定番かつ高品質。"},
    {"name": "DPM++ SDE Karras", "description": "DPM++ SDEにKarrasノイズスケジュールを適用。最高品質を狙えるが重い。"},
    {"name": "DDIM", "description": "高速で安定。ステップ数が少なくても機能。同じシードで同じ結果。"},
    {"name": "UniPC", "description": "比較的新しい。少ないステップ数で高品質な画像を生成できるとされる。"},
]
AVAILABLE_SAMPLER_NAMES = [s["name"] for s in SAMPLERS_INFO]

# --- API通信と画像処理関数 ---
def encode_image_to_base64_streamlit(uploaded_file_obj):
    if uploaded_file_obj is not None:
        try:
            bytes_data = uploaded_file_obj.getvalue()
            return base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            st.error(f"エラー(encode): 画像のエンコード中に問題が発生しました: {e}")
            return None
    return None

def decode_base64_to_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        st.error(f"エラー(decode): 画像のデコード中に問題が発生しました: {e}")
        return None

def convert_image_style_api(init_image_base64, prompt, negative_prompt="", denoising_strength=0.75,
                            sampler_name="Euler a", steps=30, cfg_scale=7, seed=-1,
                            width=None, height=None):
    payload = {
        "init_images": [init_image_base64], "prompt": prompt, "negative_prompt": negative_prompt,
        "denoising_strength": denoising_strength, "sampler_name": sampler_name, "steps": steps,
        "cfg_scale": cfg_scale, "seed": seed, "width": width, "height": height,
    }
    # st.write("--- 送信するペイロード (デバッグ用) ---"); st.json(payload) # デバッグ時に有効化

    api_response_object = None
    try:
        api_response_object = requests.post(IMG2IMG_ENDPOINT, json=payload, timeout=300)
        api_response_object.raise_for_status()
        r = api_response_object.json()
        if 'images' in r and r['images']:
            return r['images'][0]
        else:
            st.error(f"エラー(API): APIレスポンスに画像データがありません。レスポンス: {r}")
            return None
    except requests.exceptions.Timeout:
        st.error(f"エラー(API): リクエストがタイムアウト (接続先: {IMG2IMG_ENDPOINT})。")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"エラー(API): 接続/リクエスト失敗 (接続先: {IMG2IMG_ENDPOINT}): {e}")
        if api_response_object is not None:
            st.error(f"ステータスコード: {api_response_object.status_code}, 詳細: {api_response_object.text}")
        else:
            st.error("APIサーバーへの接続自体に失敗した可能性。Web UI起動/API設定/ポート確認を。")
        return None
    except Exception as e:
        st.error(f"予期せぬAPIエラー: {e}")
        return None

# --- Streamlit UIの初期化と状態管理 ---
st.set_page_config(layout="wide", page_title="画像スタイル変換 v1.2")

# セッションステートの初期化
if 'input_image_pil' not in st.session_state:
    st.session_state.input_image_pil = None
if 'generated_image_pil' not in st.session_state:
    st.session_state.generated_image_pil = None
if 'uploaded_file_for_processing' not in st.session_state: # 変換処理に実際に使うファイルオブジェクト
    st.session_state.uploaded_file_for_processing = None
if 'current_style_name' not in st.session_state: # 現在選択されているスタイル名
    st.session_state.current_style_name = list(STYLES.keys())[0]


def on_file_upload_change():
    """ファイルアップローダーの値が変更されたときのコールバック"""
    uploaded_file = st.session_state.get("file_uploader_key") # keyでウィジェットの値を取得
    if uploaded_file:
        st.write("--- Debug (on_change): 新しいファイルがアップロードされました ---")
        st.session_state.input_image_pil = Image.open(uploaded_file)
        st.session_state.generated_image_pil = None  # ★ 新しいファイルなので過去の生成結果をクリア
        st.session_state.uploaded_file_for_processing = uploaded_file # 変換用に保持
    else: # ファイルがクリアされた場合
        st.write("--- Debug (on_change): ファイルがクリアされました ---")
        st.session_state.input_image_pil = None
        st.session_state.generated_image_pil = None
        st.session_state.uploaded_file_for_processing = None

def on_style_change():
    """スタイルセレクタの値が変更されたときのコールバック"""
    st.session_state.current_style_name = st.session_state.get("style_selector_key")
    # 必要であれば、スタイル変更時に他のデフォルト値をリセットするロジックをここに追加

st.title("🎨 画像スタイル変換 v1.2")
st.caption("ローカルのStable Diffusion Web UIを使って、アップロードした画像を様々なスタイルに変換します。")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 詳細パラメータ設定")
    # API_URL = st.text_input("API URL", value=API_URL) # 必要なら
    
    # スタイル定義からデフォルト値を取得（選択中のスタイルに応じて更新されるようにしたい場合は工夫が必要）
    # ここでは固定のデフォルトを使用し、メインエリアでスタイル依存のデフォルトを提示
    steps_default = STYLES[st.session_state.current_style_name].get("default_steps", 30)
    cfg_scale_default = STYLES[st.session_state.current_style_name].get("default_cfg_scale", 7.0)

    steps = st.slider("ステップ数 (Steps)", 10, 150, steps_default, 5, key="steps_slider",
                    help="画像生成時のノイズ除去ステップ数。多いほど細かく描画。通常20～50。")
    cfg_scale = st.slider("CFGスケール", 1.0, 30.0, cfg_scale_default, 0.5, key="cfg_slider",
                        help="プロンプトへの忠実度。高いとプロンプトに従うが破綻しやすく、低いと自由だがぼやけることも。通常7～12。")
    seed = st.number_input("シード値 (Seed)", value=-1, step=1, key="seed_input",
                        help="画像生成の乱数シード。-1でランダム。同じシードとパラメータで同じ画像が生成。")
    selected_sampler_name = st.selectbox("サンプラー (Sampler)", AVAILABLE_SAMPLER_NAMES,
                                        index=AVAILABLE_SAMPLER_NAMES.index("DPM++ 2M Karras") if "DPM++ 2M Karras" in AVAILABLE_SAMPLER_NAMES else 0,
                                        key="sampler_selector", help="ノイズ除去アルゴリズム。品質や速度、タッチに影響。")
    for s_info in SAMPLERS_INFO:
        if s_info["name"] == selected_sampler_name:
            st.caption(f"**{s_info['name']}**: {s_info['description']}")
            break

# --- メインコンテンツエリア ---
# 1. 画像アップロード
st.header("🖼️ 1. 画像をアップロード")
uploaded_file_widget = st.file_uploader("変換したい画像を選択", type=["png", "jpg", "jpeg", "webp"],
                                        key="file_uploader_key", on_change=on_file_upload_change,
                                        label_visibility="collapsed")

# 2. 画像プレビューエリア
if st.session_state.input_image_pil:
    st.subheader("プレビュー")
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        st.image(st.session_state.input_image_pil, caption="元画像", use_container_width=True)
        original_width, original_height = st.session_state.input_image_pil.size
        st.caption(f"元画像のサイズ: {original_width}x{original_height}")
    with col_prev2:
        if st.session_state.generated_image_pil:
            st.image(st.session_state.generated_image_pil, caption="生成された画像", use_container_width=True)
            buf = io.BytesIO()
            st.session_state.generated_image_pil.save(buf, format="PNG")
            st.download_button("画像をダウンロード (PNG)", buf.getvalue(),
                            file_name=f"converted_{st.session_state.current_style_name.replace(' ', '_')}.png",
                            mime="image/png", use_container_width=True)
        else:
            st.info("ここに変換後の画像が表示されます。")

# 3. スタイルとプロンプト設定
if st.session_state.input_image_pil:
    st.header("🎨 2. スタイルとプロンプトを設定")
    style_name_selected = st.selectbox("適用するスタイル", options=list(STYLES.keys()),
                                    key="style_selector_key", on_change=on_style_change,
                                    index=list(STYLES.keys()).index(st.session_state.current_style_name))
    current_style_data = STYLES[style_name_selected]

    subject_prompt = st.text_input("被写体の説明 (例: 'a cute cat', 'a beautiful mountain landscape')",
                                key=f"subject_{style_name_selected}")
    base_prompt_default = current_style_data.get("base_prompt", "")
    base_prompt_user_edit = st.text_area("基本プロンプト (編集可)", value=base_prompt_default,
                                        height=100, key=f"base_prompt_{style_name_selected}")
    full_prompt = f"{subject_prompt}, {base_prompt_user_edit}" if subject_prompt else base_prompt_user_edit

    common_neg = "worst quality, low quality, normal quality, blurry, ugly, deformed, text, watermark, signature, extra limbs, disfigured, malformed_hands, bad_anatomy"
    style_neg_suffix = current_style_data.get("negative_prompt_suffix", "")
    full_neg_default = f"{common_neg}, {style_neg_suffix}".strip(", ")
    negative_prompt = st.text_area("ネガティブプロンプト (編集可)", value=full_neg_default,
                                height=100,  key=f"neg_prompt_{style_name_selected}")

    denoising_default = current_style_data.get("default_denoising_strength", 0.75)
    denoising_strength = st.slider("Denoising Strength (スタイルの強さ)", 0.0, 1.0, denoising_default, 0.05,
                                key=f"denoising_{style_name_selected}",
                                help="高いほどプロンプト/スタイルの影響が強く、低いほど元画像の特徴が残ります。")

    if current_style_data.get("requires_lora"):
        st.info(f"このスタイル「{style_name_selected}」はLoRAモデルの使用を推奨します。")
        lora_sugg = current_style_data.get("lora_suggestion", {})
        lora_name = st.text_input("LoRAファイル名 (例: your_lora.safetensors)", value=lora_sugg.get("name", ""),
                                key=f"lora_name_{style_name_selected}", help="models/Lora フォルダ内のファイル名。")
        lora_trigger = st.text_input("LoRAトリガーワード", value=lora_sugg.get("trigger", ""),
                                    key=f"lora_trigger_{style_name_selected}")
        lora_weight = st.slider("LoRAの重み", 0.0, 2.0, lora_sugg.get("weight", 0.8), 0.1,
                                key=f"lora_weight_{style_name_selected}")
        if lora_name and lora_trigger:
            full_prompt += f", {lora_trigger}, <lora:{os.path.splitext(lora_name)[0]}:{lora_weight}>"
        elif lora_name and not lora_trigger:
            st.warning("LoRAファイル名が入力されていますがトリガーワードが空です。")

    st.header("🚀 3. 変換実行")
    if st.button("🎨 スタイル変換実行！", type="primary", use_container_width=True):
        if st.session_state.uploaded_file_for_processing:
            base64_image = encode_image_to_base64_streamlit(st.session_state.uploaded_file_for_processing)
            if base64_image:
                with st.spinner("画像を変換中です...しばらくお待ちください..."):
                    ow, oh = st.session_state.input_image_pil.size # 元画像のサイズを使用
                    generated_image_base64 = convert_image_style_api(
                        base64_image, full_prompt, negative_prompt=negative_prompt,
                        denoising_strength=denoising_strength, sampler_name=selected_sampler_name, # サイドバーの値
                        steps=steps, cfg_scale=cfg_scale, seed=seed, # サイドバーの値
                        width=ow, height=oh)
                if generated_image_base64:
                    st.session_state.generated_image_pil = decode_base64_to_image(generated_image_base64)
                    st.success("画像変換が完了しました！")
                    st.rerun() # 表示を更新するために再実行
                # API呼び出し失敗時のエラーはconvert_image_style_api内でst.error表示
            else: # Base64エンコード失敗
                st.error("画像のエンコードに失敗しました。")
        else:
            st.warning("まず画像をアップロードしてください。")
else: # 画像がアップロードされていない場合
    st.info("上部で画像をアップロードすると、設定項目が表示されます。")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit and Stable Diffusion Web UI API")