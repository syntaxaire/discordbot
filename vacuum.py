import pymysql.cursors
from config import *
import urllib.request, json

class Vacuum:
    def __init__(self):
        pass

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com',user=db_secrets[0],password=db_secrets[1],db=db_secrets[2],charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    def config(self,url):
        self.updateurl=url

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


    def do_insert(self,query,args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                #sql = "SELECT * FROM `progress_deaths` WHERE 1"
                cursor.execute(query,args)
                self.connection.commit()
                cursor.close()
        finally:
            self.connection.close()


    def playtime_log(self):
        with urllib.request.urlopen(self.updateurl) as url:
            data = json.loads(url.read().decode())
            pl=data['players']
            players=[]
            query = "insert into `progress_playertracker` (player,world,armor,health,x,y,z) VALUES "
            for p in pl:
                players.append(p['name'])
                players.append(p['world'])
                players.append(p['armor'])
                players.append(p['health'])
                players.append(p['x'])
                players.append(p['y'])
                players.append(p['z'])
                query=query+"(%s, %s, %s, %s, %s, %s, %s),"

            query=query[:-1]

            self.do_insert(query,players)





    def add_death_message(self,message):
        m = message.split()
        m[1] = m[1].lower()  #case insensitivity support for player name

        #we are going to gather the player coords out of the tracking db to add to their death notice
        coords=self.do_query("select world, x, y, z from progress_playertracker where player=%s ORDER by id DESC limit 1",m[1])
        coords=coords[0]
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
        result=self.do_query("SELECT player, count(*) as `count` FROM `progress_deaths` where match(message) against (%s)",message)
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


