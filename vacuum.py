import pymysql.cursors
from config import *
import urllib.request, json, urllib.error, http.client
import datetime


class Vacuum:
    def __init__(self):
        self.players = []

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com', user=db_secrets[0], password=db_secrets[1],
                                          db=db_secrets[2], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def config(self, url, mode):
        self.updateurl = url
        self.master_config = mode

    def do_query(self, query, args=''):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
        finally:
            self.connection.close()
        return (result)

    def playtime_global(self):
        players = self.do_query(
            "select abs(sum(timedelta)) as seconds, count(timedelta) as sessions, player from progress_playertracker_v2 group by player")
        total_seconds = 0
        total_sessions = 0
        for p in players:
            total_seconds = total_seconds + int(p['seconds'])
            total_sessions = total_sessions + p['sessions']
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        return ("These fucking nerds have played %s days, %s hours worth of meincraft over %s sessions" % (
            days, hours, total_sessions))

    def playtime_single(self, player):
        time = self.do_query(
            "select sum(timedelta) as seconds, count(timedelta) as sessions from progress_playertracker_v2 where player=%s",
            player)
        return [time[0]['seconds'], time[0]['sessions']]

    def playtime_insult(self, player):
        a = self.playtime_single(player)
        totaltime = a[0]
        sessions = a[1]
        if not totaltime == 0:
            m, s = divmod(totaltime, 60)
            h, m = divmod(m, 60)
            insult = ""
            if h > 80:
                insult = ". is this shit your full time job or something"
            elif h > 50:
                insult = ". go outside you fuckin nerd"
            elif h > 30:
                insult = ". don't you have something better to do with your time?"

            return "Estimated playtime for %s: %d hours %d minutes in %s sessions%s" % (player, h, m, sessions, insult)
        else:
            return "bitch dont play"

    def do_insert(self, query, args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                self.connection.commit()
                cursor.close()
        finally:
            self.connection.close()

    def playtime_scraper(self):
        try:
            with urllib.request.urlopen(self.updateurl) as url:
                data = json.loads(url.read().decode())
                pl = data['players']
                players = []
                for p in pl:
                    p = p['name']
                    players.append(p)
                    # we start by checking to see if the player is currently active
                    if self.playtime_player_active(p):
                        pass
                        # player was logged in, and is still logged in
                        # we do not need to do anything for this player at this time.
                    else:
                        print("adding player %s since they have logged in" % p)
                        # player was not logged in, but is logged in now.
                        self.playtime_player_addplayer(p)
                # now we are going to find players that have logged out since the last check
                self.playtime_player_checkplayers(players)

        except urllib.error.URLError:
            # minecraft server is offline and buttbot is still online
            self.playtime_player_saveall()

        except http.client.RemoteDisconnected:
            # we are going to save all data here too
            self.playtime_player_saveall()

        finally:
            pass

    def playtime_player_checkplayers(self, players):
        for e in self.players:
            if e[0] in players:
                pass
                # person is still logged in. we do not need to do anything at this time.
            else:
                # log that they logged out
                print("%s has logged out" % e[0])
                self.playtime_player_record(e[0], self.playtime_player_deltaseconds(e[1]))
                # remove player.
                self.playtime_player_removeplayer(e)

    def playtime_player_deltaseconds(self, startTime):
        d = startTime - datetime.datetime.utcnow()
        d = abs(int(d.total_seconds()))
        if d > 20:
            d = d - 10
        return d

    def playtime_player_saveall(self):
        for e in self.players:
            self.playtime_player_record(e[0], self.playtime_player_deltaseconds(e[1]))
            # remove player.
            self.playtime_player_removeplayer(e)

    def playtime_player_record(self, player, deltatime):
        print("going to do query: user is %s and timedetla is %s" % (player, deltatime))
        self.do_insert("INSERT into `progress_playertracker_v2` (`player`,`timedelta`,`datetime`) values (%s,%s,%s)",
                       (player, deltatime, datetime.datetime.utcnow()))

    def playtime_player_addplayer(self, player):
        self.players.append([player, datetime.datetime.utcnow()])

    def playtime_player_removeplayer(self, player):
        self.players.remove(player)

    def playtime_player_active(self, player):
        try:
            if any(e[0] == player for e in self.players):
                return True
            else:
                return False
        except AttributeError:
            # the self.players variable is empty.  This can happen when the bot first turns on or when a player joins
            # and no one else is logged in.
            return False

    def lastseen(self, player):
        lastseen = self.do_query(
            "select datetime from progress_playertracker_v2 where player=%s order by datetime desc limit 1", player)
        try:
            lastseen = lastseen[0]['datetime']
            now = datetime.datetime.utcnow()

            timedelta = now - lastseen
            seconds = abs(timedelta.total_seconds())
            if seconds > 15:
                days, remainder = divmod(seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                return ('last saw %s %s days %s hours ago' % (player, int(days), int(hours)))
            else:
                return ("Did you remember to wear your helmet today, honey?")
        except IndexError:
            return ("Havent seen em")

    def get_player_coords(self, player):
        try:
            with urllib.request.urlopen(self.updateurl) as url:
                data = json.loads(url.read().decode())
                pl = data['players']
                for p in pl:
                    if p['name'] == player:
                        return {'x': p['x'], 'y': p['y'], 'z': p['z'], 'world': p['world']}
        except Exception:
            # we dont actually really care what the error is here, theres too many inside of url for me to care.
            # i'm just going to return the error handling coords:
            return {'x': 0, 'y': 0, 'z': 0, 'world': 'Exception Handling'}

    def add_death_message(self, message):
        m = message.split()
        m[1] = m[1].lower()  # case insensitivity support for player name
        coords = self.get_player_coords(m[1])
        # now i need to combine the death reason into a string, which will be words in positions 2-n of the death message 'm'
        dmsg = ''
        if m[2] == 'was':
            for i in m[3:]:
                dmsg = dmsg + " " + i
        else:
            for i in m[2:]:
                dmsg = dmsg + " " + i
        dmsg = dmsg.strip()
        try:
            self.do_insert(
                "INSERT INTO `progress_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`) VALUES(%s, %s, %s, %s, %s, %s, %s);",
                (m[1], dmsg, coords['world'], coords['x'], coords['y'], coords['z'], datetime.datetime.utcnow()))
        except TypeError:
            #catch this error, something that i dont believe should be possible with how this is set up but?????
            self.do_insert(
                "INSERT INTO `progress_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`) VALUES(%s, %s, %s, %s, %s, %s, %s);",
                (m[1], dmsg, "Exception Handling", 0, 0, 0, datetime.datetime.utcnow()))


    def top_10_deaths(self):

        result = self.do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",
            '')
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass

    def howchies_profile(self, message):
        result = self.do_query(
            "SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s) GROUP BY player ORDER by count DESC",
            message)
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self, player):
        result = self.do_query(
            "SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s GROUP BY message ORDER BY count DESC",
            player)
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    def top_10_death_reasons(self):
        result = self.do_query(
            "SELECT message, count(*) as `count` FROM `progress_deaths` GROUP BY message ORDER BY count DESC LIMIT 10",
            '')
        if result:
            return self.sort(result, 'message', 'count')
        else:
            pass

    def sort(self, target, t1, t2):
        cmsg = ''
        i = 1
        for d in target:
            if i != 1:
                cmsg = cmsg + ', '
            cmsg = cmsg + d[t1] + '(' + str(d[t2]) + ')'
            i = i + 1
        return cmsg
