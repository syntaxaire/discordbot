import pymysql.cursors
from config import *
import urllib.request, json
import datetime

class Vacuum:
    def __init__(self):
        pass

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com',user=db_secrets[0],password=db_secrets[1],db=db_secrets[2],charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    def config(self,url,mode):
        self.updateurl=url
        self.master_config=mode

    def do_query(self,query,args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                if args:
                    cursor.execute(query,args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
        finally:
            self.connection.close()
        return (result)

    def playtime(self,player):
        query=self.do_query("select datetime from ligyptto_minecraft.progress_playertracker where player=%s",player)
        totaltime=0
        sessions=0
        sessiontimestamps=0
        print(query)
        for ts in query:
            ts=ts['datetime']
            try:
                if previous is None:
                    previous=ts #this is the start
                    sessiontimestamps=sessiontimestamps+1
                else:
                    timedelta=previous-ts
                    seconds=abs(timedelta.total_seconds())
                    if seconds < 20:
                        #this is a break in play
                        previous=None
                        if sessiontimestamps==1:
                            #special case - player was logged in for less than 20 seconds
                            totaltime=totaltime+10 #we'll just call this session 10 seconds.
                        elif sessiontimestamps==2:
                            #second special case - player was logged in for 2 timestamps so between 20-30 seconds.
                            totaltime=totaltime+20 #we'll call this one 20 seconds.
                        else:
                            totaltime=totaltime+((sessiontimestamps-1)*10) #we are going to remove one to better approximate the +- 10 seconds on both ends of the login sequence
                        #ok that bullshit is done lets do some hoose keeping
                        sessions = sessions + 1
                        sessiontimestamps=0
                        previous=None
                    else:
                        #this is a continuation of play
                        previous=ts
                        sessiontimestamps=sessiontimestamps+1
            except UnboundLocalError:
                previous = ts  # this is the start
                sessiontimestamps = sessiontimestamps + 1

        if not totaltime == 0:
            m, s = divmod(totaltime, 60)
            h, m = divmod(m, 60)
            return "%d hours %02d minutes" % (h, m)
        else:
            return "bitch dont play"



    def do_insert(self,query,args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query,args)
                self.connection.commit()
                cursor.close()
        finally:
            self.connection.close()


    def playtime_log(self):
        try:
            with urllib.request.urlopen(self.updateurl) as url:
                data = json.loads(url.read().decode())
                pl=data['players']
                players=[]
                query = "insert into `progress_playertracker` (datetime,player,world,armor,health,x,y,z) VALUES "
                for p in pl:
                    players.append(datetime.datetime.utcnow())
                    players.append(p['name'])
                    players.append(p['world'])
                    players.append(p['armor'])
                    players.append(p['health'])
                    players.append(p['x'])
                    players.append(p['y'])
                    players.append(p['z'])
                    query=query+"(%s, %s, %s, %s, %s, %s, %s, %s),"

                query=query[:-1]

                self.do_insert(query,players)

        except Exception:
            print("Playtime_Log::ERROR: Caught exception when trying to open Dynamap JSON file")


    def lastseen(self,player):
        lastseen=self.do_query("select datetime from progress_playertracker where player=%s order by datetime desc limit 1",player)
        try:
            lastseen=lastseen[0]['datetime']
            now = datetime.datetime.utcnow()

            timedelta=now-lastseen
            seconds=abs(timedelta.total_seconds())
            if seconds > 15:
                days,remainder=divmod(seconds,86400)
                hours, remainder = divmod(remainder, 3600)
                return('last saw %s %s days %s hours ago' % (player, int(days), int(hours)))
            else:
                return("Did you remember to wear your helmet today, honey?")
        except IndexError:
            return( "Havent seen em")


    def add_death_message(self,message):
        m = message.split()
        m[1] = m[1].lower()  #case insensitivity support for player name
        #try to update the location db rq to prevent an exception for new players
        self.playtime_log()
        #we are going to gather the player coords out of the tracking db to add to their death notice
        coords=self.do_query("select world, x, y, z from progress_playertracker where player=%s ORDER by id DESC limit 1",m[1])
        try:
            coords=coords[0]
        except IndexError:
            coords={'x':0,'y':0,'z':0,'world':'Exception Handling'}

        #now i need to combine the death reason into a string, which will be words in positions 2-n of the death message 'm'
        dmsg=''
        if m[2]== 'was':
            for i in m[3:]:
                dmsg = dmsg + " " + i
        else:
            for i in m[2:]:
                dmsg=dmsg+" "+i
        dmsg=dmsg.strip()
        self.do_insert("INSERT INTO `progress_deaths` (`player`,`message`,`world`,`x`,`y`,`z`) VALUES(%s, %s, %s, %s, %s, %s);",(m[1],dmsg,coords['world'],coords['x'],coords['y'],coords['z']))


    def top_10_deaths(self):

        result = self.do_query("SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",'')
        if result:
            return self.sort(result, 'player', 'count')
        else:
            pass


    def howchies_profile(self,message):
        result=self.do_query("SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s) GROUP BY player ORDER by count DESC",message)
        if result:
            return self.sort(result, 'player', 'count')
        else:
            return 'No deaths recorded'

    def ouchies_profile(self,player):
        result=self.do_query("SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s GROUP BY message ORDER BY count DESC",player)
        if result:
            return self.sort(result, 'message', 'count')
        else:
            return 'No deaths recorded'

    def top_10_death_reasons(self):
        result = self.do_query("SELECT message, count(*) as `count` FROM `progress_deaths` GROUP BY message ORDER BY count DESC LIMIT 10",'')
        if result:
            return self.sort(result,'message','count')
        else:
            pass

    def sort(self,target,t1,t2):
            cmsg = ''
            i = 1
            for d in target:
                if i != 1:
                    cmsg = cmsg + ', '
                cmsg = cmsg + d[t1] + '(' + str(d[t2]) + ')'
                i = i + 1
            return cmsg


