#!/usr/bin/env python3

import requests
from requests.adapters import HTTPAdapter
from st2reactor.sensor.base import PollingSensor

__all_ = ["DcstoreAppSensor"]


BASE_URL = "http://dcstore.shenmo.tech/store"


class DcstoreAppSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(DcstoreAppSensor, self).__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._logger = self.sensor_service.get_logger(__name__)
        self._trigger_ref = "dcs.matched_app"

    def setup(self):
        """
        配置, 只会被执行一次
        """
        self._s = requests.Session()
        self._s.mount("http://", HTTPAdapter(max_retries=3))
        self._s.mount("http://", HTTPAdapter(max_retries=3))
        self._s.get(BASE_URL, timeout=5)
        self._last_version = None
        self._app_json = "{}/{}/{}/app.json".format(
            BASE_URL, self._config["category"], self._config["pkgname"]
        )

    def poll(self):
        """
        PollingSensor 程序执行的核心
        """
        app_r = self._s.get(self._app_json)
        app_json = app_r.json()
        self._logger.info("DcstoreAppSensor get app_json is %s", app_json)
        app_version = app_json.get("Version")
        last_version = self._get_last_version()
        self._logger.info("DcstoreAppSensor app_version is %s last_version is %s",
                          app_version, last_version)
        if last_version != app_version:
            self._set_last_version(last_version)
            self._dispatch_trigger_for_app(app_json)

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
        if not self._last_version and hasattr(self.sensor_service, "get_value"):
            self._last_version = self.sensor_service.get_value(name="last_version")
        return self._last_version

    def _set_last_version(self, last_version):
        self._last_version = last_version
        if hasattr(self.sensor_service, "set_value"):
            self.sensor_service.set_value(name="last_version", value=last_version)

    def _dispatch_trigger_for_app(self, app):
        trigger = self._trigger_ref
        payload = {
            "Name": app["Name"],
            "Version": app["Version"],
            "Filename": app["Filename"],
            "Pkgname": app["Pkgname"],
            "Author": app["Author"],
            "Contributor": app["Contributor"],
            "Website": app["Website"],
            "Update": app["Update"],
            "Size": app["Size"],
            "More": app["More"],
        }
        # 核心
        self.sensor_service.dispatch(trigger=trigger, payload=payload)
