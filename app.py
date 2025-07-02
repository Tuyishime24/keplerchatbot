from flask import Flask, request, render_template, jsonify
from rapidfuzz import fuzz
import json
import os

app = Flask(__name__)

# Load Q&A data from JSON file
with open("kepler_qa_data.json", "r", encoding="utf-8") as file:
    qa_data = json.load(file)

def find_best_match(user_question, category_filter=None):
    user_question = user_question.lower().strip()
    best_score = 0
    best_answer = None
    detected_category = None

    if category_filter and category_filter.lower() != "all":
        filtered_data = [item for item in qa_data if item.get("category", "").lower() == category_filter.lower()]
    else:
        filtered_data = qa_data

    for item in filtered_data:
        question_text = item.get("question", "").lower()
        score = fuzz.partial_ratio(user_question, question_text)
        if score > best_score:
            best_score = score
            best_answer = item.get("answer", "")
            detected_category = item.get("category", "").lower()

    return best_answer, best_score, detected_category

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.is_json:
            try:
                data = request.get_json()
                user_question = data.get("question", "")
                selected_category = data.get("category")
                if selected_category:
                    selected_category = selected_category.lower()
                else:
                    selected_category = "all"

                # Try match within selected category first
                answer, score, detected_category = find_best_match(user_question, selected_category)

                # If no good match, try globally
                if score < 60:
                    answer, score, detected_category = find_best_match(user_question, category_filter=None)

                # Fallback response if still no match
                if score < 60 or not answer:
                    answer = (
                        "🤖 Sorry, I didn’t understand that. Try asking about:\n"
                        "- 🏫 Admission & Registration\n"
                        "- 🧭 Orientation\n"
                        "- 📚 Programs"
                    )
                    detected_category = None

                return jsonify({
                    "answer": answer,
                    "detected_category": detected_category
                })

            except Exception as e:
                return jsonify({"answer": f"⚠️ Error: {str(e)}"}), 400

        else:
            # fallback for form POST (not JSON) — optional
            question = request.form.get("question", "")
            answer, _, _ = find_best_match(question)
            return render_template("index.html", question=question, answer=answer)

    # GET request
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)