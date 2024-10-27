import os
import random
from flask import Flask, request
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the MongoDB connection string from environment variables
MONGODB_KEY = os.getenv('MONGODB_KEY')

# Create a MongoDB client and handle connection errors
try:
    client = MongoClient(MONGODB_KEY)
    # Check if the client is connected
    client.server_info()  # This will raise an exception if the connection fails
except errors.ServerSelectionTimeoutError as err:
    print("Could not connect to MongoDB: ", err)
    raise  # Reraise the error after logging

# Select the database and collection
db = client['bibilia_mashinani']  # or replace with client['your_db_name']
questions_collection = db['questions']  # Collection for storing questions

question_points = db['points']

mem_points_collection = db['mem_points']

# Define the sample quiz questions
sample_questions = [
    {
        "question": "What is the first miracle Jesus performed?",
        "options": ["Healing the blind man", "Parting the Red Sea", "Walking on Water", "Turning Water into Wine"],
        "correct_answer": 4
    },
    {
        "question": "Who is the father of Jacob?",
        "options": ["Abraham", "Isaac", "Nebuchadnezzar", "Saul"],
        "correct_answer": 2
    }
]

# Function to initialize questions in the database
def initialize_questions():
    # Check if the collection is empty
    if questions_collection.count_documents({}) == 0:
        questions_collection.insert_many(sample_questions)

# Initialize questions on app startup
initialize_questions()

# Function to retrieve questions from the database
def get_questions():
    questions = list(questions_collection.find())
    return {i + 1: {
        "question": q["question"],
        "options": q["options"],
        "correct_answer": q["correct_answer"]
    } for i, q in enumerate(questions)}

# Load quiz questions from the database
questions = get_questions()

user_scores = {
    '254701234567': 10,
    '254712345678': 15,
    '254723456789': 5
}

# Sample Bible verses
verses = [
    {"book": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world..."},
    {"book": "Psalm", "chapter": 23, "verse": 1, "text": "The Lord is my shepherd, I shall not want."},
    {"book": "Romans", "chapter": 8, "verse": 28, "text": "And we know that in all things God works..."},
    {"book": "Proverbs", "chapter": 3, "verse": 5, "text": "Trust in the Lord with all your heart..."},
    {"book": "Philippians", "chapter": 4, "verse": 13, "text": "I can do all things through Christ who strengthens me."}
]

# Store user points and current question
user_points = 0
user_memorization_points = 0
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
    response += "7. Fitness Challenge \n"
    response += "0. Exit"
    return response

def show_mem_menu():
    response = "CON Scripture Memorization : \n"
    response += "1. View This Week's Verse \n"
    response += "2. Check-In for Memorization \n"
    response += "3. View Your Progress \n"
    response += "99. Back To Main Menu"
    return response

def show_comm_menu():
    response = "CON Community Service : \n"
    response += "1. View Available Missions \n"
    response += "2. Log Service Hours \n"
    response += "3. View Ranks \n"
    response += "99. Back To Main Menu"
    return response

def show_dev_menu():
    response = "CON Daily Devotional : \n"
    response += "1. View Today's Reflection \n"
    response += "2. Share Reflection \n"
    response += "3. View Community Reflections \n"
    response += "99. Back To Main Menu"
    return response

def show_pray_menu():
    response = "CON Prayer Chain : \n"
    response += "1. Submit a Prayer Request \n"
    response += "2. Pray for a Request \n"
    response += "3. View Prayer Points \n"
    response += "99. Back To Main Menu"
    return response

def show_story_menu():
    response = "CON Storytelling Contest \n"
    response += "1. Submit a Story \n"
    response += "2. Vote on Stories \n"
    response += "3. View Story Rank \n"
    response += "99. Back To Main Menu"
    return response

def show_fit_menu():
    response = "CON Fitness Challenge : \n"
    response += "1. Log Activity \n"
    response += "2. View My Fitness Points \n"
    response += "3. View Monthly Achievements \n"
    response += "99. Back to Main Menu"
    return response

# Function to get a random verse
def get_random_verse():
    verse = random.choice(verses)
    response = f"CON This Week's Verse: \n"
    response += f"{verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text']} \n\n"
    response += "May God Bless You! \n"

    response += "11. Back to Memorization Menu"
    return response

@app.route("/", methods=["POST", "GET"])
def ussd_callback():
    global response, user_points, user_current_question, user_memorization_points
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
   
    # Store points for the user (upsert = update if exists, insert if not)
    question_points.update_one(
        {'phone_number': phone_number},  # Identify by phone number
        {'$set': {'points': user_points}},  # Update points
        upsert=True  # Insert if doesn't exist
    )

    # For memorization points
    mem_points_collection.update_one(
        {'phone_number': phone_number},
        {'$set': {'points': user_memorization_points}},
        upsert=True
    )

    # Retrieve points from the database for the user
    user_data = question_points.find_one({'phone_number': phone_number})
    user_points = user_data['points'] if user_data else 0  # Default to 0 if no data found

    # Retrieve memorization points similarly
    mem_data = mem_points_collection.find_one({'phone_number': phone_number})
    user_memorization_points = mem_data['points'] if mem_data else 0

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
        response = get_question(1)

    elif text.startswith("1*1*"):
        # Process quiz answers
        answer_data = text.split("*")
        user_answer = int(answer_data[-1])  # Extract the user's answer
        current_question = user_current_question

        # Validate user input
        total_options = len(questions[current_question]["options"])
        if user_answer < 1 or user_answer > total_options:
            # If the user's answer is not within the valid range, show an error message
            response = f"CON Invalid input! Please choose a number between 1 and {total_options}. \n"
            response += get_question(current_question)  # Repeat the question
        else:
            # Check if the answer is correct
            if user_answer == questions[current_question]["correct_answer"]:
                user_points += 5
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
        response = show_mem_menu()

    elif text == '2*1':
        response = get_random_verse()

    elif text == '2*2':
        # Asking if the user has memorized the verse
        response = "CON Have you memorized this week's verse? \n"
        response += "1. Yes \n"
        response += "2. No"

    elif text == '2*2*1':
        # If user selects Yes
        user_memorization_points += 10
        response = "END Great! You've earned 10 points for memorizing this week's verse."

    elif text == '2*2*2':
        # If user selects No
        response = "CON Would you like to try again? \n"
        response += "11. Back to Memorization Menu"

    elif text == '2*3':
        response = "CON Your Memorization Progress : \n"
        if user_memorization_points <= 10:
            response += "Level: 1 - Seed Planter \n"
            response += "You've planted your first seeds of knowledge. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 10 and user_memorization_points <= 30:
            response += "Level: 2 - Verse Learner \n"
            response += "You've started your journey of memorizing scripture. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 30 and user_memorization_points <= 50:
            response += "Level: 3 - Scripture Desciple \n"
            response += "You're Learning the verses by heart. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 50 and user_memorization_points <= 80:
            response += "Level: 4 - Memorization Scholar \n"
            response += "You're knowledge of the world is deepening. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 80 and user_memorization_points <= 100:
            response += "Level: 5 - Wisdom Seeker \n"
            response += "You’re now a wisdom seeker, learning His word with intent. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 100 and user_memorization_points <= 150:
            response += "Level: 6 - Scripture Master \n"
            response += "You've mastered the art of scripture memorization. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"
        elif user_memorization_points > 150:
            response += "Level: 7 - Faithful Steward \n"
            response += "You're a steward of His word, living by every verse. \n"
            response += f"Points: {user_memorization_points} \n"
            response += "11. Back To Memorization Menu"

    elif text == "3":
        # Community Service
        response = show_comm_menu()
       

    elif text == "4":
        # Daily Devotional
        response = show_dev_menu()

    elif text == "5":
        # Prayer Chain
        response = show_pray_menu()

    elif text == "6":
        # Storytelling Contest
        response = show_story_menu()

    elif text == "7":
        #Fitness Challenge
        response = show_fit_menu()
       

    elif text == '99':
        response = show_main_menu()

    elif text == '11':
        response = show_mem_menu()

    elif text == "0":
        # Exit
        response = "END Thank you for using the Bibilia Mashinani. God bless you!"

    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'), debug=True)