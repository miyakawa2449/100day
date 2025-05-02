from flask import Flask, request, jsonify, render_template
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# モデルとトークナイザーのロード
model_name = "rinna/llama-3-youko-8b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return "Use POST method to send a message."

    try:
        user_input = request.json.get("message", "")
        logging.info(f"User input: {user_input}")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # モデルで応答を生成
        inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Bot response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)