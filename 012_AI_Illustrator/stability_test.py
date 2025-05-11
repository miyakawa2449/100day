# 0. 必要なライブラリをインポート
import os
from PIL import Image, ImageOps # init_imageを使わない場合、ImageOpsは不要になる可能性
from dotenv import load_dotenv
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

def main():
    # 1. 環境変数からAPIキーを読み込み
    load_dotenv()
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        print("エラー: APIキーが設定されていません。'.env' ファイルに STABILITY_API_KEY を設定してください。")
        return

    # 2. Stability AI クライアントを初期化
    try:
        stability_api = client.StabilityInference(
            key=api_key,
            verbose=True,
            engine="stable-diffusion-xl-1024-v1-0"
        )
    except Exception as e:
        print(f"クライアント初期化中にエラーが発生しました: {e}")
        return

    # 3. メイン処理
    try:
        # a. 画像読み込みと前処理 (今回は init_image を使わないので、この部分はAPI呼び出しでは使用しない)
        # jpg_image_path = "your_photo.jpg"
        # if not os.path.exists(jpg_image_path):
        #     print(f"エラー: 画像ファイルが見つかりません: {jpg_image_path}")
        #     return
            
        # target_size = (1024, 1024)

        # print(f"画像を読み込んでいます: {jpg_image_path}") # このログも init_image を使う場合のみ
        # with Image.open(jpg_image_path) as img:
        #     img.thumbnail(target_size, Image.Resampling.LANCZOS)
        #     img_rgba = img.convert("RGBA")
        #     padded_img = Image.new('RGB', target_size, (255, 255, 255))
        #     paste_position = (
        #         (target_size[0] - img_rgba.width) // 2,
        #         (target_size[1] - img_rgba.height) // 2
        #     )
        #     padded_img.paste(img_rgba, paste_position, img_rgba if img_rgba.mode == 'RGBA' else None)
        #     init_image_pil = padded_img
        # print("画像の読み込みと前処理が完了しました。") # このログも init_image を使う場合のみ

        # b. プロンプト設定
        current_prompt = "A cute cat drawn in high quality anime style."
        print(f"使用するプロンプト: {current_prompt}")


        # c. API呼び出し (generate) - init_image と start_schedule をコメントアウト
        print("Stability AI API を呼び出しています (Text-to-Image)...")
        response = stability_api.generate(
            prompt=current_prompt,
            # init_image=init_image_pil, # init_image を使わない
            # start_schedule=0.6,        # init_image を使わないので不要
            cfg_scale=8.0,
            steps=30,
            width=1024, # Text-to-Image の場合、出力画像のサイズを指定
            height=1024, # 同上
            # sampler="K_DPMPP_2M", # 必要であれば有効なサンプラー名を指定
        )

        # d. レスポンス処理と詳細ログ出力 (変更なし)
        output_idx = 0
        has_successful_image = False
        print("\n--- APIレスポンス処理開始 ---")
        for resp_idx, resp_data in enumerate(response):
            print(f"レスポンスブロック {resp_idx + 1}:")
            for art_idx, artifact in enumerate(resp_data.artifacts):
                print(f"  アーティファクト {art_idx + 1}:")
                
                raw_artifact_type = artifact.type
                raw_finish_reason = artifact.finish_reason
                
                print(f"    Type (raw value): {raw_artifact_type}")
                try:
                    artifact_type_name = generation.ArtifactType.Name(raw_artifact_type)
                    print(f"    Type (name): {artifact_type_name}")
                except ValueError:
                    artifact_type_name = f"Unknown or N/A (raw value was {raw_artifact_type})"
                    print(f"    Type (name): {artifact_type_name}")

                print(f"    Finish Reason (raw value): {raw_finish_reason}")
                try:
                    finish_reason_name = generation.FinishReason.Name(raw_finish_reason)
                    print(f"    Finish Reason (name): {finish_reason_name}")
                except ValueError:
                    finish_reason_name = f"Unknown or N/A (raw value was {raw_finish_reason})"
                    print(f"    Finish Reason (name): {finish_reason_name}")

                if artifact.text:
                    print(f"    Text/JSON content: {artifact.text}")

                FINISH_REASON_NULL_OR_FILTER = 0 
                FINISH_REASON_SUCCESS = 1

                if raw_artifact_type == generation.ARTIFACT_IMAGE:
                    print(f"    これは画像アーティファクトです。")
                    if raw_finish_reason == FINISH_REASON_SUCCESS:
                        if artifact.binary:
                            output_path = f"output_text2img_{output_idx}.png" # ファイル名を変更
                            with open(output_path, "wb") as f:
                                f.write(artifact.binary)
                            print(f"    画像保存成功: {output_path}")
                            output_idx += 1
                            has_successful_image = True
                        else:
                            print(f"    警告: 画像アーティファクト (SUCCESS) ですが、バイナリデータがありません。")
                    elif raw_finish_reason == FINISH_REASON_NULL_OR_FILTER:
                        print(f"    警告: 画像がコンテンツフィルターによってブロックされました (Reason: {finish_reason_name})。")
                    else: 
                        print(f"    警告: 画像の生成に失敗または完了しませんでした (Reason: {finish_reason_name})。")
                
                elif raw_artifact_type == generation.ARTIFACT_CLASSIFICATIONS:
                    print(f"    これは分類アーティファクトです。")
                elif raw_artifact_type == generation.ARTIFACT_TEXT:
                    print(f"    これはテキストアーティファクトです。")
                else:
                    print(f"    これは不明なタイプ ({artifact_type_name}) のアーティファクトです。")
                
                print(f"  ---")
        
        if not has_successful_image:
            print("\n最終的に成功した画像は生成されませんでした。")
        else:
            print(f"\n{output_idx} 枚の画像が正常に生成されました。")
        print("--- APIレスポンス処理終了 ---")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("--- スクリプト実行開始 ---")
    # ... (準備のメッセージは変更なし) ...
    main()
    print("\n--- スクリプト実行終了 ---")