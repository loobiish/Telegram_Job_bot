##___________________Library_____________________##

import telebot
import time
import json
import requests
import pandas as pd
from datetime import datetime
import random
import numpy as np
import os
import sys
from flask import Flask, request

##___________________Bot_Confirmation______________________##

token = "1349348866:AAG3VD_SkxlHIltZl0gRw4LHd6hnmpla15o"

bot = telebot.TeleBot(token)
server = Flask(__name__)


##____________________User_Details_________________________##

user_details = {}
feedback_reply = {}

class Job:
    def __init__(self, job_field):
        self.job_field = job_field
        self.location = None
        self.company = None


##_____________________Job_Search__________________________##

def search_jobs(job, location_given, company_given, id):
    if job.lower() == "na":
        job = ""
    if location_given.lower() == "na":
        location_given = ""
    if company_given.lower() == "na":
        company_given = ""
    job=job.replace(" ", "%20")
    location_given=location_given.replace(" ", "%20")
    company_given=company_given.replace(" ", "%20")
    urls = f"http://15.206.63.193:5000/db/main?tsearch={job}&lsearch={location_given}&csearch={company_given}&dept=&"
    req = requests.get(urls)
    job_list = json.loads(req.content)
    job_details(job_list, id)

def job_details(job_list, id):
    if len(job_list["result"]) == 0:
        bot.send_message(id, "Sorry no new jobs available, please try again later.")
    else:
        try:
            bot.send_message(id, "Here are latest jobs for you!")
            for i in range(0, 15):
                try:
                    comp = job_list["result"][i]["Company"]
                    loc = job_list["result"][i]["Location"]
                    title = job_list["result"][i]["Title"]
                    indus = job_list["result"][i]["Industry"]
                    link = job_list["result"][i]["URL"]
                    bot.send_message(id, f"🟠 *Company*: {comp}\n*🟡 Title*: {title}\n*🟢 Industry*: {indus}\n*🔵 Location*: {loc}\n"
                    f"\n\n*🟣 Link*:\n{link}", parse_mode="Markdown")
                except:
                    pass
        except:
            pass
        bot.send_message(id, "Type *Update* to update jobs.", parse_mode="Markdown")
    return True


##___________________________/start____________________________##

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Job searching bot! \n🔴 Type */start* to start again.\n🔴 Type *Update* to update jobs.\n"
    "🔴 Type *About* to know about this bot.\n🔴 Type *Help* for help.\n🔴 Type *Feedback* to give a feedback.\n🔴 Type *Donate* to donate and show your support 😊"
    "\n🔴 For advertisement or commercial purpose send mail to: job.finding.bot@gmail.com", parse_mode="Markdown")
    owner_id = 872448274
    chat_id = message.chat.id
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
    user_id = df_read.to_dict("records")
    nme = [message.from_user.first_name]
    if message.from_user.username==None:
        usrnme = ["Na"]
    else:
        usrnme = [message.from_user.username]
    chtid = [chat_id]
    rgst_on = [dt_string]
    lst_usd = [0]
    lst_job = ["Na"]
    lst_loc = ["Na"]
    lst_comp = ["Na"]
    subs = [1]
    dic = {"Name": nme, "Username": usrnme, "Chat_ID": chtid, "Registered_On": rgst_on, "Last_Used": lst_usd, 
    "Last_Job": lst_job, "Last_Location": lst_loc, "Last_Company": lst_comp, "Subscription": subs}
    temp_list=[]
    for i in range(len(user_id)):
        temp_list.append(user_id[i]["Chat_ID"])
    for i in chtid:
        if i not in temp_list:
            print("Added")
            df = pd.DataFrame(dic)
            df.to_csv(os.path.join(sys.path[0],"customer_list.csv"), mode= 'a', header=False, index = False)
            bot.send_message(owner_id, f"New data added\nName: {message.from_user.first_name}\nUser name: {message.from_user.username}\nChat ID: {chat_id}"
            "\n\nCheck list: /customer_list\n\nSend ad: /send_ad\nAnnouncement: /announce")
    bot.send_message(chat_id, "*Note*: You can pause your subscription by typing /off.", parse_mode="Markdown")


##______________________/list_____________________________##

@bot.message_handler(commands=["list"])
def list_command(message):
    owner_id = 872448274
    chat_id = message.chat.id
    if chat_id == owner_id:
        bot.send_message(owner_id, "List of commands:\n/start: For start menu\n/off: To pause subscription\n/on: To resume subscription\n"
        "/send_ad: To send ad\n/announce: For announcement\n/customer_list: For customer list\n/reply_feedback: To reply a feedback\nKey: 58789")
    else:
        bot.send_message(chat_id, "Access Denied!")

##_______________________/off_____________________________##

@bot.message_handler(commands=["off"])
def off_subs(message):
    chat_id = message.chat.id
    df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
    li = df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"]
    if li.array[0] != 0:
        bot.send_message(chat_id, "🔴 We have *paused* your subscription that means you will not recieve any notificaion, update or notice from us. You will not be able to update jobs too. "
        "If possible please state your reason to pause subscription by typing *Feedback*, that will help us a lot. You can resume your subscription any time by typing /on.", parse_mode="Markdown")
        df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"] = 0
        df_read.to_csv(os.path.join(sys.path[0],"customer_list.csv"), index=False)
    else:
        bot.send_message(chat_id, "Your subscription is already paused, resume it anytime by typing /on")


##_______________________/on___________________________##

@bot.message_handler(commands=["on"])
def on_subs(message):
    chat_id = message.chat.id
    df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
    li = df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"]
    if li.array[0] != 1:
        bot.send_message(chat_id, "🔴 Welcome back! We are glad to see you again. We have *resumed* your subscription. You are now able to recieve lastest "
        "job updates by typing *Update*. Type /start to see menu.", parse_mode="Markdown")
        df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"] = 1
        df_read.to_csv(os.path.join(sys.path[0],"customer_list.csv"), index=False)
    else:
        bot.send_message(chat_id, "Your subscription is already active!")
    


##_________________________/send_ad__________________________##

@bot.message_handler(commands=["send_ad"])
def ask_ad(message):
    owner_id = 872448274
    msg = bot.send_message(owner_id, "Enter the *key* value", parse_mode="Markdown")
    bot.register_next_step_handler(msg, ad_key)

def ad_key(message):
    owner_id = 872448274 
    key = message.text 
    if key == "58789":
        msg = bot.send_message(owner_id, "Enter the number of people you want to send ad(write *All* if you want to send message to everyone), "
        "advertisement image location(with '\\' instead of '\') and advertisement "
        "text/link separated by *#*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, send_adv)
    else:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Wrong key!", parse_mode="Markdown")
        bot.send_message(owner_id, f"Advertisement access denied to: {message.from_user.first_name}\n{message.from_user.username}\n{chat_id}")

def send_adv(message):
    owner_id = 872448274 
    try:
        ad = message.text
        ad_list=ad.split("#")
        df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
        user_id = df_read.to_dict("records")
        temp_list=[]
        for i in range(len(user_id)):
            temp_list.append(int(user_id[i]["Chat_ID"]))
        if str(ad_list[0]).lower()=="all":
            for i in temp_list:
                photo = open(ad_list[1], "rb")
                li = df_read.loc[df_read["Chat_ID"]== i, "Subscription"]
                if li.array[0] == 1:
                    bot.send_photo(i, photo, caption= ad_list[2])
        else:
            random.shuffle(temp_list)
            for i in range(int(ad_list[0])):
                try:
                    photo = open(ad_list[1], "rb")
                    li = df_read.loc[df_read["Chat_ID"]== temp_list[i], "Subscription"]
                    if li.array[0] == 1:    
                        bot.send_photo(temp_list[i], photo, caption= ad_list[2])
                        bot.send_message(owner_id, temp_list[i])
                except:
                    pass
        bot.send_message(owner_id, "Process of sending ad: Complete")
    except Exception as e:
        bot.send_message(owner_id, e)


##______________________/announce_____________________________##

@bot.message_handler(commands=['announce'])
def send_announcement(message):
    owner_id = 872448274
    msg = bot.send_message(owner_id, "Enter the *key* value", parse_mode="Markdown")
    bot.register_next_step_handler(msg, announce_key)

def announce_key(message):
    owner_id = 872448274 
    key = message.text 
    if key == "58789":
        msg = bot.send_message(owner_id, "Enter your announcement. This message will be sent to everyone.", parse_mode="Markdown")
        bot.register_next_step_handler(msg, announce)
    else:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Wrong key!", parse_mode="Markdown")
        bot.send_message(owner_id, f"Announcement denied to: {message.from_user.first_name}\n{message.from_user.username}\n{chat_id}")

def announce(message):
    owner_id = 872448274 
    try:
        ann = message.text
        df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
        user_id = df_read.to_dict("records")
        temp_list=[]
        for i in range(len(user_id)):
            temp_list.append(int(user_id[i]["Chat_ID"]))
        for i in temp_list:
            li = df_read.loc[df_read["Chat_ID"]== i, "Subscription"]
            if li.array[0] == 1:
                bot.send_message(i, ann)
        bot.send_message(owner_id, "Process of announcement: Complete")
    except Exception as e:
        bot.send_message(owner_id, e)


##_______________________/customer_list_____________________________##

@bot.message_handler(commands=['customer_list'])
def check_customer(message):
    owner_id = 872448274
    msg = bot.send_message(owner_id, "Enter the *key* value", parse_mode="Markdown")
    bot.register_next_step_handler(msg, list_key)

def list_key(message):
    owner_id = 872448274 
    key = message.text 
    if key == "58789":
        bot.send_document(owner_id, open(os.path.join(sys.path[0],"customer_list.csv"), "rb"))
    else:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Wrong key!", parse_mode="Markdown")
        bot.send_message(owner_id, f"Customer list access denied to: {message.from_user.first_name}\n{message.from_user.username}\n{chat_id}")


##__________________________/reply_feedback__________________________##

@bot.message_handler(commands=['reply_feedback'])
def replyfeedback(message):
    owner_id = 872448274
    msg = bot.send_message(owner_id, "Enter the *key* value", parse_mode="Markdown")
    bot.register_next_step_handler(msg, feedback_key)

def feedback_key(message):
    owner_id = 872448274 
    key = message.text 
    if key == "58789":
        msg = bot.send_message(owner_id, "Enter the chat id and feedback separated by *#*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, feedback_message)
    else:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Wrong key!", parse_mode="Markdown")
        bot.send_message(owner_id, f"Feedback access denied to: {message.from_user.first_name}\n{message.from_user.username}\n{chat_id}")

def feedback_message(message):
    feedback = message.text
    feedback_list=feedback.split("#")
    bot.send_message(feedback_list[0], feedback_list[1])


##________________________Hi__________________________##

@bot.message_handler(func=lambda msg: msg.text is not None and ("hi" in msg.text.lower() or "hey" in msg.text.lower() or "hei" in msg.text.lower() or "hello" in msg.text.lower()))
def send_hi(message):
    chat_id = message.chat.id
    df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
    li = df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"]
    if li.array[0] == 1:
        bot.reply_to(message, "Welcome to the Job searching bot! \n🔴 Type */start* to start again.\n🔴 Type *Update* to update jobs.\n"
        "🔴 Type *About* to know about this bot.\n🔴 Type *Help* for help.\n🔴 Type *Feedback* to give a feedback.\n🔴 Type *Donate* to donate and show your support 😊", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "You have paused your subscription, please type /on to resume it.")


##____________________Feedback__________________________##

@bot.message_handler(func=lambda msg: msg.text is not None and "feedback" in msg.text.lower())
def send_feedback(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Please start writing your feedback. Try to write your feedback in a single message.* The bot will accept only one single message"
    " as a feedback.*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, feedback_thanks)

def feedback_thanks(message):
    chat_id = message.chat.id
    try:
        owner_id = 872448274
        feedback = message.text
        bot.send_message(owner_id, f"Name: {message.from_user.first_name}\nUsername: {message.from_user.username}\nChat ID: {chat_id}\n\nFeedback: {feedback}\nType: /reply_feedback")
        bot.send_message(chat_id, "Thank you for your feedback 😊. We have recorded your feedback and will surely check it and work on it.")
    except:
        bot.send_message(chat_id, "Something went wrong, please try again later.")


##______________________Help________________________##

@bot.message_handler(func=lambda msg: msg.text is not None and "help" in msg.text.lower())
def send_help(message):
    bot.reply_to(message, "To use this bot type *Update*. The bot will ask about your prefered Job title, Location and Company. "
    "Type *Na* if you don't have any preferable Job title, Location or Company."
    "For any complain or suggestion please write a feedback by typing *Feedback*.", parse_mode="Markdown")


##________________________About______________________##

@bot.message_handler(func=lambda msg: msg.text is not None and "about" in msg.text.lower())
def send_about(message):
    bot.reply_to(message, "This is a telegram bot to give latest job update created by me (I'm not going to disclose my name here 😅). "
    "It searches jobs from following websites: \nLinkedin, Naukari, Monster India, Internshala, Time Jobs and Indeed \nand show best jobs here. The user can compare and apply to these jobs"
    " through the links. *Please don't Copyright this bot.* The sole purpose of this bot is to provide information about jobs and source link is provided with the jobs. "
    "Sometimes bot might not show results, this might occur due to some technical fault. In cases like this please inform us by writing a feedback. "
    "Write a feedback by typing *Feedback* if you have any question or complain.", parse_mode="Markdown")


##____________________Thanks_____________________##

@bot.message_handler(func=lambda msg: msg.text is not None and ("thank" in msg.text.lower() or "thanks" in msg.text.lower() or "thankyou" in msg.text.lower()))
def send_greetings(message):
    bot.reply_to(message, "Welcome 😊. You can update jobs again by typing *Update*.", parse_mode="Markdown")


##_________________Donation_______________________##
##Work_Left

@bot.message_handler(func=lambda msg: msg.text is not None and ("donation" in msg.text.lower() or "donate" in msg.text.lower() or "pay" in msg.text.lower()))
def send_donation(message):
    owner_id = 872448274
    bot.reply_to(message, "Thank you for your support, we will add a donation link soon. 😊😊", parse_mode="Markdown")
    bot.send_message(owner_id, f"Donation: {message.from_user.first_name}")


##_________________Update___________________##

@bot.message_handler(func=lambda msg: msg.text is not None and ("update" in msg.text.lower() or "new" in msg.text.lower() or "jobs" in msg.text.lower() or "job" in msg.text.lower() or "updated" in msg.text.lower()))
def send_update(message):
    chat_id = message.chat.id
    df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
    li = df_read.loc[df_read["Chat_ID"]== chat_id, "Subscription"]
    if li.array[0] == 1:
        msg = bot.send_message(chat_id, "Please write your prefered Job field.\nExample: *Teaching*\n "
        "\n🔴 If you don't have any prefarable Job field type *Na*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, location)
    else:
        bot.send_message(chat_id, "You have paused your subscription, please type /on to resume it.")

def location(message):
    chat_id = message.chat.id
    try:
        jf = message.text
        try:
            if jf.lower() == "/start":
                send_welcome
        except:
            bot.send_message(chat_id, "Invalid input please try again.")
        user = Job(jf)
        user_details[chat_id] = user
        msg = bot.send_message(chat_id, "Please write your prefered Location.\nExample: *Kolkata*\n "
        "\n🔴 If you don't have any prefarable Location type *Na*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, company)
    except:
        bot.send_message(chat_id,"Something went wrong please try again.")

def company(message):
    chat_id = message.chat.id
    try:
        loc = message.text
        try:
            if loc.lower() == "/start":
                send_welcome
        except:
            bot.send_message(chat_id, "Invalid input please try again.")
        user = user_details[chat_id]
        user.location = loc
        msg = bot.send_message(chat_id, "Please write your prefered Company.\nExample: *Amazon*\n "
        "\n🔴 If you don't have any prefarable Company type *Na*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, at_answer)
    except:
        bot.send_message(chat_id,"Something went wrong please try again.")

def at_answer(message):
    chat_id = message.chat.id
    try:
        com = message.text
        try:
            if com.lower() == "/start":
                send_welcome
        except:
            bot.send_message(chat_id, "Invalid input please try again.")
        user = user_details[chat_id]
        user.company = com
        bot.send_message(chat_id, "Please wait I'm searching best jobs for you.")        
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        df_read = pd.read_csv(os.path.join(sys.path[0],"customer_list.csv"))
        df_read.loc[df_read["Chat_ID"]== chat_id, "Last_Used"] = dt_string
        df_read.loc[df_read["Chat_ID"]== chat_id, "Last_Job"] = user.job_field
        df_read.loc[df_read["Chat_ID"]== chat_id, "Last_Location"] = user.location
        df_read.loc[df_read["Chat_ID"]== chat_id, "Last_Company"] = user.company
        df_read.to_csv(os.path.join(sys.path[0],"customer_list.csv"), index = False)

        search_jobs(user.job_field, user.location, user.company, chat_id)
    except Exception as e:
        bot.send_message(chat_id, e)


##________________Bot_Run____________##

@server.route('/' + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stram.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://fast-brook-37232.herokuapp.com/" + token)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port= int(os.environ.get("PORT", 5000)))