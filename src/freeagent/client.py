from .categories import FreeAgentCategories
from .bank import FreeAgentBank


class FreeAgent(FreeAgentCategories, FreeAgentBank):
    def __init__(self):
        super().__init__()
