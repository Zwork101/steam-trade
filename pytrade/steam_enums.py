from enum import Enum

class ETradeOfferState(Enum):
    """
    """
    Invalid = 1
    Active = 2
    Accepted = 3
    Countered = 4
    Expired = 5
    Canceled = 6
    Declined = 7
    InvalidItems = 8
    NeedsConfirmation = 9
    CanceledBySecondFactor = 10
    Escrow = 11

class SteamUrls(Enum):
    """
    """
    Community = "https://steamcommunity.com"
    Api = "https://api.steampowered.com"
    Store = "https://store.steampowered.com"
