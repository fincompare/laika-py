import threading
import time

from requests import request
from urllib.parse import urlparse

from .model import *


class Endpoints(object):
    @staticmethod
    def method():
        return "GET"

    @staticmethod
    def health():
        return "/api/health"

    @staticmethod
    def status(feature, env):
        return f"/api/features/{feature}/status/{env}"

    @staticmethod
    def features(feature=None):
        return f"/api/features{'' if feature is None else f'/{feature}'}"

    @staticmethod
    def environments():
        return "/api/environments"

    class Events(object):
        @staticmethod
        def method():
            return "POST"

        class Environment(object):
            @staticmethod
            def method():
                return Endpoints.Events.method()

            @staticmethod
            def create():
                return "/api/events/environment_created"

            @staticmethod
            def delete():
                return "/api/events/environment_deleted"

            @staticmethod
            def order():
                return "/api/events/environments_ordered"

        class Feature(object):
            @staticmethod
            def method():
                return Endpoints.Events.method()

            @staticmethod
            def create():
                return "/api/events/feature_created"

            @staticmethod
            def delete():
                return "/api/events/feature_deleted"

            @staticmethod
            def toggle():
                return "/api/events/feature_toggled"

        class User(object):
            @staticmethod
            def method():
                return Endpoints.Events.method()

            @staticmethod
            def create():
                return "/api/events/user_created"


class Client(object):
    class State(object):

        environments = list()
        features = list()
        last_update = 0.0

    def __init__(self, url, username, password, environment, interval=15.0):
        """
        initialize client
        """
        self.url = url
        self.username = username
        self.password = password
        self.interval = interval
        self.environment = environment
        self.state = self.State()
        try:
            parsed = urlparse(url)
            if parsed.username:
                username = parsed.username
            if parsed.password:
                password = parsed.password
        except:
            pass
        self.auth = (username, password)
        self.timer = None
        return

    def url_for(self, callback, *args, **kwargs):
        """
        generate url for/using given callback.
        """
        return f"{self.url}{callback(*args, **kwargs)}"

    def init_timer(self, interval, *args, **kwargs):
        """
        sets up timer to do polling
        """
        self.timer = threading.Timer(
            interval=interval,
            function=self.init_timer,
            args=(interval, *args),
            kwargs=kwargs,
        )
        self.timer.start()
        self.poll()
        return self.timer

    @staticmethod
    def error_wrapper(response):
        return RuntimeWarning(
            response,
            response.ok,
            response.status_code,
            response.reason,
            response.text,
        )

    def stop(self):
        if self.timer:
            self.timer.cancel()
        return self

    def poll(self):
        """
        polls remote and de-serializes data into self.state
        """
        envs = request(
            method=Endpoints.method(),
            url=self.url_for(Endpoints.environments),
            auth=self.auth,
        )
        features = request(
            method=Endpoints.method(),
            url=self.url_for(Endpoints.features, None),
            auth=self.auth,
        )
        if envs.ok:
            self.state.environments = [Environment(**obj) for obj in envs.json()]
        else:
            raise self.error_wrapper(envs)
        if features.ok:
            self.state.features = [Feature(**obj) for obj in features.json()]
        else:
            raise self.error_wrapper(features)
        self.state.last_update = time.time()
        return self.state

    def get_features(self, named: str):
        return [feat for feat in self.state.features if named == feat.name]

    def set_state(
        self, feature: str, state: bool, env: str = "", local_only: bool = False
    ):
        """
        sets state of the feature on the `env`

        @feature: name of the feature
        @state: desired state (True or False)
        @env: environment, empty defaults to current one
        @local_only: only update local cache
        """
        if not env:
            env = self.environment
        if not local_only:
            self.feature_toggle(feature, env, state)
        features = self.get_features(named=feature)
        for feat in features:
            feat.status[env] = state
        return

    def get_state(
        self, feature: str, env: str = "", on_demand: bool = False
    ) -> Optional[Feature]:
        """
        helper function to return state of the feature.

        @feature: name of the feature
        @env: name of the environment
        @on_demand: skip cache, query directly (slow but consistent)
        """
        return (
            self.get_ondemand(feature, env)
            if on_demand
            else self.get_cached(feature, env)
        )

    def get_cached(self, feature: str, env: str = "") -> bool:
        """
        get status of `feature` on `env`
        """
        if not env:
            env = self.environment
        features = self.get_features(named=feature)
        states = [feat.status.get(env, False) for feat in features]
        return states and all(states)

    def get_ondemand(self, feature: str, env: str = "") -> Optional[Feature]:
        """
        query remote for most up-to-date state of feature
        """
        if not env:
            env = self.environment
        response = request(
            method=Endpoints.method(),
            url=self.url_for(Endpoints.features, feature),
            auth=self.auth,
        )
        if response.ok:
            result = response.json()
            feature = Feature(**result)
            return feature.status.get(env, False)
        else:
            raise self.error_wrapper(response)

    def generator(self, feature: str, env: str = "", on_demand: bool = True):
        """
        generator (helper) to get feature status.
        """
        while True:
            yield self.get_state(feature, env, on_demand)
            continue

    def env_create(self, name: str):
        return request(
            method=Endpoints.Events.Environment.method(),
            url=self.url_for(Endpoints.Events.Environment.create),
            auth=self.auth,
            json=dict(
                name=name,
            ),
        ).json()

    def env_delete(self, name: str):
        return request(
            method=Endpoints.Events.Environment.method(),
            url=self.url_for(Endpoints.Events.Environment.delete),
            auth=self.auth,
            json=dict(
                name=name,
            ),
        ).json()

    def env_order(self, envs: list):
        raise NotImplementedError("nope")

    def feature_create(self, name: str):
        return request(
            method=Endpoints.Events.Feature.method(),
            url=self.url_for(Endpoints.Events.Feature.create),
            auth=self.auth,
            json=dict(
                name=name,
            ),
        ).json()

    def feature_delete(self, name: str):
        return request(
            method=Endpoints.Events.Feature.method(),
            url=self.url_for(Endpoints.Events.Feature.delete),
            auth=self.auth,
            json=dict(
                name=name,
            ),
        ).json()

    def feature_toggle(self, feature: str, env: str = "", state=None):
        if not env:
            env = self.environment
        if state is None:
            state = not self.get_state(feature, env)
        return request(
            method=Endpoints.Events.Feature.method(),
            url=self.url_for(Endpoints.Events.Feature.toggle),
            auth=self.auth,
            json=dict(
                feature=feature,
                environment=env,
                status=state,
            ),
        ).json()

    def user_create(self, username: str, password: str):
        return request(
            method=Endpoints.Events.User.method(),
            url=self.url_for(Endpoints.Events.User.create),
            auth=self.auth,
            json=dict(
                username=username,
                password=password,
            ),
        ).json()
