#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime, timedelta
import sys
import re

default_hours = 9
default_mins = 0
morning_hours = 8
noon_hours = 12
afternoon_hours = 15
evening_hours = 21
night_hours = 23


remindme_regex = re.compile("^[rR]app?el[^ ]*( ?moi)? ?(de|d'?|que|qu'?)?")
today_regex = re.compile("aujourd([' ]?hui)?")
dat_regex = re.compile(u"apr[eè]s[- ]demain") # 'd'ay 'a'fter 't'omorrow
tomorrow_regex = re.compile("demain")
mon_regex = re.compile("lundi( *prochain)")
tue_regex = re.compile("mardi( *prochain)")
wed_regex = re.compile("mercredi( *prochain)")
thu_regex = re.compile("jeudi( *prochain)")
fri_regex = re.compile("vendredi( *prochain)")
sat_regex = re.compile("samedi( *prochain)")
sun_regex = re.compile("dimanche( *prochain)")
day_regexes = [today_regex, dat_regex, tomorrow_regex, 
    mon_regex, tue_regex, wed_regex, thu_regex, fri_regex, sat_regex, sun_regex]
timeprefix = u"(le|l'|à|a|au|du|ce|cet|cette|) *"
morning_regex = re.compile(timeprefix + "matin[^ ]*")
noon_regex = re.compile(timeprefix + "midi")
afternoon_regex = re.compile(timeprefix + u"apr[eè]s[- ]*midi")
evening_regex = re.compile(timeprefix + u"soir[^ ]*")
night_regex = re.compile(timeprefix + "nuit[^ ]*")
time_regex = re.compile(
    # 1. 
    u"([aà]|vers|pour|d'ici|autour *de|) *" +
    # 2. hours      3      4
    u"([0-9]{1,2}) *(:|[hH](eures?)?) *" +
    # 5. mins
    u"([0-9]{0,2})"
)
time_regexes = [time_regex, morning_regex, afternoon_regex, noon_regex,
    evening_regex, night_regex] # afternoon BEFORE noon
intime_regex = re.compile(
    "dans *" +
    #12             3      4           5
    "(([0-9]{1,2}) *(:|[hH](eures?)?) *(et)?)? *" +
    #6 7             8    9
    "(([0-9]{1,2}) *([mM](in(ute)?)?s?)?)?"
)


def has_one(s1, s2):
    return len(set(s1).intersection(set(s2))) > 0

class Reminder:
    forced_now = None

    def __init__(self, when, what):
        self.when = when;
        self.what = what

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.when == other.when 
            and self.what == other.what)

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def now(cls):
        return cls.forced_now if cls.forced_now else datetime.now()

    def __str__(self):
        return unicode(self.what) + ", le " + unicode(self.when.day) + "/" + unicode(self.when.month) + \
            u" à " + unicode(self.when.hour) + ":" + ("0" if self.when.minute < 10 else "") + unicode(self.when.minute)

    @classmethod
    def parse(cls, sentence):
        if not remindme_regex.search(sentence):
            return None

        ### remove beginning of sentence
        sentence = remindme_regex.sub('', sentence)

        ### day ###
        dat = dat_regex.search(sentence)
        tomorrow = not dat and tomorrow_regex.search(sentence)
        today = not tomorrow and not dat and today_regex.search(sentence)
        mon = mon_regex.search(sentence)
        tue = tue_regex.search(sentence)
        wed = wed_regex.search(sentence)
        thu = thu_regex.search(sentence)
        fri = fri_regex.search(sentence)
        sat = sat_regex.search(sentence)
        sun = sun_regex.search(sentence)

        # remove day info from sentence
        for regex in day_regexes:
            sentence = regex.sub('', sentence)


        ### intime ###
        intime = intime_regex.search(sentence)
        if intime:
            if not intime.group(2) and not intime.group(6):
                intime = False
            else:
                in_hours = int(intime.group(2)) if intime.group(2) else 0
                in_mins = int(intime.group(7)) if intime.group(7) else 0

        # remove from sentence
        sentence = intime_regex.sub('', sentence)

        ### time ###
        hours = default_hours
        mins = default_mins
        if not intime:
            morning = morning_regex.search(sentence)
            afternoon = afternoon_regex.search(sentence)
            noon = noon_regex.search(sentence)
            evening = evening_regex.search(sentence)
            night = night_regex.search(sentence)
            if morning:
                hours = morning_hours
            elif afternoon: # check before noon!
                hours = afternoon_hours
            elif noon:
                hours = noon_hours
            elif evening:
                hours = evening_hours
            elif night:
                hours = night_hours

            match = time_regex.search(sentence)
            if match:
                hours = int(match.group(2))
                mins = int(match.group(5)) if match.group(5) != '' else 0

            if morning and hours > 12:
                hours -= 12
            elif (afternoon or evening) and hours < 12:
                hours += 12

        # remove time from sentence
        for regex in time_regexes:
            sentence = regex.sub('', sentence)

        ### now we manipulate the clock object
        clock = Reminder.now()
        if dat:
            clock += timedelta(days=2)
        elif tomorrow:
            clock += timedelta(days=1)
        elif today:
            pass
        elif mon or tue or wed or thu or fri or sat or sun:
            wanted_weekday = \
                0 if mon else \
                1 if tue else \
                2 if wed else \
                3 if thu else \
                4 if fri else \
                5 if sat else 6
            for i in xrange(1, 7):
                later = clock + timedelta(days=i)
                if later.weekday() == wanted_weekday:
                    clock = later
                    break
                raise "unreachable: weekday not found"
        clock = clock.replace(second=0, microsecond=0)
        if intime:
            clock += timedelta(hours=in_hours, minutes=in_mins)
        else:
            clock = clock.replace(hour=hours, minute=mins, second=0, microsecond=0)

        if clock < Reminder.now():
            clock += timedelta(days=1)
        if clock < Reminder.now():
            raise "invalid"

        
        ### unduplicate spaces
        sentence = re.compile(' +').sub(' ', sentence)
        sentence = re.compile('^ *').sub('', sentence)
        sentence = re.compile(' *$').sub('', sentence)

        ### what's remaining in the sentence should be the reason... hopefully
        return Reminder(clock, sentence)



def run_tests():
    Reminder.forced_now = datetime(2015, 11, 5, 12, 44, 45)

    in_one_hour        = datetime(2015, 11, 5, 13, 44, 00, 000000)
    in_two_hours       = datetime(2015, 11, 5, 14, 44, 00, 000000)
    in_two_hours_30    = datetime(2015, 11, 5, 15, 14, 00, 000000)
    in_5_min           = datetime(2015, 11, 5, 12, 49, 00, 000000)
    in_20_min          = datetime(2015, 11, 5, 13, 04, 00, 000000)
    tonight            = datetime(2015, 11, 5, 21, 00, 00, 000000)
    at_20              = datetime(2015, 11, 5, 20, 00, 00, 000000)
    at_20_30           = datetime(2015, 11, 5, 20, 30, 00, 000000)
    tomorrow_morning   = datetime(2015, 11, 6,  8, 00, 00, 000000)
    tomorrow_afternoon = datetime(2015, 11, 6, 15, 00, 00, 000000)
    tomorrow_at_16     = datetime(2015, 11, 6, 16, 00, 00, 000000)
    tomorrow_at_16_30  = datetime(2015, 11, 6, 16, 30, 00, 000000)
    tomorrow_at_8_30   = datetime(2015, 11, 6, 8, 30, 00, 000000)
    a = [
        (u"blabla", None),
        (u"rappelle-moi de manger ce soir", Reminder(tonight, "manger")),
        (u"rappelle-moi de manger à 20h", Reminder(at_20, "manger")),
        (u"rappelle-moi de manger à 20h30", Reminder(at_20_30, "manger")),
        #("rappelle-moi de manger", Reminder(tomorrow_morning, "manger")),
        (u"rappelle-moi de manger demain matin", Reminder(tomorrow_morning, "manger")),
        (u"rappelle-moi de manger demain après-midi", Reminder(tomorrow_afternoon, "manger")),
        (u"rappelle-moi de manger demain à 16h", Reminder(tomorrow_at_16, "manger")),
        (u"rappelle-moi de manger à 8:30", Reminder(tomorrow_at_8_30, "manger")),
        #(u"rappelle-moi de manger dans une heure", Reminder(in_one_hour, "manger")),
        (u"rappelle-moi de manger dans 1 heure", Reminder(in_one_hour, "manger")),
        (u"rappelle-moi de manger dans 1h", Reminder(in_one_hour, "manger")),
        (u"rappelle-moi de manger dans 2h30", Reminder(in_two_hours_30, "manger")),
        (u"rappelle-moi de manger dans 2 heures et 30 minutes", Reminder(in_two_hours_30, "manger")),
        #(u"rappelle-moi de manger dans deux heures et trente minutes", Reminder(in_two_hours_30, "manger")),
        (u"rappelle-moi de manger dans 5min", Reminder(in_5_min, "manger")),
        (u"rappelle-moi de manger dans 20 minutes", Reminder(in_20_min, "manger")),
    ]

    for (sentence, expected) in a:
        sys.stdout.write("testing '" + sentence + "'... ")
        got = Reminder.parse(sentence)
        if (expected != got):
            print "wrong! got " + unicode(got) + ", expected " + unicode(expected)
            print "test failed, exiting."
            exit()
        else:
            print "ok, got " + unicode(got)
        

if __name__ == '__main__':
    run_tests()
