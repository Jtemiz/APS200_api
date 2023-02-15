import logging
import traceback

import pymysql
from dbutils.persistent_db import PersistentDB
import globals as glob

db_config = {
    'host': '127.0.0.1',
    'user': 'messmodul',
    'password': 'Jockel01.',
    'database': 'MESSDATEN',
    'connect_timeout': 5
}

mysql_connection_pool = PersistentDB(
    creator=pymysql,
    **db_config
)

def createTable(tableName):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "CREATE TABLE `" + tableName + "` LIKE `ExampleTable`;"
        cursor.execute(sql)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.createTable(): " + str(ex) + "\n" + traceback.format_exc())

def insertTable(tableName):
    try:
        SqlData = list([(i['position'], i['height'], i['speed'], i['strWidth'], i['limVal']) for i in glob.LONGTERM_VALUES])
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "INSERT INTO `" + tableName + "` (POSITION, HOEHE, GESCHWINDIGKEIT, BREITE, GRENZWERT) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(sql, SqlData)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error('db_connection.insertTable(): ' + str(ex) + '/n' + traceback.format_exc())


def insert_comment(table_name, comment, position):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "INSERT INTO `comments` VALUES (%s, %s,%s)"
        cursor.execute(sql, (table_name, position, comment))
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        if ("Duplicate entry" in str(ex)):
            try:
                cnx = mysql_connection_pool.connection()
                cursor = cnx.cursor()
                sql = "UPDATE `comments` SET `comment`=%s WHERE `measurement`=%s AND `position`=%s"
                cursor.execute(sql, (glob.TABLENAME, position, comment))
                cnx.commit()
                cursor.close()
                cnx.close()
                return 'Comment updated'
            except Exception as ex:
                logging.error("db_connection.insertComment(): " + str(ex) +
                              "\n" + traceback.format_exc())

def insertMetadata():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "INSERT INTO `metadata` VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (glob.TABLENAME, glob.METADATA_LOCATION, glob.METADATA_DISTANCE, glob.METADATA_USER, glob.METADATA_MEASURE, glob.METADATA_NAME))
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.insertMetadata(): " + str(ex) + "\n" + traceback.format_exc())

def insertCommentBtn(comment):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "INSERT IGNORE INTO `commentBtns` VALUE (%s)"
        cursor.execute(sql, comment)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.insertCommentBtn(): " + str(ex) + "\n" + traceback.format_exc())


def get_table(table_name):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT * FROM `%s` ORDER BY 'POSITION'"
        cursor.execute(sql, table_name)
        result = list(cursor.fetchall())
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logging.error("db_connection.getTable(): " + str(ex) + "\n" + traceback.format_exc())
        return []


def getComments(tablename):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT `position`, `comment` FROM `comments` WHERE `measurement`= %s ORDER BY 'POSITION'"
        cursor.execute(sql, tablename)
        result = list(cursor.fetchall())
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logging.error("db_connection.getComments(): " + str(ex) + "\n" + traceback.format_exc())
        return []


def getMetadata(tablename):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT * FROM `metadata` where `measurement`= %s"
        cursor.execute(sql, tablename)
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logging.error("db_connection.getMetadata(): " + str(ex) + "\n" + traceback.format_exc())
        return []

def get_all_metadata():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT * FROM `metadata` ORDER BY `measurement`"
        cursor.execute(sql, )
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logging.error("db_connection.getAllTables(): " + str(ex) + "\n" + traceback.format_exc())
        return []

def getAllCommentBtns():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT * FROM `commentBtns`"
        cursor.execute(sql, )
        result = list(cursor.fetchall())
        cursor.close()
        cnx.close()
        coms = []
        for com in result:
            coms.append(com[0])
        return coms
    except Exception as ex:
        logging.error("db_connection.getAllCommentBtns(): " + str(ex) + "\n" + traceback.format_exc())
        return []

def dropCommentBtn(comment):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "DELETE FROM commentBtns WHERE comment LIKE %s"
        cursor.execute(sql, comment)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.dropCommentBtn(): " + str(ex) + "\n" + traceback.format_exc())

def dropTable(tablename):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "DROP TABLE `%s`"
        cursor.execute(sql, int(tablename))
        sql = "DELETE FROM metadata WHERE measurement LIKE %s"
        cursor.execute(sql, tablename)
        sql = "DELETE FROM comments WHERE measurement LIKE %s"
        cursor.execute(sql, tablename)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.dropTable(): " + str(ex) + "\n" + traceback.format_exc())

