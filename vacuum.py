import pymysql.cursors
from config import *
import urllib.request, json

class Vacuum:
    def __init__(self):
        pass

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com',user=db_secrets[0],password=db_secrets[1],db='ligyptto_minecraft',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)


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
        with urllib.request.urlopen("http://136.33.144.178:8123/up/world/DIM-11/") as url:
            data = json.loads(url.read().decode())
            pl=data['players']
            players=[]
            query = "insert into `progress_playertracker` (player) VALUES "
            for p in pl:
                players.append(p['name'])
                query=query+"(%s),"

            query=query[:-1]

            self.do_insert(query,players)





    def add_death_message(self,message):
        m = message.split()
        m[1] = m[1].lower()  #case insensitivity support for player name

        #now i need to combine the death reason into a string, which will be words in positions 2-n of the death message 'm'
        dmsg=''
        for i in m[2:]:
            dmsg=dmsg+" "+i
        dmsg=dmsg.strip()

        self.do_insert("INSERT INTO `progress_deaths` (`player`,`message`) VALUES(%s, %s);",(m[1],dmsg))

    def top_10_deaths(self):

        result = self.do_query("SELECT player, count(*) as `count` FROM `progress_deaths` GROUP BY player ORDER BY count DESC LIMIT 10",'')
        if result:
            cmsg = ''
            i = 1
            for d in result:
                if i != 1:
                    cmsg = cmsg + ', '
                cmsg = cmsg + d['player'] + '(' + str(d['count']) + ')'
                i = i + 1
            return cmsg
        else:
            pass

    def ouchies_profile(self,player):
        result=self.do_query("SELECT message,count(*) as `count` FROM `progress_deaths` WHERE player=%s GROUP BY message ORDER BY count DESC",player)
        if result:
            cmsg = ''
            i = 1
            for d in result:
                if i != 1:
                    cmsg = cmsg + ', '
                cmsg = cmsg + d['message'] + '(' + str(d['count']) + ')'
                i = i + 1
            return cmsg
        else:
            return 'No deaths recorded'

    def top_10_death_reasons(self):
        result = self.do_query("SELECT message, count(*) as `count` FROM `progress_deaths` GROUP BY message ORDER BY count DESC LIMIT 10",'')
        if result:
            cmsg = ''
            i = 1
            for d in result:
                if i != 1:
                    cmsg = cmsg + ', '
                cmsg = cmsg + d['message'] + '(' + str(d['count']) + ')'
                i = i + 1
            return cmsg
        else:
            pass





