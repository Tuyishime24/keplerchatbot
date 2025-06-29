from flask import Flask, request, render_template, jsonify
from rapidfuzz import fuzz
import json

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
    best_answer = "🤖 Sorry, I couldn't find an answer for that. Please try asking something else."

    # Filter questions by category if provided
    if category != "all":
        filtered_data = [
            item for item in qa_data
            if item.get("category", "").lower() == category.lower()
        ]
    else:
        filtered_data = qa_data

    for item in filtered_data:
        score = fuzz.partial_ratio(user_question, item["question"].lower())
        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    return best_answer

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
            # Fallback for form submissions (not used with current frontend)
            question = request.form.get("question", "")
            answer = find_answer(question)
            return render_template("index.html", question=question, answer=answer)

    # GET request: return chat UI
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)