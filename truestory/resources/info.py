"""API exposing miscellaneous information."""


import operator

from truestory.models import PreferencesModel, RssTargetModel
from truestory.resources import base


# Lazily inited.
prefs = None


class BaseInfoResource(base.BaseResource):

    """Base class for all info related resources."""

    URL_PREFIX = "/info"


class SitesInfoResource(BaseInfoResource):

    """Whitelisted news sites."""

    ENDPOINT = "sites"

    @staticmethod
    def _get_prefs():
        global prefs
        if not prefs:
            prefs = PreferencesModel.instance()
        return prefs

    def get(self):
        """Returns a list of accepted trusted sources (news websites)."""
        site_list = []
        prefs = self._get_prefs()
        for site, details in prefs.sites.items():
            site_item = details.copy()
            del site_item["side"]
            rss_targets = RssTargetModel.all(
                RssTargetModel.query(
                    ("enabled", "=", True),
                    ("site", "=", site),
                )
            )
            site_item["enabled"] = bool(rss_targets)
            site_list.append(site_item)

        site_list.sort(key=operator.itemgetter("agree"), reverse=True)
        for site_item in site_list:
            del site_item["agree"]

        return {"sites": site_list}
