import MySQLDdb
from Frequencer.settings import *

try:
    conn=MySQLdb.connect(host=HOSTNAME,user='root',passwd='hohoyi123',port=3306, charset='utf-8')
    cur=conn.cursor()
     
    cur.execute('create database if not exists %s' % DBNAME)
    conn.select_db(DBNAME)
    cur.execute('create table if not exists %s(id varchar(255) primary key, frequency int' % TABLENAME)

    conn.commit()
    cur.close()
    conn.close()
 
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
