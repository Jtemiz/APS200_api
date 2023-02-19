import datetime
import os
import traceback

import socketio
import app.globals as glob
import app.db_connection as db_con
import app.arduino_connection as ard_con

SIO = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
APP = socketio.ASGIApp(SIO)
BACKGROUND_TASK_STARTED = False


@SIO.event
def connect(sid, environ, data):
    global BACKGROUND_TASK_STARTED
    if not BACKGROUND_TASK_STARTED:
        SIO.start_background_task(background_task)
        BACKGROUND_TASK_STARTED = True


async def background_task():
    while True:
        await SIO.sleep(0.2)
        await SIO.emit('status', {
            'MEASUREMENT_ACTIVE': glob.MEASUREMENT_ACTIVE,
            'PAUSE_ACTIVE': glob.PAUSE_ACTIVE,
            'BATTERY_LEVEL': glob.BATTERY_LEVEL,
            'MEASUREMENT_DISTANCE': glob.MEASUREMENT_DISTANCE,
            'MEASUREMENT_VALUE': glob.MEASUREMENT_VALUE
        })


#################
# Chart Actions #
#################
@SIO.on('chart:start:measuring')
def chart_start_measuring(sid, data):
    glob.METADATA_TIMESTAMP = str(data['timestamp'])

    print(glob.METADATA_TIMESTAMP)
   # ard_con.reset_arduino()
   # ard_con.start_arduino()
    glob.MEASUREMENT_ACTIVE = True
    glob.PAUSE_ACTIVE = False
    return 'ok'


@SIO.on('chart:stop:measuring')
def chart_stop_measuring(sid):
    try:
        #ard_con.stop_arduino()
        db_con.create_table(glob.METADATA_TIMESTAMP)
        db_con.insert_table(glob.METADATA_TIMESTAMP)
        db_con.insert_metadata(glob.METADATA_TIMESTAMP)
        glob.VIEW_VALUES = []
        glob.LONGTERM_VALUES = []
        glob.MEASUREMENT_DISTANCE = 0.0
        glob.MEASUREMENT_ACTIVE = False
        glob.PAUSE_ACTIVE = False
        return 'ok'
    except Exception as ex:
        print(ex)
        return 'error', ex


@SIO.on('chart:start:pause')
def chart_start_pause(sid):
    #ard_con.stop_arduino()
    db_con.create_table(glob.METADATA_TIMESTAMP)
    db_con.insert_table(glob.METADATA_TIMESTAMP)
    glob.VIEW_VALUES = []
    glob.LONGTERM_VALUES = []
    glob.PAUSE_ACTIVE = True
    return 'ok'


@SIO.on('chart:stop:pause')
def chart_stop_pause(sid):
    ard_con.start_arduino()
    glob.PAUSE_ACTIVE = False
    return 'ok'


@SIO.on('chart:add:comment')
def chart_add_comment(sid, data: dict):
    try:
        if glob.MEASUREMENT_ACTIVE and glob.RUNNING_MEASUREMENT is not None:
            db_con.insert_comment(glob.RUNNING_MEASUREMENT, data['comment'], glob.MEASUREMENT_DISTANCE)
            return 'ok'
        else:
            return 'Keine Aktive Messung'
    except Exception as ex:
        return 'error', ex


@SIO.on('chart:set:metadata')
def chart_set_metaData(sid, data: dict):
    try:
        metaData = data['metaData']
        glob.METADATA_NAME = metaData['name']
        glob.METADATA_USER = metaData['user']
        glob.METADATA_LOCATION = metaData['location']
        glob.METADATA_NOTES = metaData['notes']
        return 'ok'
    except Exception as ex:
        print(ex)
        return 'error', ex


################
# Data Actions #
################
""" :returns a specific table with all measurement values for instance on opening a measurement on the data page """
@SIO.on('data:get:measurement')
def data_get_measurement(sid, table_name: str):
    try:
        if isinstance(table_name, str):
            return db_con.get_table(table_name)
        else:
            return 'bad argument'
    except Exception as ex:
        return 'error', ex


""" :return all available tables from the database for instance on init of data page """
@SIO.on('data:get:allTables')
def data_get_all_tables(sid):
    try:
        result = []
        for i, table in enumerate(db_con.get_all_metadata()):
            result.append({'id': i+1, 'location': table[1], 'distance': table[2], 'user': table[3], 'name': table[4], 'notes': table[5], 'date': table[0]})
        return result
    except Exception as ex:
        return 'error', ex


@SIO.on('data:delete:table')
def data_delete_table(sid, table_name: str):
    try:
        db_con.drop_table(table_name)
        return 'ok'
    except Exception as ex:
        return 'error', ex


# todo: create csv

####################
# SETTINGS Actions #
####################

@SIO.on('settings:get:commentBtns')
def settings_get_all_comment_btns(sid):
    try:
        return db_con.getAllCommentBtns()
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:add:commentBtn')
def settings_add_comment_btn(sid, comment_btn: str):
    try:
        db_con.insertCommentBtn(comment_btn)
        return 'ok'
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:delete:commentBtn')
def settings_delete_comment_btn(sid, comment_btn: str):
    try:
        db_con.dropCommentBtn(comment_btn)
        return 'ok'
    except Exception as ex:
        return 'error', ex
