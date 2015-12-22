import os
os.environ['REDASH_REDIS_URL'] = "redis://localhost:6379/5"
# Use different url for Celery to avoid DB being cleaned up:
os.environ['REDASH_CELERY_BROKER'] = "redis://localhost:6379/6"


import logging
from unittest import TestCase
import datetime
from redash import settings
from factories import Factory

settings.DATABASE_CONFIG = {
    'name': 'circle_test',
    'threadlocals': True
}

from redash import redis_connection
import redash.models

logging.getLogger('peewee').setLevel(logging.INFO)


class BaseTestCase(TestCase):
    def setUp(self):
        redash.models.create_db(True, True)
        self.factory = Factory()

    def tearDown(self):
        redash.models.db.close_db(None)
        redash.models.create_db(False, True)
        redis_connection.flushdb()

    def assertResponseEqual(self, expected, actual):
        for k, v in expected.iteritems():
            if isinstance(v, datetime.datetime) or isinstance(actual[k], datetime.datetime):
                continue

            if isinstance(v, list):
                continue

            if isinstance(v, dict):
                self.assertResponseEqual(v, actual[k])
                continue

            self.assertEqual(v, actual[k], "{} not equal (expected: {}, actual: {}).".format(k, v, actual[k]))
