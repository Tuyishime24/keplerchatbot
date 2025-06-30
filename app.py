from flask import Flask, request, render_template, jsonify
from rapidfuzz import fuzz
import json
import os  # Needed for getting PORT from environment

app = Flask(__name__)

# Load Q&A data from JSON file
with open("kepler_qa_data.json", "r", encoding="utf-8") as file:
    qa_data = json.load(file)

def find_answer(user_question, category="all"):
    """
    Match user's question with the most relevant Q&A entry.
    If a category is provided, filter questions by it first.
    """
    user_question = user_question.lower().strip()
    best_score = 0
    best_answer = None

    filtered_data = (
        [item for item in qa_data if item.get("category", "").lower() == category.lower()]
        if category != "all" else qa_data
    )

    for item in filtered_data:
        score = fuzz.partial_ratio(user_question, item["question"].lower())
        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    print(f"User question: '{user_question}' | Best match score: {best_score}")  # optional

    if best_score > 60:
        return best_answer
    else:
        return (
            "🤖 Sorry, I didn’t understand that. Try asking about:\n"
            "- 🏫 Admission & Registration\n"
            "- 🧭 Orientation\n"
            "- 📚 Programs\n"
        )

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.is_json:
            try:
                data = request.get_json()
                question = data.get("question", "")
                category = data.get("category", "all")
                answer = find_answer(question, category)
                return jsonify({"answer": answer})
            except Exception as e:
                return jsonify({"answer": f"⚠️ Error: {str(e)}"}), 400
        else:
            question = request.form.get("question", "")
            answer = find_answer(question)
            return render_template("index.html", question=question, answer=answer)

    return render_template("index.html")

if __name__ == "__main__":
    # Use the port provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)