import datetime
import http.client
import json
import urllib.error
import urllib.request
import random
import logging
import time
from butt_config import ButtConfig

from dateutil.parser import parse
import shared

log = logging.getLogger('bot.' + __name__)


class Vacuum:
    def __init__(self, config: ButtConfig):
        self.players = []
        self.playtime_load()
        self.updateurl = ""
        self.config = ""
        self.table_prefix = config.table_prefix
        self.NSA_module = config.nsa_module

        try:
            if self.players:
                pass
        except TypeError:
            # variable is empty instead of being an empty list
            self.players = []

    def playtime_scraper(self):
        log.debug("scraper started at %s" % str(time.time()))
        try:
            with urllib.request.urlopen(self.updateurl) as url:
                data = json.loads(url.read().decode())
                pl = data['players']
                players = []
                query_data = list()
                for p in pl:
                    log.debug("found player %s" % p['name'])
                    if self.NSA_module:
                        query_data.append((
                            datetime.datetime.utcnow(),
                            p['name'],
                            p['world'],
                            p['x'],
                            p['y'],
                            p['z']
                        ))
                    if not p['name'] in players:
                        players.append(p['name'])
                    # we start by checking to see if the player is currently active
                    if self.playtime_player_active(p['name']):
                        pass
                        # player was logged in, and is still logged in
                        # we do not need to do anything for this player at this time.
                    else:
                        log.debug("     adding player %s since they have logged in" % p['name'])
                        # player was not logged in, but is logged in now.
                        self.playtime_player_addplayer(p['name'])
                # now we are going to find players that have logged out since the last check
                if self.NSA_module:
                    shared.db['minecraft'].do_insertmany("INSERT INTO `{}_NSA_module`"
                                                         "(`datetime`, `player`, `dimension`, `x`, `y`, `z`) "
                                                         "VALUES (%s, %s, %s, %s, %s, %s)".format(self.table_prefix),
                                                         query_data)
                self.playtime_player_checkplayers(players)

        except urllib.error.URLError:
            # minecraft server is offline and buttbot is still online
            self.playtime_player_saveall()
            log.warning("scraper lost connection with minecraft server")

        except http.client.RemoteDisconnected:
            # we are going to save all data here too
            self.playtime_player_saveall()
            log.warning("scraper lost connection with minecraft server")

        finally:
            pass

    def playtime_player_checkplayers(self, players):
        try:
            for e in self.players:
                if e[0] in players:
                    pass
                    # person is still logged in. we do not need to do anything at this time.
                else:
                    # log that they logged out
                    self.playtime_player_record(e[0], self.playtime_player_deltaseconds(e[1]))
                    self.playtime_player_removeplayer(e)
        except TypeError:
            # something went wrong with variable initialization.
            self.players = []
            self.playtime_player_checkplayers(players)

    @staticmethod
    def playtime_player_deltaseconds(starttime):
        d = starttime - datetime.datetime.utcnow()
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
        shared.db["minecraft"].do_insert("INSERT into `{}_playertracker_v2`(`player`, `timedelta`, `datetime`)"
                                         " values( % s, % s, % s)".format(self.table_prefix),
                                         (player, deltatime, datetime.datetime.utcnow()))
        shared.db["minecraft"].close()

    def playtime_player_addplayer(self, player):
        log.debug("  adding player %s to serialized player list" % player)
        self.players.append([player, datetime.datetime.utcnow()])
        self.playtime_serialize()

    def playtime_player_removeplayer(self, player):
        log.debug("  removing player %s from serialized player list" % player)
        self.players.remove(player)
        self.playtime_serialize()

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

    def playtime_serialize(self):
        with open('players_%s.txt' % self.table_prefix, 'w') as f:
            json.dump(self.players, f, ensure_ascii=False, default=str)

    def playtime_load(self):
        try:
            with open('players_%s.txt' % self.table_prefix) as f:
                self.players = json.load(f)
        except FileNotFoundError:
            # nothing special needs to happen here
            pass
        for i in self.players:
            i[1] = parse(i[1])

    # noinspection PyBroadException
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
        # now i need to combine the death reason into a string, which will be words in positions 2-n of the death
        # message 'm'
        dmsg = ''
        if m[2] == 'was':
            for i in m[3:]:
                dmsg = dmsg + " " + i
        else:
            for i in m[2:]:
                dmsg = dmsg + " " + i
        dmsg = dmsg.strip()
        try:
            shared.db["minecraft"].do_insert(
                "INSERT INTO `{}_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`)"
                "VALUES(%s, %s, %s, %s, %s, %s, %s);".format(self.table_prefix),
                (m[1], dmsg, coords['world'], coords['x'], coords['y'], coords['z'], datetime.datetime.utcnow()))
        except TypeError:
            # catch this error, something that i dont believe should be possible with how this is set up but?????
            shared.db["minecraft"].do_insert(
                "INSERT INTO `{}_deaths` (`player`,`message`,`world`,`x`,`y`,`z`,`datetime`)"
                "VALUES(%s, %s, %s, %s, %s, %s, %s);".format(self.table_prefix),
                (m[1], dmsg, "Exception Handling", 0, 0, 0, datetime.datetime.utcnow()))
        shared.db["minecraft"].close()

    def have_we_seen_player(self, player):
        current_server_result = shared.db["minecraft"].do_query(
            "select count(datetime) from {}_playertracker_v2 where player=%s".format(self.table_prefix), (player,))
        previous_server_result = shared.db["minecraft"].do_query(
            "select count(datetime) from {}_playertracker_v2_old where player=%s".format(self.table_prefix), (player,))
        shared.db["minecraft"].close()
        if current_server_result[0]['count(datetime)'] == 0:
            # new player
            if previous_server_result[0]['count(datetime)'] > 0:
                comments = [
                    "welcome back to progress, %s",
                    "fuck, %s is back",
                    "who let %s back in?",
                    "who gave %s the new IP address?",
                    "%s is back to top ouchies!"
                ]
                message = random.randrange(0, len(comments) - 1)
                return message % player
            else:
                return "welcome to progress %s" % player


class VacuumManager(dict):
    def __init__(self):
        super().__init__()
        self.instances = {}

    def __getitem__(self, attr: int):
        try:
            return self.instances[attr]
        except KeyError:
            log.warning("attempted load vacuum manager on a non-subscribed channel")

    def subscribe(self, config: ButtConfig):
        log.info("new vacuum subscription started for guid %d. table prefix is %s" % (config.guid, config.table_prefix))
        self.instances[config.guid] = Vacuum(config)

    def unsubscribe(self, guild_guid):
        log.info("unsubscribing subscription for guid %d" % guild_guid)
        self.instances.pop(guild_guid)
