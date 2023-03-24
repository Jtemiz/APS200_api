import datetime

MEASUREMENT_ACTIVE = False
PAUSE_ACTIVE = False
CALIBRATION_ACTIVE = False
CALIBRATION_DISTANCE_MEASURING_ACTIVE = False

BATTERY_LEVEL = 0
MEASUREMENT_DISTANCE = 0.0
MEASUREMENT_VALUE = 0

WATCH_DOG = False

RUNNING_MEASUREMENT = None
STREET_WIDTH = 0
LIMIT_VALUE = 4
VIEW_VALUES = []
LONGTERM_VALUES = []

METADATA_TIMESTAMP = datetime.datetime.now().timestamp()
METADATA_NAME = ''
METADATA_USER = ''
METADATA_LOCATION = ''
METADATA_NOTES = ''
