class BLClipsTransformOptions(object):
    """Unified structure for Clips transformation options"""
    def __init__(self, **kwargs):
        self._trades = set()
        self._mappings = {}
        self._defaults = False
        return super().__init__(**kwargs)

    @property
    def Trades(self):
        """Trades involved in CLIPS run"""
        return self._trades

    @Trades.setter
    def Trades(self, value):
        val = value
        if not isinstance(value, set):
            try:
                val = set(value)
            except:
                val = set()
        self._trades = val

    @Trades.deleter
    def Trades(self):
        del self._trades

    def AddTrade(self, trade):
        self._trades.add(trade)

    def AddTrades(self, trades):
        self._trades = self._trades.union(trades)

    @property
    def Defaults(self):
        """Indicates whether default values are important while clips fact creation"""
        return self._defaults

    @Defaults.setter
    def Defaults(self, value):
        self._defaults = value

    @Defaults.deleter
    def Defaults(self):
        del self._defaults

    @property
    def Mappings(self):
        """Trades involved in CLIPS run"""
        return self._mappings

    @Mappings.setter
    def Mappings(self, value):
        self._mappings = value

    @Mappings.deleter
    def Mappings(self):
        del self._mappings