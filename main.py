#!/usr/bin/env python
# encoding: utf-8 -*-

from twx.botapi import TelegramBot, ReplyKeyboardMarkup
import re
import random
import traceback
import reminders
from datetime import datetime

bot = None

knowledge = {}

rems = []

def learn_sentence(sentence):
    sentence = sentence.lower()
    s = sentence.split(' ')
    print s
    s = [w for w in s if w != 'est' or w != 'a']
    s = [w for w in s if not is_stopword(w)]
    for w in s:
        print "Associating '" + w + "' to sentence '" + sentence + "'."
        knowledge[w] = sentence

def recall_knowledge(sentence, bot, update):
    sentence = sentence.lower()
    s = sentence.split(' ')
    for w in s:
        if w in knowledge:
            print "Knowledge about '" + w + "': '" + knowledge[w] + "'."
            chatid = update.message.chat.id
            msg = random_i_know() + ' ' + knowledge[w]
            bot.send_message(chatid, msg).wait()
            break
        else:
            print "I don't know about '" + w + "'."

def is_stopword(w):
    stopwords = [
        u"est", u"a", u"à", u"si", u"?",
        u"ailleurs", u"afin", u"de", u"que", u"ainsi", u"alors", u"après", u"au-dessous",
        u"au-dessus", u"aujourd’hui", u"auparavant", u"auprès", u"aussi", u"aussitôt",
        u"autant", u"autour", u"autrefois", u"autrement", u"avant", u"avec", u"beaucoup",
        u"bien", u"bientôt", u"car", u"ceci", u"cela", u"cependant", u"certes", u"chez",
        u"comme", u"comment", u"d'abord", u"dans", u"davantage", u"dedans", u"dehors", u"déjà",
        u"demain  ", u"depuis", u"dès lors", u"dès que", u"désormais", u"dessous", u"dessus",
        u"devant", u"donc", u"dont", u"dorénavant", u"durant", u"encore", u"enfin", u"ensuite",
        u"entre", u"envers", u"exprès", u"guère", u"gré", u"hélas", u"hier", u"hors", u"ici",
        u"jamais  ", u"là", u"loin", u"longtemps", u"lorsque", u"maintenant", u"mais",
        u"malgré", u"mieux", u"moins", u"naguère", u"néanmoins", u"non", u"par", u"parce que",
        u"par-dessous", u"par-dessus", u"parfois", u"parmi", u"pas", u"pendant", u"peu",
        u"plus", u"plusieurs", u"plutôt", u"pour", u"pourquoi", u"pourtant", u"près",
        u"presque", u"puis", u"quand", u"quelquefois", u"quoi", u"quoique", u"sans", u"sauf",
        u"selon", u"seulement", u"sinon", u"sitôt", u"soudain", u"sous", u"souvent", u"surtout",
        u"tant", u"tant", u"mieux", u"tantôt", u"pis", u"tard", u"tôt", u"toujours",
        u"toutefois", u"travers", u"très", u"trop", u"vers", u"voici", u"voilà", u"volontiers",
        u"vraiment",
        u"je", u"me", u"m", u"moi", u"tu", u"te", u"t", u"toi", u"nous", u"vous", u"il", u"elle",
        u"ils", u"elles", u"se", u"en", u"y", u"le", u"la", u"l", u"le", u"lui", u"soi", u"leur",
        u"eux", u"lui", u"leur", u"celui", u"celui-ci", u"celui-là", u"celle", u"celle-ci",
        u"celle-là", u"ceux", u"ceux-ci", u"ceux-là", u"celles", u"celles-ci", u"celles-là",
        u"ce", u"ceci", u"cela", u"ça", u"qui", u"que", u"quoi", u"dont", u"où", u"lequel",
        u"auquel", u"duquel", u"laquelle", u"lesquels", u"auxquels", u"desquels",
        u"lesquelles", u"auxquelles", u"desquelles", u"qui", u"que", u"quoi", u"qu'est-ce",
        u"lequel", u"auquel", u"duquel", u"laquelle", u"lesquels", u"auxquels", u"desquels",
        u"lesquelles", u"auxquelles", u"desquelles", u"on", u"tout", u"un", u"une", u"l'un",
        u"l'une", u"d'autres", u"l'autre", u"aucun", u"aucune", u"aucuns", u"aucunes",
        u"certains", u"certaine", u"certains", u"certaines", u"tel", u"telle", u"tels",
        u"telles", u"tout", u"toute", u"tous", u"toutes", u"nul", u"nulle", u"nuls", u"nulles",
        u"quelqu'un", u"quelqu'une", u"personne", u"aucun", u"autrui", u"quiconque",
        u"d’aucuns"
        ]

    return w in stopwords




def random_i_know():
    a = [u'Je crois que',
         u'On dit que',
         u'Euh... Il me semble que',
         u'Parfois',
         u'Heureusement',
         u"Un jour j'ai fait un voyage en bateau et j'ai appris que",
         u"Dommage, car",
         u"J'espère que vous êtes au courant que",
         u"Aujourd'hui,",
         u"A l'école j'ai appris que",
         u"Il pleut donc",
         u"Derrière toi",
         u"Au marché",
         u"Au football tout le monde sait que",
         u"The only thing I know in French is:",
         u"Tu sais que",
         u"La musique adoucit les moeurs et",
         u"J'ai un secret pour vous...",
         ]
    dice_roll = random.randint(0, len(a)-1)
    return a[dice_roll]




def process_update(bot, update):
    global rems
    if update.message.text is None:
        pass
    match = re.search('^[Nn]it[sc]+h+ *: *(.*)', update.message.text);
    if match:
        msg = match.group(1)
        chatid = update.message.chat.id
        question = re.search('\? *$', update.message.text)
        if question:
            recall_knowledge(update.message.text, bot, update)
        else:
            rem = reminders.Reminder.parse(msg)
            if rem:
                print "rem!!!"
                rem.chatid = chatid
                rem.id = random.randint(0, 999999) #not clean, but I want to go to bed now
                rems.append(rem)
                bot.send_message(chatid, u"OK! rappel " + str(rem.id) + ": \n\n"
                        + unicode(rem)).wait()
            else:
                match = re.search("[sS]upprimer? *(le)? *rappel *([0-9]+)", update.message.text)
                if match:
                    remid = int(match.group(2))
                    print "removing reminder " + str(remid)
                    rems = [rem for rem in rems if rem.id != remid]
                    print "rems = " + str(rems)
                    bot.send_message(chatid, u'Très bien, le rappel ' + str(remid) + u' est supprimé.').wait()
                else:
                    bot.send_message(chatid, 'Je dis ' + msg).wait()
                    learn_sentence(msg)
    else:
        learn_sentence(update.message.text)

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
            updates = bot.get_updates(offset=last_update_id+1, timeout=5).wait()
            for update in updates:
                last_update_id = update.update_id
                print(update)
                process_update(bot, update)
            global rems
            for rem in rems:
                if rem.when < datetime.now():
                    bot.send_message(rem.chatid, "=== RAPPEL ===\n\n" +
                            unicode(rem.what))
                    print "removing reminder " + str(rem.id)
                    rems = [r for r in rems if r.id != rem.id]
                    print "rems = " + str(rems)

        except KeyboardInterrupt:
            # Allow ctrl-c.
            raise KeyboardInterrupt
        except Exception as e:
            print "---\nException: "
            print e
            traceback.print_exc()
            pass

if __name__ == '__main__':
    main()
