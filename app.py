import os
from flask import Flask, request, Response
import africastalking

app = Flask(__name__)

# Initialize Africa's Talking
africastalking.initialize(
    username='sandbox',
    api_key='atsk_98638530e5f1dbe6220de8fad0b698d05f3dab1c371c97ebac4521c7c0aad4edfdbe205d',
)
sms = africastalking.SMS

# Define quiz questions with references
questions = {
    1: {
        "question": "What is the first miracle Jesus performed?",
        "options": ["Healing the blind man", "Parting the Red Sea", "Walking on Water", "Turning Water into Wine"],
        "correct_answer": 4,
        "reference": "John 2:1-11"  # Reference for the correct answer
    },
    2: {
        "question": "Who is the father of Jacob?",
        "options": ["Abraham", "Isaac", "Nebuchadnezzar", "Saul"],
        "correct_answer": 2,
        "reference": "Genesis 25:26"  # Reference for the correct answer
    }
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

        # Send SMS notification to the user about starting the quiz
        send_sms(phone_number, "You have started the Bible Quiz! Good luck!")

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
            reference = questions[current_question]["reference"]
            response = f"CON Sorry, the correct answer was: '{correct_answer_text}' (See: {reference}) \n"

        # Move to the next question if available
        next_question = current_question + 1
        if next_question in questions:
            user_current_question = next_question
            response += get_question(next_question)
        else:
            # End the quiz if there are no more questions
            response = f"END Quiz completed! Your total score is {user_points}. Thank you for playing."

            # Send SMS notification about total points with reference
            send_sms(phone_number, f"Quiz completed! Your total score is {user_points} points. You can find the answers in the Bible chapters referenced in the questions.")

    elif text == '1*2':
        # Leaderboard functionality
        response = "CON Top Scorers: \n"
        response += "99. Back To Main Menu"

    elif text == "2":
        # Scripture Memorization
        response = "CON Scripture Memorization : \n"
        response += "1. View This Week's Verse \n"
        response += "99. Back To Main Menu"

    elif '99' in text:
        response = show_main_menu()

    elif text == "0":
        # Exit
        response = "END Thank you for using the Bibilia Mashinani. God bless you!"

    return response

def send_sms(phone_number, message):
    """Function to send SMS using Africa's Talking."""
    try:
        response = sms.send(message, [phone_number])
        print(f"SMS sent successfully: {response}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

@app.route('/incoming-messages', methods=['POST'])
def incoming_messages():
    """Route to handle incoming SMS messages."""
    data = request.get_json(force=True)
    print(f'Incoming message...\n{data}')
    return Response(status=200)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000), debug=True)
