"""nsebot — a lean NSE trading engine built on free data.

Two modes share one risk and execution core:
  swing     CNC delivery, daily bars, decided after the close
  intraday  MIS, 5-minute bars, squared off before 15:15 IST

Market data is free (Yahoo Finance via yfinance). This customized checkout
permits paper execution only. Live broker transport and login are disabled;
credentials cannot enable them.
"""

__version__ = '3.0.0'
