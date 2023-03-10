from configparser import ConfigParser

import socketio
import app.globals as glob
import app.db_connection as db_con
import app.arduino_connection as ard_con

SIO = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
APP = socketio.ASGIApp(SIO)
BACKGROUND_TASK_STARTED = False
ard_con.init_connection()

config = ConfigParser()
config.read('app/preferences.ini')

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
            'MEASUREMENT_VALUE': glob.MEASUREMENT_VALUE,
            'LIMIT_VALUE': glob.LIMIT_VALUE,
            'CALI_ACTIVE': glob.CALIBRATION_ACTIVE,
            'CALI_DIST_MES_ACTIVE': glob.CALIBRATION_DISTANCE_MEASURING_ACTIVE,
            'MEASUREMENT_DISTANCE': glob.MEASUREMENT_DISTANCE
        })
        if glob.MEASUREMENT_ACTIVE:
            await SIO.emit('value', glob.VIEW_VALUES)
            glob.VIEW_VALUES = []


#################
# Chart Actions #
#################
@SIO.on('chart:start:measuring')
def chart_start_measuring(sid, data):
    glob.VIEW_VALUES = []
    glob.LONGTERM_VALUES = []
    glob.METADATA_TIMESTAMP = str(data['timestamp'])
    ard_con.reset_arduino()
    ard_con.start_arduino()
    glob.MEASUREMENT_ACTIVE = True
    glob.PAUSE_ACTIVE = False
    return 'ok'


@SIO.on('chart:stop:measuring')
def chart_stop_measuring(sid):
    try:
        ard_con.stop_arduino()
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
    ard_con.stop_arduino()
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
        if glob.MEASUREMENT_ACTIVE:
            db_con.insert_comment(glob.METADATA_TIMESTAMP, data['comment'], glob.MEASUREMENT_DISTANCE)
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
        glob.STREET_WIDTH = metaData['streedwidth']
        return 'ok'
    except Exception as ex:
        print(ex)
        return 'error', ex


@SIO.on('chart:get:limitvalue')
def chart_get_limitvalue(sid):
    try:
        return glob.LIMIT_VALUE
    except Exception as ex:
        print(ex)
        return 'error', ex

@SIO.on('chart:set:limitvalue')
def chart_set_limitvalue(sid, data):
    try:
        glob.LIMIT_VALUE = data
        return 'ok'
    except Exception as ex:
        return 'error', ex


################
# Data Actions #
################
@SIO.on('data:get:measurement')
def data_get_measurement(sid, data: {}):
    """ returns a specific table with all measurement values for instance on opening a measurement on the data page """
    try:
        if isinstance(data['tableName'], str):
            return db_con.get_table(data['tableName'], data['withComments'])
        else:
            return 'bad argument'
    except Exception as ex:
        return 'error', ex


@SIO.on('data:get:allTables')
def data_get_all_tables(sid):
    """ return all available tables from the database for instance on init of data page """
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


@SIO.on('data:set:metadata')
def data_set_metadata(sid, data: {}):
    try:
        db_con.update_metadata(data['tableName'], data['metaData']['name'], data['metaData']['user'], data['metaData']['location'], data['metaData']['notes'])
        return 'ok'
    except Exception as ex:
        return 'error', ex

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

@SIO.on('settings:start:calibration')
def settings_start_calibration(sid, password: str):
    try:
        if password == config['calibration']['password']:
            glob.CALIBRATION_ACTIVE = True
            glob.CALIBRATION_DISTANCE_MEASURING_ACTIVE = False
            return config['calibration']['steps']
        else:
            return 'wrong password'
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:stop:calibration')
def settings_stop_calibration(sid):
    try:
        glob.CALIBRATION_ACTIVE = False
        glob.CALIBRATION_DISTANCE_MEASURING_ACTIVE = False
        return 'ok'
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:set:calibrationStep')
def settings_set_calibration_step(sid, data: {}):
    try:
        if data['password'] == config['calibration']['password']:
            ard_con.set_calibration_value(data['step'])
            glob.CALIBRATION_ACTIVE = True
        else:
            return 'wrong password'
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:start:calibration:measurement')
def settings_start_calibration_distance_measurement(sid, password):
    try:
        if password == config['calibration']['password']:
            ard_con.start_calibration_distance_measuring()
            glob.CALIBRATION_DISTANCE_MEASURING_ACTIVE = True
    except Exception as ex:
        return 'error', ex


@SIO.on('settings:stop:calibration:measurement')
def settings_stop_calibration_distance_measurement(sid, password):
    try:
        if password == config['calibration']['password']:
            ard_con.stop_calibration_distance_measuring()
            glob.CALIBRATION_DISTANCE_MEASURING_ACTIVE = False
    except Exception as ex:
        return 'error', ex