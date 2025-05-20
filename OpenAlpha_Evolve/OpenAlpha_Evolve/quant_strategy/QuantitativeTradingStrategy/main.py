# region imports
from AlgorithmImports import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Data import *
from QuantConnect.Indicators import *
from QuantConnect.Orders import *
# endregion

class QuantitativeTradingStrategy(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)  # Set Start Date
        self.set_end_date(2025, 1, 1)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash
        self.set_brokerage_model(BrokerageName.Default)
        
        # Add assets
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.qqq = self.add_equity("QQQ", Resolution.DAILY).symbol
        
        # Set benchmark
        self.set_benchmark("SPY")
        
        # Initialize indicators
        self.fast_ema = self.ema(self.spy, 20, Resolution.DAILY)
        self.slow_ema = self.ema(self.spy, 50, Resolution.DAILY)
        
        # Schedule rebalancing
        self.schedule.on(self.date_rules.month_start(),
                        self.time_rules.after_market_open(self.spy, 30),
                        self.rebalance)

    def rebalance(self):
        """Monthly rebalancing logic"""
        if self.fast_ema.current.value > self.slow_ema.current.value:
            if not self.portfolio[self.spy].invested:
                self.set_holdings(self.spy, 0.8)
                self.liquidate(self.qqq)
        else:
            if not self.portfolio[self.qqq].invested:
                self.set_holdings(self.qqq, 0.8)
                self.liquidate(self.spy)

    def on_data(self, data: Slice):
        """Log current portfolio value"""
        self.plot("Portfolio", "Value", self.portfolio.total_portfolio_value)
