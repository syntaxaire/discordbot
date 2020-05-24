import datetime
import logging
import random

from discord.ext.commands import Bot, Cog, Context, command

from shared import db

log = logging.getLogger('bot.' + __name__)


class VacuumCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    @command
    def lastseen(ctx: Context, *args):
        try:
            player = args[0]
            if player:

                lastseen = db["minecraft"].do_query(
                    "select datetime from progress_playertracker_v2 "
                    "where player=%s order by datetime desc limit 1".format(),
                    (player,)
                )
                db["minecraft"].close()
                try:
                    lastseen = lastseen[0]['datetime']
                    now = datetime.datetime.utcnow()

                    timedelta = now - lastseen
                    seconds = abs(timedelta.total_seconds())
                    if seconds > 15:
                        days, remainder = divmod(seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        ctx.send('last saw %s %s days %s hours ago' % (player, int(days), int(hours)))
                    else:
                        ctx.send("Did you remember to wear your helmet today, honey?")
                except IndexError:
                    ctx.send("Havent seen em")
        except IndexError:
            ctx.send("who am i looking for?")

    @command
    def playtime(self, ctx: Context, *args):
        try:
            player = args[0]
            if player:
                returnz = self.playtime_insult(player)
                if returnz:
                    ctx.send(returnz)
            else:
                ctx.send(self.playtime_global())
        except IndexError:
            ctx.send(self.playtime_global())

    @staticmethod
    def playtime_global():
        players = db["minecraft"].do_query(
            "select abs(sum(timedelta)) as seconds, count(timedelta)"
            " as sessions, player from progress_playertracker_v2 group by player")
        db["minecraft"].close()
        total_seconds = 0
        total_sessions = 0
        for p in players:
            total_seconds = total_seconds + int(p['seconds'])
            total_sessions = total_sessions + p['sessions']
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        return ("These fucking nerds have played %s days, %s hours worth of meincraft over %s sessions" % (
            days, hours, total_sessions))

    @staticmethod
    def playtime_single(player):
        time = db["minecraft"].do_query(
            "select sum(progress_playertracker_v2.timedelta) as seconds, "
            "count(progress_playertracker_v2.timedelta) as sessions "
            "from progress.progress_playertracker_v2 where player in "
            "(select player_name from progress.minecraft_players "
            "where player_guid = (select player_guid as guid from progress.minecraft_players where player_name = %s))",
            (player,))
        db["minecraft"].close()
        return [time[0]['seconds'], time[0]['sessions']]

    def playtime_insult(self, player):
        a = self.playtime_single(player)
        totaltime = a[0]
        sessions = a[1]
        if not totaltime == 0:
            m, s = divmod(totaltime, 60)
            h, m = divmod(m, 60)
            insult = ""
            if h > 1000:
                insult = ". i found kurr lol"
            elif h > 150:
                insult = ". why are you still so bad at this game"
            elif h > 80:
                insult = ". is this shit your full time job or something"
            elif h > 50:
                insult = ". go outside you fuckin nerd"
            elif h > 30:
                insult = ". don't you have something better to do with your time?"
            elif h < 25:
                insult = ". weak"

            return "Estimated playtime for %s: %d hours %d minutes in %s sessions%s" % (player, h, m, sessions, insult)
        else:
            return "bitch dont play"

    def howchies_profile(self, message):
        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s)"
            "GROUP BY player ORDER by count DESC",
            message)
        db["minecraft"].close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self, player):
        result = db["minecraft"].do_query(
            "SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s"
            " GROUP BY message ORDER BY count DESC",
            (player,))
        db["minecraft"].close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    @command
    def howchies(self, message):
        if message:
            return "People who died to " + message + ": " + self.howchies_profile(message)
        else:
            return 'Heres whats killing you: ' + self.top_10_death_reasons()

    def top_10_death_reasons(self):
        result = db["minecraft"].do_query(
            "SELECT message, count(*) as `count` FROM `progress_deaths` "
            "GROUP BY message ORDER BY count DESC LIMIT 10",
            '')
        db["minecraft"].close()
        if result:
            return self.sort(result, 'message', 'count')
        else:
            pass

    @command
    def ouchies(self, message):
        if message:
            return "Deaths for %s: %s" % (message, self.ouchies_profile(message))
        else:
            return 'Top 10 ouchies: %s' % self.top_10_deaths()

    @command
    def alias(self, player):
        names = self.player_alias(player)
        if len(names) == 0:
            return "I dont think i've ever seen that butt"
        elif len(names) == 1:
            return "I've only seen this jerk as %s" % names[0]
        else:
            return "I've seen this jerk play as %s" % ", ".join(names)

    def top_10_deaths(self):

        result = db["minecraft"].do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",
            '')
        db["minecraft"].close()
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass

    def deathsperhour_list(self):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta) / 60 / 60) as deaths_per_hour"
            "FROM progress.progress_playertracker_v2 as T left join(SELECT count(D.player) as deaths, "
            "D.player from progress.progress_deaths D GROUP BY D.player) D ON T.player = D.player group by"
            "T.player ORDER BY deaths_per_hour DESC LIMIT 10"
        )
        if dph:
            return self.sort(dph, 'player', 'deaths_per_hour')

    @command
    def deathsperhour(self, player):
        dph = db["minecraft"].do_query(
            "select T.player, COALESCE(D.deaths, 0) / (sum(T.timedelta)/60/60) as deaths_per_hour FROM "
            "progress.progress_playertracker_v2 as T left join (SELECT count(D.player) as deaths, D.player"
            " from progress.progress_deaths D where player=%s GROUP BY D.player) D"
            " ON T.player = D.player where T.player=%s group by T.player", (player, player))
        db["minecraft"].close()
        try:
            if dph[0]['deaths_per_hour'] > 0:
                # good return
                if dph[0]['deaths_per_hour'] > 5:
                    insults = [
                        "my hero",
                        "a true gaming legend"
                    ]
                    insult = insults[random.randrange(0, len(insults) - 1)]

                else:
                    insult = "you should try harder"
                return "deaths per hour for %s is %s. %s" % \
                       (player,
                        str(dph[0]['deaths_per_hour']),
                        insult)
            else:
                comments = [
                    "%s is the most boring person on the server",
                    "actually, %s is just a gaming god",
                    "persistence is key for %s",
                    "%s is a god among mortals"
                ]
                return comments[random.randrange(0, len(comments)) - 1] % player
        except IndexError:
            return "%s doesnt play" % player

    @staticmethod
    def player_alias(player):
        db["minecraft"].build()
        r = db["minecraft"].do_query("select player_name from minecraft_players where player_guid ="
                                     " (select player_guid as guid from minecraft_players where player_name = %s)",
                                     (player,))
        names = []
        for re in r:
            names.append(re['player_name'])
        return names

    @staticmethod
    def sort(target, t1, t2):
        cmsg = ''
        i = 1
        for d in target:
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[t1] + '(' + str(d[t2]) + ')'
            i = i + 1
        return cmsg
