import os
from flask import Flask, request

app = Flask(__name__)

# Define quiz questions
questions = {
    1: {
        "question": "What is the first miracle Jesus performed?",
        "options": ["Healing the blind man", "Parting the Red Sea", "Walking on Water", "Turning Water into Wine"],
        "correct_answer": 4
    },
    2: {
        "question": "Who is the father of Jacob?",
        "options": ["Abraham", "Isaac", "Nebuchadnezzar", "Saul"],
        "correct_answer": 2
    }
}

user_scores = {
    '254701234567': 10,
    '254712345678': 15,
    '254723456789': 5
}

# Store user points and current question
user_points = 0
user_current_question = 1

# Main Menu
def show_main_menu():
    response = "CON Welcome to Bibilia Mashinani \n"
    response += "1. Bible Quiz \n"
    response += "2. Scripture Memorization \n"
    response += "3. Community Service \n"
    response += "4. Daily Devotional \n"
    response += "5. Prayer Chain \n"
    response += "6. Storytelling Contest \n"
    response += "0. Exit"
    return response

@app.route("/", methods=["POST", "GET"])
def ussd_callback():
    global response, user_points, user_current_question
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "")

    def get_question(question_number):
        """Helper function to retrieve a question and its options."""
        question = questions[question_number]["question"]
        options = questions[question_number]["options"]
        response = f"CON Question {question_number}: {question} \n"
        for i, option in enumerate(options, 1):
            response += f"{i}. {option} \n"
        return response

    if text == "":
        # Main Menu
        response = show_main_menu()

    elif text == "1":
        # Bible Quiz Menu
        response = "CON Bible Quiz Time! : \n"
        response += "1. Start Quiz \n"
        response += "2. View Score Leaderboard \n"
        response += "99. Back To Main Menu"

    elif text == "1*1":
        # Start the first question in the quiz
        response = get_question(1)

    elif text.startswith("1*1*"):
        # Process quiz answers
        answer_data = text.split("*")
        user_answer = int(answer_data[-1])  # Extract the user's answer
        current_question = user_current_question

        # Check if the answer is correct
        if user_answer == questions[current_question]["correct_answer"]:
            user_points += 5  # Add points for correct answer
            response = f"CON Correct! You earn 5 points. \n"
        else:
            correct_option = questions[current_question]["correct_answer"]
            correct_answer_text = questions[current_question]["options"][correct_option - 1]
            response = f"CON Sorry, the correct answer was: '{correct_answer_text}' \n"

        # Move to the next question if available
        next_question = current_question + 1
        if next_question in questions:
            user_current_question = next_question
            response += get_question(next_question)
        else:
            # End the quiz if there are no more questions
            response = f"END Quiz completed! Your total score is {user_points}. Thank you for playing."

    elif text == '1*2':
        # Leaderboard functionality
        sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        response = "CON Top Scorers: \n"
        for i, (user, score) in enumerate(sorted_scores[:5], 1):
            response += f"{i}. {user[-4:]} - {score} points\n"  # Showing last 4 digits of phone number
        response += "99. Back To Main Menu"

    elif text == "2":
        # Scripture Memorization
        response = "CON Scripture Memorization : \n"
        response += "1. View This Week's Verse \n"
        response += "2. Check-In for Memorization \n"
        response += "3. View Your Progress \n"
        response += "99. Back To Main Menu"

    elif text == "3":
        # Community Service
        response = "CON Community Service : \n"
        response += "1. View Available Missions \n"
        response += "2. Log Service Hours \n"
        response += "3. View Ranks \n"
        response += "99. Back To Main Menu"

    elif text == "4":
        # Daily Devotional
        response = "CON Daily Devotional : \n"
        response += "1. View Today's Reflection \n"
        response += "2. Share Reflection \n"
        response += "3. View Community Reflections \n"
        response += "99. Back To Main Menu"

    elif text == "5":
        # Prayer Chain
        response = "CON Prayer Chain : \n"
        response += "1. Submit a Prayer Request \n"
        response += "2. Pray for a Request \n"
        response += "3. View Prayer Points \n"
        response += "99. Back To Main Menu"

    elif text == "6":
        # Storytelling Contest
        response = "CON Storytelling Contest \n"
        response += "1. Submit a Story \n"
        response += "2. Vote on Stories \n"
        response += "3. View Story Rank \n"
        response += "0. Back To Main Menu"

    elif '99' in text:
        response = show_main_menu()

    elif text == "0":
        # Exit
        response = "END Thank you for using the Bibilia Mashinani. God bless you!"

    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'), debug=True)
