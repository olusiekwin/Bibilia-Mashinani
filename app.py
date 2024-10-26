import os
from flask import Flask, request
app = Flask(__name__)

response = ""

@app.route("/", methods=["POST", "GET"])
def ussd_callback():
  global response
  session_id = request.values.get("sessionId", None)
  service_code = request.values.get("serviceCode", None)
  phone_number = request.values.get("phoneNumber", None)
  text = request.values.get("text", "default")

  if text == "":
    response  = "CON Welcome to Bibilia Mashinani \n"
    response += "1. Bible Quiz \n"
    response += "2. Scripture Memorization \n"
    response += "3. Community Service \n"
    response += "4. Daily Devotional \n"
    response += "5. Prayer Chain \n"
    response += "6. Storytelling Contest \n"
    response += "0. Exit"

  elif text == "1":
    response = "CON Bible Quiz Time! : \n"
    response += "1. Start Quiz \n"
    response += "2. View Score Leaderboard \n"
    response += "0. Back To Main Menu"

  elif text == "2":
    response = "CON Scripture Memorization : \n"
    response += "1. View This Week's Verse \n"
    response += "2. Check-In for Memorization \n"
    response += "3. View Your Progress \n"
    response += "0. Back To Main Menu"

  elif text == "3":
    response = "CON Community Service : \n"
    response += "1. View Available Missions \n"
    response += "2. Log Service Hours \n"
    response += "3. View Ranks \n"
    response += "0. Back To Main Menu"

  elif text == "4":
    response = "CON Daily Devotional : \n"
    response += "1. View Today's Reflection \n"
    response += "2. Share Reflection \n"
    response += "3. View Community Reflections \n"
    response += "0. Back To Main Menu"

  elif text == "5":
    response = "CON Prayer Chain : \n"
    response += "1. Submit a Prayer Request \n"
    response += "2. Pray for a Request \n"
    response += "3. View Prayer Points \n"
    response += "0. Back To Main Menu"

  elif text == "6":
    response = "CON Storytelling Contest \n"
    response += "1. Submit a Story \n"
    response += "2. Vote on Stories \n"
    response += "3. View Story Rank \n"
    response += "0. Back To Main Menu"

  return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))