import MySQLdb
import sys
from settings import *
from .monitors import datadog
import logging

reload(sys)
sys.setdefaultencoding('utf-8')


class DBAdapter(object):
    def __init__(self, user, passwd, port=3306, encoding='utf8'):
#        self.conn = MySQLdb.connect(host=HOSTNAME,user=user,passwd=passwd,port=3306, charset=encoding)
#        self.cur = self.conn.cursor
        self._user = user
        self._passwd = passwd
        self._encoding = encoding
        self._port = port
        self.logger = logging.getLogger('DBAdapter')

    def create_db_or_table_if_not_exist(self):
        try:
            conn=MySQLdb.connect(host=DBHOST,user=self._user,passwd=self._passwd,port=self._port, charset=self._encoding)
            cur=conn.cursor()
             
            createdb_sql = 'create database if not exists %s' % DBNAME
            createtable_sql = 'create table if not exists %s(id varchar(255) primary key, frequency int)' % TABLENAME
            cur.execute(createdb_sql)
            conn.select_db(DBNAME)
            cur.execute(createtable_sql)

            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            if cur:
                cur.close()
            if conn:
                conn.close()
                    

    def insert_or_update_values(self, dic):
        try:
            conn=MySQLdb.connect(host=DBHOST,user=self._user,passwd=self._passwd,port=self._port, charset=self._encoding)
            cur=conn.cursor()
            
            conn.select_db(DBNAME)
            keys = dic.keys()
            length = len(keys)
            start = 0
            batch = 50
            sql = 'select * from %s where id in ' % TABLENAME
            insert_sql = 'insert into %s values' %  TABLENAME
            insert_sql = insert_sql + '(%s, %s)'
            update_sql = 'update %s set' % TABLENAME
            update_sql = update_sql + " frequency=%d where id = '%s'"

            while length > 0:
                insert = []
                update = {}
                if length > batch:
                    take = batch
                else:
                    take = length
                process = keys[start:start + take]
                self.logger.debug("Processing keys: %s" % ", ".join(process))
                params = ", ".join(map(lambda x: '%s', process))
                query = sql + '(%s)' % params
                cur.execute(query, process)
                results = cur.fetchall()
                for item in results:
                    value = item[1] + dic[item[0]]
                    update[item[0]] = value

                updatekeys = update.keys()
                for item in process:
                    if item not in updatekeys:
                        insert.append((item, dic[item]))

                #insert not found words
                self.logger.info("Inserting %d words to DB......" % len(insert))
                cur.executemany(insert_sql, insert)
                self.logger.info("dic.word.inserted: %d" % len(insert))
                datadog.gauge("dic.word.inserted", len(insert))
                self.logger.info("Updating existed words......")
                #update existed words
                for item in update:
                    q = update_sql % (update[item], item)
                    cur.execute(q)
                    datadog.gauge('dic.word.updated', 1)
                self.logger.info("dic.word.updated: %d" % len(update))
                start += take
                length = length - take
                conn.commit()

#            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            self.logger.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            self.logger.error(e)
            if cur:
                cur.close()
            if conn:
                conn.close()
            raise e


    def check_exist(self, words):
        pass


    def dump_all(self, targetfile=DUMP_DICFILE):
        try:
            conn=MySQLdb.connect(host=DBHOST,user=self._user,passwd=self._passwd,port=self._port, charset=self._encoding)
            cur=conn.cursor()            
            conn.select_db(DBNAME)

            query_all = 'select * from %s' % TABLENAME
            count = cur.execute(query_all)
            print("Total words: %d" % count)
            results = cur.fetchall()
            with open(targetfile, 'w+') as handler:
                for item in results:
                    handler.write(item[0] + '\t' + str(item[1]))
                    handler.write('\n')

            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            if cur:
                cur.close()
            if conn:
                conn.close()
            raise e

if __name__ == '__main__':
    adpt = DBAdapter("root", "hohoyi123")
    adpt.create_db_or_table_if_not_exist()
    testdata = {"jimmy": 12, "sunshine": 23, "microsoft": 4, "ivy": 9, 'bird': 16, "ipad": 2}
    adpt.insert_or_update_values(testdata)
    testdata2 = {"jimmy": 5, 'bird': 8, "ipad": 11, "apple": 7, "forest": 3}
    adpt.insert_or_update_values(testdata2)
