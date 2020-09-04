#!/usr/bin/env python3

import requests
from requests.adapters import HTTPAdapter

from st2reactor.sensor.base import PollingSensor

__all_ = [
    'DcstoreAppSensor'
]


BASE_URL = 'http://dcstore.shenmo.tech/store'


class DcstoreAppSensor(PollingSensor):

   def setup(self) :
       """
       配置, 只会被执行一次
       """
       self._s = requests.Session()
       self._s.mount('http://', HTTPAdapter(max_retries=3))
       self._s.mount('http://', HTTPAdapter(max_retries=3))
       self._s.get(BASE_URL, timeout=5)
       self._last_version = None
       self._app_json = "{}/{}/{}/app.json".format(BASE_URL, self._config['category'], self._config['pkgname'])

   def poll(self):
       """
       PollingSensor 程序执行的核心
       """
       pass

   def cleanup(self):
       """
       st2系统停止时会执行
       """
       pass

   def add_trigger(self, trigger):
       pass

   def update_trigger(self, trigger):
       pass

   def remove_trigger(self, trigger):
       pass

   def _get_last_version(self):
       if not self._last_version and hasattr(self._sensor_service, 'get_value'):
           self._last_version = self._sensor_service.get_value(name='last_version')
        return self._last_version
