
class Item:
    """

    """

    def __init__(self, data, missing=False):
        """
        Args:
            data:
            missing:
        """
        self.appid = data.get('appid')
        self.classid = data.get('classid')
        self.instanceid = data.get('instanceid')
        self.assetid = data.get('assetid')
        self.icon_url = data.get('icon_url')
        self.icon_url_large = data.get('icon_url_large')
        self.pos = data.get('pos')
        self.amount = data.get('amount')
        self.id = data.get('id')
        self.app_data = data.get('app_data')
        self.tags = data.get('tags', [])
        self.icon_drag_url = data.get('icon_drag_url')
        self.name = data.get('name')
        self.actions = data.get('actions')
        self.market_marketable_restriction = data.get('market_marketable_restriction')
        self.descriptions = data.get('descriptions', [])
        self.market_hash_name = data.get('market_hash_name')
        self.market_name = data.get('market_name')
        self.tradable = bool(data.get('tradable')) if data.get('tradable') != None else None
        self.marketable = bool(data.get('marketable')) if data.get('marketable') != None else None
        self.market_tradable_restriction = data.get('market_tradable_restriction')
        self.name_color = data.get('name_color')
        self.background_color = data.get('background_color')
        self.type = data.get('type')
        self.commodity = data.get('commodity')
        self.missing = missing

    @property
    def small_image(self):
        """

        Returns:

        """
        if not self.icon_url:
            return None
        return "https://steamcommunity-a.akamaihd.net/economy/image/" + self.icon_url

    @property
    def large_image(self):
        """

        Returns:

        """
        if not self.icon_url_large:
            return None
        return "https://steamcommunity-a.akamaihd.net/economy/image/" + self.icon_url_large
