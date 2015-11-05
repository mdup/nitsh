from twx.botapi import TelegramBot, ReplyKeyboardMarkup
import re

"""
Setup the bot
"""

try:
    with open ('API_KEY', 'r') as myfile:
        api_key=myfile.read().replace('\n', '')
except IOError:
    print "please write the api key in file `API_KEY`"
    exit(1)

bot = TelegramBot(api_key)
bot.update_bot_info().wait()
print(bot.username)

"""
Send a message to a user
"""
#user_id = int(<someuserid>)
#result = bot.send_message(user_id, 'test message body').wait()
#print(result)

"""
Get updates sent to the bot
"""
last_update_id = int(0)
while True:
    updates = bot.get_updates(offset=last_update_id+1).wait()
    for update in updates:
        last_update_id = update.update_id
        print(update)
        if update.message.text is None:
            continue
        match = re.search('^[Nn]it[sc]+h+ *: *(.*)', update.message.text);
        if match:
            answer = match.group(1)
            bot.send_message(update.message.chat.id, 'Je dis ' + answer).wait()

"""
Use a custom keyboard
"""
#keyboard = [
#    ['7', '8', '9'],
#    ['4', '5', '6'],
#    ['1', '2', '3'],
#         ['0']
#]
#reply_markup = ReplyKeyboardMarkup.create(keyboard)

#bot.send_message(user_id, 'please enter a number', reply_markup=reply_markup).wait()
#bot.send_message(user_id, 'please enter a number', reply_markup=reply_markup).wait()
