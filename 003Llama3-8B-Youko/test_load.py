import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time # 時間計測用に追加

model_name = "rinna/llama-3-youko-8b"
print(f"Starting script...")
print(f"Loading model: {model_name}")
start_time = time.time() # 開始時間を記録

try:
    # トークナイザーのロード
    tokenizer_start_time = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer_end_time = time.time()
    print(f"Tokenizer loaded successfully in {tokenizer_end_time - tokenizer_start_time:.2f} seconds.")

    # モデルのロード
    # 初回実行時はここでダウンロードが始まります (時間がかかります)
    # メモリ使用量を抑えたい場合やGPUを使いたい場合はオプションを追加しますが、
    # まずはシンプルにロードできるか試します。
    model_start_time = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16, # メモリ効率化 (CPU/GPUの対応確認要)
        device_map="auto"  # GPUがあれば自動割り当て (CPUのみなら不要)
    )
    model_end_time = time.time()
    print(f"Model loaded successfully in {model_end_time - model_start_time:.2f} seconds.")

    # モデルがCPU/GPUどちらにロードされたか確認
    print(f"Model is on device: {model.device}")

    while True:
        input_text = input("You: ")  # ユーザーからの入力を受け取る
        if input_text.lower() in ["exit", "quit"]:  # 終了条件
            print("Exiting chat...")
            break

        # 入力から応答までの時間を計測
        start_time = time.time()  # 計測開始
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,       # 応答の長さを制限
            temperature=0.4,         # 多様性を抑える
            top_p=0.8,               # 確率の高いトークンに絞る
            do_sample=True           # サンプリングを有効化
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        end_time = time.time()  # 計測終了 (関数呼び出しに注意)

        # 応答と処理時間を表示
        print(f"Bot: {response}")
        print(f"Response time: {end_time - start_time:.2f} seconds")


except ImportError as e:
    print(f"Error: {e}")
    print("Required libraries might not be installed. Please run: pip install transformers torch accelerate sentencepiece")
except Exception as e:
    print(f"An error occurred: {e}")
    print("This might be due to insufficient RAM or other issues.")

end_time = time.time() # 終了時間を記録
print(f"Script finished in {end_time - start_time:.2f} seconds.")