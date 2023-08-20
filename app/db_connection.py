import logging
import traceback

import pymysql
from dbutils.persistent_db import PersistentDB
import app.globals as glob
from configparser import ConfigParser
import logging

logger = logging.getLogger()

config = ConfigParser()
config.read('app/preferences.ini')

db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database'],
    'connect_timeout': int(config['mysql']['connect_timeout'])
}

mysql_connection_pool = PersistentDB(
    creator=pymysql,
    **db_config
)


def create_table(tableName):
    cnx = mysql_connection_pool.connection()
    cursor = cnx.cursor()
    sql = "CREATE TABLE IF NOT EXISTS`" + tableName + "` LIKE `ExampleTable`;"
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()


def insert_table(tableName):
    SqlData = list([(i['position'], i['height'], i['speed'], i['strWidth'], i['limVal']) for i in glob.LONGTERM_VALUES])
    cnx = mysql_connection_pool.connection()
    cursor = cnx.cursor()
    sql = "INSERT INTO `" + tableName + "` (POSITION, HOEHE, GESCHWINDIGKEIT, BREITE, GRENZWERT) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, SqlData)
    cnx.commit()
    cursor.close()
    cnx.close()
    logger.info('table in database inserted')


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
                cursor.execute(sql, (comment, table_name, position))
                cnx.commit()
                cursor.close()
                cnx.close()
                return 'Comment updated'
            except Exception as ex:
                logger.error("db_connection.insertComment(): " + str(ex) +
                              "\n" + traceback.format_exc())


def insert_metadata(timestamp):
    cnx = mysql_connection_pool.connection()
    cursor = cnx.cursor()
    sql = "INSERT INTO `metadata` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (timestamp, glob.METADATA_LOCATION, glob.MEASUREMENT_DISTANCE, glob.METADATA_USER,
                         glob.METADATA_NAME, glob.METADATA_NOTES))
    cnx.commit()
    cursor.close()
    cnx.close()


def update_metadata(timestamp, measurement_name, username, location, notes):
    cnx = mysql_connection_pool.connection()
    cursor = cnx.cursor()
    sql = "UPDATE `metadata` SET `location`=%s, `username`=%s, `measurementname`=%s, `notes`=%s WHERE `measurement`=%s"
    cursor.execute(sql, (location, username, measurement_name, notes, timestamp))
    cnx.commit()
    cursor.close()
    cnx.close()


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
        logger.error("db_connection.insertCommentBtn(): " + str(ex) + "\n" + traceback.format_exc())


def get_table(table_name, with_comments):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        if with_comments:
            sql = "SELECT vals.POSITION, vals.HOEHE, vals.GESCHWINDIGKEIT, vals.BREITE, vals.GRENZWERT, coms.comment " \
                  "FROM `%s` AS vals LEFT JOIN " \
                  "(SELECT `position`, `comment` FROM `comments` WHERE `measurement`=%s) " \
                  "AS coms ON coms.position = vals.POSITION " \
                  "ORDER BY vals.POSITION"
            cursor.execute(sql, (int(table_name), table_name))
        else:
            sql = "SELECT * FROM `%s` ORDER BY 'POSITION'"
            cursor.execute(sql, int(table_name))
        result = list(cursor.fetchall())
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logger.error("db_connection.getTable(): " + str(ex) + "\n" + traceback.format_exc())
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
        logger.error("db_connection.getComments(): " + str(ex) + "\n" + traceback.format_exc())
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
        logger.error("db_connection.getMetadata(): " + str(ex) + "\n" + traceback.format_exc())
        return []


def get_all_metadata():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT `measurement`, `location`, `distance`, `username`, `measurementname`, `notes` FROM `metadata` ORDER BY `measurement`"
        cursor.execute(sql, )
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        print(result)
        return result
    except Exception as ex:
        logger.error("db_connection.getAllTables(): " + str(ex) + "\n" + traceback.format_exc())
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
        logger.error("db_connection.getAllCommentBtns(): " + str(ex) + "\n" + traceback.format_exc())
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
        logger.error("db_connection.dropCommentBtn(): " + str(ex) + "\n" + traceback.format_exc())


def drop_table(tablename):
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
