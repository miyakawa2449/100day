import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# モデルとトークナイザーのロード
model_name = "rinna/llama-3-youko-8b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

st.title("Chatbot")

user_input = st.text_input("メッセージを入力してください:")
if st.button("送信"):
    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    st.text_area("Botの応答", value=response, height=200)