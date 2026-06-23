#!/usr/bin/env python3
# ============================================================
# 📄 REPORT GENERATOR - PDF/HTML Backtest Reports
# ============================================================
#
# Generates professional backtest reports with:
# - Performance summary
# - Equity curve visualization
# - Trade analysis
# - Risk metrics
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# For HTML reports
from jinja2 import Template

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Report Generator
    
    Generates professional backtest reports:
    - Executive Summary
    - Performance Metrics
    - Equity Curve Charts
    - Trade Analysis
    - Risk Metrics
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.name = "Report Generator"
        self.version = "1.0.0"
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"📄 {self.name} v{self.version} initialized")
        logger.info(f"   Output Directory: {output_dir}")
    
    def generate_report(
        self,
        backtest_results: Dict,
        symbol: str = "GBPUSD",
        timeframe: str = "H1"
    ) -> Dict:
        """
        Generate complete backtest report
        
        Args:
            backtest_results: Results from HistoricalRunner
            symbol: Trading symbol
            timeframe: Timeframe
            
        Returns:
            Report metadata
        """
        logger.info(f"📄 Generating report for {symbol} {timeframe}")
        
        # Extract data
        trades = backtest_results.get('trades', [])
        equity_curve = backtest_results.get('equity_curve', [])
        performance = backtest_results.get('performance', {})
        
        # Generate charts
        charts = self._generate_charts(equity_curve, trades)
        
        # Generate HTML
        html_content = self._generate_html(
            symbol=symbol,
            timeframe=timeframe,
            performance=performance,
            trades=trades,
            charts=charts
        )
        
        # Save HTML
        filename = f"report_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✅ Report saved: {filepath}")
        
        return {
            'filepath': filepath,
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_charts(
        self,
        equity_curve: List[float],
        trades: List[Dict]
    ) -> Dict:
        """
        Generate chart images
        
        Args:
            equity_curve: Equity curve data
            trades: List of trades
            
        Returns:
            Dict of chart filenames
        """
        charts = {}
        
        # 1. Equity Curve
        equity_chart = self._plot_equity_curve(equity_curve)
        charts['equity_curve'] = equity_chart
        
        # 2. Drawdown
        drawdown_chart = self._plot_drawdown(equity_curve)
        charts['drawdown'] = drawdown_chart
        
        # 3. Trade Distribution
        if trades:
            trade_chart = self._plot_trade_distribution(trades)
            charts['trade_distribution'] = trade_chart
        
        # 4. Monthly Returns
        monthly_chart = self._plot_monthly_returns(equity_curve)
        charts['monthly_returns'] = monthly_chart
        
        return charts
    
    def _plot_equity_curve(self, equity_curve: List[float]) -> str:
        """
        Plot equity curve
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Chart filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(equity_curve, color='#00ff88', linewidth=2)
        ax.fill_between(range(len(equity_curve)), equity_curve, color='#00ff88', alpha=0.2)
        
        ax.set_title('Equity Curve', color='white', fontsize=14)
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Equity ($)', color='white')
        ax.grid(True, alpha=0.1)
        
        ax.set_facecolor('#0a0e1a')
        fig.patch.set_facecolor('#0a0e1a')
        
        # Style axes
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#2a3a60')
        
        # Save
        filename = f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_drawdown(self, equity_curve: List[float]) -> str:
        """
        Plot drawdown
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Chart filename
        """
        if len(equity_curve) < 2:
            return None
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (running_max - equity) / running_max * 100
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.fill_between(range(len(drawdown)), 0, drawdown, color='#ff4444', alpha=0.5)
        ax.plot(drawdown, color='#ff4444', linewidth=1)
        
        ax.set_title('Drawdown', color='white', fontsize=14)
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Drawdown (%)', color='white')
        ax.grid(True, alpha=0.1)
        
        ax.set_facecolor('#0a0e1a')
        fig.patch.set_facecolor('#0a0e1a')
        
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#2a3a60')
        
        filename = f"drawdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_trade_distribution(self, trades: List[Dict]) -> str:
        """
        Plot trade distribution
        
        Args:
            trades: List of trades
            
        Returns:
            Chart filename
        """
        if not trades:
            return None
        
        pnls = [t.get('pnl', 0) for t in trades]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogram
        ax.hist(pnls, bins=20, color='#00ccff', alpha=0.7, edgecolor='white')
        ax.axvline(0, color='white', linestyle='--', alpha=0.5)
        
        # Statistics
        avg_pnl = np.mean(pnls)
        ax.axvline(avg_pnl, color='#00ff88', linestyle='-', linewidth=2, label=f'Avg: ${avg_pnl:.2f}')
        
        ax.set_title('Trade P&L Distribution', color='white', fontsize=14)
        ax.set_xlabel('P&L ($)', color='white')
        ax.set_ylabel('Frequency', color='white')
        ax.legend()
        ax.grid(True, alpha=0.1)
        
        ax.set_facecolor('#0a0e1a')
        fig.patch.set_facecolor('#0a0e1a')
        
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#2a3a60')
        
        filename = f"trade_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_monthly_returns(self, equity_curve: List[float]) -> str:
        """
        Plot monthly returns
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Chart filename
        """
        if len(equity_curve) < 21:
            return None
        
        monthly_returns = []
        for i in range(0, len(equity_curve), 21):
            if i + 21 < len(equity_curve):
                ret = (equity_curve[i+21] - equity_curve[i]) / equity_curve[i] * 100
                monthly_returns.append(ret)
        
        if not monthly_returns:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        colors = ['#00ff88' if r >= 0 else '#ff4444' for r in monthly_returns]
        ax.bar(range(len(monthly_returns)), monthly_returns, color=colors, alpha=0.7)
        
        ax.axhline(0, color='white', linestyle='-', alpha=0.5)
        
        ax.set_title('Monthly Returns (%)', color='white', fontsize=14)
        ax.set_xlabel('Month', color='white')
        ax.set_ylabel('Return (%)', color='white')
        ax.grid(True, alpha=0.1)
        
        ax.set_facecolor('#0a0e1a')
        fig.patch.set_facecolor('#0a0e1a')
        
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#2a3a60')
        
        filename = f"monthly_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _generate_html(
        self,
        symbol: str,
        timeframe: str,
        performance: Dict,
        trades: List[Dict],
        charts: Dict
    ) -> str:
        """
        Generate HTML report
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            performance: Performance metrics
            trades: List of trades
            charts: Chart filenames
            
        Returns:
            HTML content
        """
        template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MARDUK-TRADING-RIG™ - Backtest Report</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    background: #0a0e1a;
                    font-family: 'Courier New', monospace;
                    padding: 2rem;
                    color: #ffffff;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .header {
                    background: #0f1322;
                    padding: 2rem;
                    border-radius: 1rem;
                    border: 2px solid #ffcc00;
                    margin-bottom: 2rem;
                    text-align: center;
                }
                .header h1 {
                    color: #ffcc00;
                    font-size: 2rem;
                }
                .header .subtitle {
                    color: #8da0c0;
                    margin-top: 0.5rem;
                }
                .grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }
                .card {
                    background: #0f1322;
                    padding: 1.5rem;
                    border-radius: 1rem;
                    border: 1px solid #2a3a60;
                }
                .card h2 {
                    color: #ffcc00;
                    font-size: 1.2rem;
                    margin-bottom: 1rem;
                    border-bottom: 1px solid #2a3a60;
                    padding-bottom: 0.5rem;
                }
                .metric {
                    display: flex;
                    justify-content: space-between;
                    padding: 0.5rem 0;
                    border-bottom: 1px solid #1a2a4a;
                }
                .metric .label {
                    color: #8da0c0;
                }
                .metric .value {
                    color: #88ffaa;
                    font-weight: bold;
                }
                .metric .value.green { color: #88ff88; }
                .metric .value.red { color: #ff6666; }
                .metric .value.gold { color: #ffcc00; }
                .chart {
                    width: 100%;
                    margin: 1rem 0;
                }
                .chart img {
                    width: 100%;
                    border-radius: 0.5rem;
                    border: 1px solid #2a3a60;
                }
                .footer {
                    text-align: center;
                    padding: 1rem;
                    color: #8da0c0;
                    font-size: 0.8rem;
                    border-top: 1px solid #1a2a4a;
                    margin-top: 2rem;
                }
                .footer .copy {
                    color: #ffcc00;
                }
                @media (max-width: 700px) {
                    .grid { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <h1>🚀 MARDUK-TRADING-RIG™</h1>
                    <div class="subtitle">Backtest Report · {{ symbol }} {{ timeframe }}</div>
                    <div style="color: #8da0c0; font-size: 0.8rem; margin-top: 0.5rem;">
                        Generated: {{ timestamp }}
                    </div>
                </div>

                <!-- Performance Summary -->
                <div class="grid">
                    <div class="card">
                        <h2>📊 Performance Summary</h2>
                        <div class="metric">
                            <span class="label">Total Trades</span>
                            <span class="value">{{ performance.total_trades }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Win Rate</span>
                            <span class="value">{{ performance.win_rate }}%</span>
                        </div>
                        <div class="metric">
                            <span class="label">Net Profit</span>
                            <span class="value gold">${{ "%.2f"|format(performance.net_profit) }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Profit Factor</span>
                            <span class="value">{{ performance.profit_factor }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Sharpe Ratio</span>
                            <span class="value">{{ performance.sharpe_ratio }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Max Drawdown</span>
                            <span class="value red">{{ performance.max_drawdown }}%</span>
                        </div>
                    </div>

                    <div class="card">
                        <h2>💰 Trade Statistics</h2>
                        <div class="metric">
                            <span class="label">Wins / Losses</span>
                            <span class="value">{{ performance.wins }} / {{ performance.losses }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Average Win</span>
                            <span class="value green">${{ "%.2f"|format(performance.avg_win) }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Average Loss</span>
                            <span class="value red">${{ "%.2f"|format(performance.avg_loss) }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Best Trade</span>
                            <span class="value green">${{ "%.2f"|format(performance.best_trade) }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Worst Trade</span>
                            <span class="value red">${{ "%.2f"|format(performance.worst_trade) }}</span>
                        </div>
                        <div class="metric">
                            <span class="label">Avg Trade</span>
                            <span class="value">{{ "%.2f"|format(performance.avg_trade) }}</span>
                        </div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="grid">
                    <div class="card">
                        <h2>📈 Equity Curve</h2>
                        <div class="chart">
                            <img src="{{ charts.equity_curve }}" alt="Equity Curve">
                        </div>
                    </div>
                    <div class="card">
                        <h2>📉 Drawdown</h2>
                        <div class="chart">
                            <img src="{{ charts.drawdown }}" alt="Drawdown">
                        </div>
                    </div>
                    {% if charts.trade_distribution %}
                    <div class="card">
                        <h2>📊 Trade Distribution</h2>
                        <div class="chart">
                            <img src="{{ charts.trade_distribution }}" alt="Trade Distribution">
                        </div>
                    </div>
                    {% endif %}
                    {% if charts.monthly_returns %}
                    <div class="card">
                        <h2>📊 Monthly Returns</h2>
                        <div class="chart">
                            <img src="{{ charts.monthly_returns }}" alt="Monthly Returns">
                        </div>
                    </div>
                    {% endif %}
                </div>

                <!-- Footer -->
                <div class="footer">
                    <span class="copy">© 2026 Seliim Ahmed. All Rights Reserved.</span><br>
                    <span>MARDUK-TRADING-RIG™ · Part of the Marduk System™</span>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Prepare template data
        data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'performance': performance,
            'trades': trades[:10],  # Only show last 10
            'charts': charts
        }
        
        # Render template
        template_obj = Template(template)
        html_content = template_obj.render(**data)
        
        return html_content


# ============================================================
# 🚀 USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    # Test the Report Generator
    generator = ReportGenerator()
    
    # Sample data
    sample_trades = []
    np.random.seed(42)
    for i in range(50):
        pnl = np.random.normal(50, 100)
        sample_trades.append({'pnl': pnl, 'return': pnl/10000})
    
    sample_performance = {
        'total_trades': 50,
        'wins': 32,
        'losses': 18,
        'breakeven': 0,
        'win_rate': 64.0,
        'net_profit': 1500.00,
        'profit_factor': 1.8,
        'avg_win': 120.00,
        'avg_loss': -80.00,
        'avg_trade': 30.00,
        'best_trade': 450.00,
        'worst_trade': -200.00,
        'sharpe_ratio': 1.5,
        'max_drawdown': 12.5
    }
    
    sample_equity = [10000]
    for i in range(100):
        change = np.random.normal(0, 0.005)
        sample_equity.append(sample_equity[-1] * (1 + change))
    
    # Generate report
    result = generator.generate_report(
        backtest_results={
            'trades': sample_trades,
            'equity_curve': sample_equity,
            'performance': sample_performance
        },
        symbol='GBPUSD',
        timeframe='H1'
    )
    
    print(f"\n✅ Report generated: {result['filepath']}")
