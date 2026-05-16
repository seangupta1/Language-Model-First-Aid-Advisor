from flask import Flask, render_template, request
import torch
from model.first_aid_advisor import FirstAidAdvisorLM

app = Flask(__name__)

# Device selection (GPU if available)
device = "cuda" if torch.cuda.is_available() else "cpu"  # choose device
print("Using device:", device)

model = FirstAidAdvisorLM(model_name="fine_tuned")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt")

    response = model.answer(
        prompt=prompt,
        device=device
    )

    return render_template(
        "index.html",
        prompt=prompt,
        response=response
        )