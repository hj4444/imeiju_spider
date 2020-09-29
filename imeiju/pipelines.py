import datetime
import logging
import traceback

import pymysql
from pymysql import OperationalError
from twisted.enterprise import adbapi
from twisted.internet import defer

from imeiju.items import TVItem

logger = logging.getLogger(__name__)


class MysqlAsyncPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.starttime = None

    @classmethod
    def from_settings(cls, settings):
        db_params = dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset=settings["MYSQL_CHARSET"],
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **db_params)
        return cls(dbpool)

    def open_spider(self, spider):
        self.start_time = datetime.datetime.now()

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        try:
            yield self.dbpool.runInteraction(self.do_insert, item)
        except OperationalError:
            if self.report_connection_error:
                logger.error("Can't connect to MqlSQL")
                self.report_connection_error = False

        except:
            print(traceback.format_exc())
        # d.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        defer.returnValue(item)

    @staticmethod
    def do_insert(tx, item):
        if isinstance(item, TVItem):
            sql = "insert into tv values ('{0}','{1}','{2}','{3}','{4}')".format(item['id'],
                                                                                 pymysql.escape_string(item['name']),
                                                                                 pymysql.escape_string(item['desc']),
                                                                                 pymysql.escape_string(item['season']),
                                                                                 pymysql.escape_string(
                                                                                     item['episode_num']))
            tx.execute(sql)
            for video in item['episode']:
                sql = """insert into episode(tv_id,num,video_url)  values (%s,"%s","%s")""" % (
                    video['tv_id'],
                    pymysql.escape_string(video['num']),
                    pymysql.escape_string(video['video_url']))
                tx.execute(sql)

    def _handle_error(self, failure):
        logging.ERROR(failure)

    def close_spider(self, spider):
        self.dbpool.close()
        finish_time = datetime.datetime.now()
        print(self.__class__.__name__, self.start_time, finish_time)
