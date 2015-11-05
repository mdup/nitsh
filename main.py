from twx.botapi import TelegramBot, ReplyKeyboardMarkup
import re

"""
Setup the bot
"""

def process_update(bot, update):
    if update.message.text is None:
        pass
    match = re.search('^[Nn]it[sc]+h+ *: *(.*)', update.message.text);
    if match:
        msg = match.group(1)
        chatid = update.message.chat.id
        bot.send_message(chatid, 'Je dis ' + msg).wait()

def main():
    try:
        with open('API_KEY', 'r') as f:
            api_key = f.read().replace('\n', '')
    except IOError:
        print "please write the api key in file `API_KEY`"
        exit(1)

    bot = TelegramBot(api_key)
    bot.update_bot_info().wait()
    print(bot.username)

    last_update_id = int(0)
    while True:
        try:
            updates = bot.get_updates(offset=last_update_id+1).wait()
            for update in updates:
                last_update_id = update.update_id
                print(update)
                process_update(bot, update)
        except KeyboardInterrupt:
            # Allow ctrl-c.
            raise KeyboardInterrupt
        except Exception as e:
            print e
            pass

if __name__ == '__main__':
    main()
