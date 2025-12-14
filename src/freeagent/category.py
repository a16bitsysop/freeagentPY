from .base import FreeAgentBase


class CategoryAPI(FreeAgentBase):
    def __init__(self, parent):
        self.parent = parent  # the main FreeAgent instance
        super().__init__()
        self.categories = {}

    def _prep_categories(self):
        if not self.categories:
            self.categories = self.parent.get_api("categories")

    def get_desc_id(self, description):
        self._prep_categories()
        for _, cats in self.categories.items():
            for cat in cats:
                if description.lower() in cat.get("description", "").lower():
                    return cat["url"]
        return None

    def get_nominal_id(self, nominal_code):
        self._prep_categories()
        for _, cats in self.categories.items():
            for cat in cats:
                if str(nominal_code) == cat.get("nominal_code", ""):
                    return cat["url"]
        return None
