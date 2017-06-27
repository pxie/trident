import logging as log

log.basicConfig(format='%(asctime)s %(levelname)-5s %(process)d:%(thread)d %(pathname)s:%(lineno)d %(message)s',
                level=log.DEBUG)


def getLogger():
    return log
