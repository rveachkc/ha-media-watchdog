import os
from typing import Self, Union
from urllib.parse import urlparse

import homeassistant_api
import yaml
from prometheus_client import Counter, Gauge
from requests.exceptions import ConnectionError
from rv_script_lib import ScriptBase

from ha_watchdog_libs.watchdog_rules import WatchdogRule


class ApiTokenMissing(Exception):
    None


class HaMediaWatchdog(ScriptBase):
    ACTION_WARN = "warn"
    ACTION_STOP = "stop"
    ACTION_HOME = "home"

    PARSER_INCLUDE_REPEAT_OPTIONS = True
    PARSER_VERBOSITY_CONFIG = "count"
    PROM_METRIC_PREFIX = "watchdog"

    def extraArgs(self: Self):
        self.parser.add_argument("config", type=str, help="config file")

    def extraMetrics(self: Self):
        self.prom_action_count = Counter(
            f"{self.PROM_METRIC_PREFIX}_action",
            "Count of actions taken",
            ["action", "entity", "source", "api_host"],
            registry=self.prom_registry,
        )

        self.prom_rules_loaded = Gauge(
            f"{self.PROM_METRIC_PREFIX}_rules_loaded",
            "Number of rules loaded for processing",
            ["api_url", "api_host"],
            registry=self.prom_registry,
        )

    @staticmethod
    def getPlayerRuleAction(
        entity_id: str, source_name: str, rule: WatchdogRule
    ) -> Union[str, None]:
        if rule.rule_applies(entity_id=entity_id, source_name=source_name):
            return rule.action

        return None

    def checkPlayer(self: Self, player: homeassistant_api.models.entity.Entity):
        player_friendly_name = player.state.attributes.get("friendly_name")
        player_entity_id = player.state.entity_id
        player_source_name = player.state.attributes.get("source")

        self.log.debug("Player obj", player=player.model_dump())

        self.log.debug(
            "Player Log",
            state=player.state.state,
            entity_id=player_entity_id,
            source=player_source_name,
            device_class=player.state.attributes.get("device_class"),
            friendly_name=player_friendly_name,
            entity_picture=player.state.attributes.get("entity_picture"),
        )

        # this checks the rule to see if we need to perform action.
        # returns an iterator of a 2 part tuple:
        # (rule_name: str, rule_applies: bool)
        rule_checks = map(
            lambda x: (
                x.name,
                self.getPlayerRuleAction(
                    entity_id=player_entity_id,
                    source_name=player_source_name,
                    rule=x,
                ),
            ),
            self.rules,
        )

        # filters out rules that do not apply
        rule_checks = filter(
            lambda x: bool(x[1]),
            rule_checks,
        )

        # converts to a list for repeat access
        rule_checks = list(rule_checks)

        # create a set of the actions to take
        rule_actions = set(map(lambda x: x[1], rule_checks))

        # groups affected rule names by the actions we will take.
        # honestly, this is mostly used for logging.
        rule_action_dict = {
            x: list(
                map(
                    lambda z: z[0],
                    filter(
                        lambda y: y[1] == x,
                        rule_checks,
                    ),
                ),
            )
            for x in rule_actions
        }

        if self.ACTION_WARN in rule_actions:
            self.prom_action_count.labels(
                self.ACTION_WARN,
                player_entity_id,
                player_source_name,
                urlparse(self.client.api_url).netloc,
            ).inc()
            self.log.warning(
                "Media Watchdog Detection",
                action=self.ACTION_WARN,
                player=player_friendly_name,
                entity_id=player_entity_id,
                source=player_source_name,
                rules=rule_action_dict.get(self.ACTION_WARN),
            )

        if self.ACTION_HOME in rule_actions:
            self.prom_action_count.labels(
                self.ACTION_HOME,
                player_entity_id,
                player_source_name,
                urlparse(self.client.api_url).netloc,
            ).inc()
            self.log.warning(
                "Media Watchdog Detection",
                action=self.ACTION_HOME,
                player=player_friendly_name,
                entity_id=player_entity_id,
                source=player_source_name,
                rules=rule_action_dict.get(self.ACTION_HOME),
            )

            self.media_player_services.select_source(
                entity_id=player_entity_id, source="Home"
            )

    @staticmethod
    def read_config_from_file(config_path: str):
        with open(config_path, "r") as config_fd:
            config_data = yaml.safe_load(config_fd)

        api_url = config_data.get("api_url")
        rules = [WatchdogRule(**x) for x in config_data.get("rules", [])]

        return api_url, rules

    def runJob(self: Self):
        api_url, self.rules = self.read_config_from_file(self.args.config)

        self.token = os.getenv("HOMEASSISTANT_TOKEN")
        if self.token is None:
            raise ApiTokenMissing(
                "The HOMEASSISTANT_TOKEN environment variable must be set"
            )

        self.client = homeassistant_api.Client(
            api_url,
            self.token,
        )

        self.log.debug("HomeAssistant Client Configured", api_url=self.client.api_url)
        self.prom_rules_loaded.labels(
            self.client.api_url, urlparse(self.client.api_url).netloc
        ).set(len(self.rules))

        try:
            self.media_player_services = self.client.get_domain("media_player")
        except ConnectionError:
            self.log.warning("Unable to connect to Home Assistant")
            return None

        entities = self.client.get_entities()

        mp = entities.get("media_player")

        if not mp.entities:
            self.log.warning("Zero Entities returned. Is Home Assistant Down?")
            return None

        for mpn, mpi in mp.entities.items():
            self.log.debug("found entity", name=mpn)

            self.checkPlayer(mpi)
