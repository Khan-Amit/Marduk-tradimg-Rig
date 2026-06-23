#!/usr/bin/env python3
# ============================================================
# 🚀 MARDUK-TRADING-RIG™ - MAIN ENTRY POINT
# ============================================================
#
# 3-6-9 + Fibonacci + Macro = Infinite Probability Trading Engine
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

import sys
import time
import logging
import argparse
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# ============================================================
# 📝 LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/marduk_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================
# 🎨 BANNER
# ============================================================

def print_banner():
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                                              ║
{Fore.YELLOW}║  🚀 MARDUK-TRADING-RIG™                                                     ║
{Fore.YELLOW}║  Part of the Marduk System™                                                 ║
{Fore.CYAN}║                                                                              ║
{Fore.GREEN}║  3-6-9 + Fibonacci + Macro = Infinite Probability Trading Engine              ║
{Fore.CYAN}║                                                                              ║
{Fore.MAGENTA}║  © 2026 Seliim Ahmed. All Rights Reserved.                                  ║
{Fore.CYAN}║  Unauthorized use is strictly prohibited and will be prosecuted.              ║
{Fore.CYAN}║                                                                              ║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

# ============================================================
# 🧠 CORE ENGINE IMPORT
# ============================================================

def import_core_modules():
    """Import core modules with error handling"""
    try:
        from core.quantum_engine import QuantumEngine
        from core.macro_engine import MacroEngine
        from core.probability_engine import ProbabilityEngine
        from core.cashflow_engine import CashFlowEngine
        return True
    except ImportError as e:
        logger.error(f"Failed to import core modules: {e}")
        return False

# ============================================================
# 🚀 MAIN EXECUTION
# ============================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MARDUK-TRADING-RIG™ - 3-6-9 + Fibonacci + Macro Trading Engine'
    )
    
    parser.add_argument(
        '--mode',
        choices=['live', 'backtest', 'analyze', 'dashboard'],
        default='analyze',
        help='Run mode: live trading, backtesting, analysis, or dashboard'
    )
    
    parser.add_argument(
        '--symbol',
        default='GBPUSD',
        help='Trading symbol (default: GBPUSD)'
    )
    
    parser.add_argument(
        '--timeframe',
        default='M1',
        help='Timeframe (default: M1)'
    )
    
    parser.add_argument(
        '--config',
        default='config/settings.json',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check core modules
    if not import_core_modules():
        logger.error("❌ Core modules not found. Please ensure all files are in place.")
        sys.exit(1)
    
    logger.info(f"🚀 Starting MARDUK-TRADING-RIG™ in {args.mode} mode")
    logger.info(f"📊 Symbol: {args.symbol} | Timeframe: {args.timeframe}")
    logger.info(f"📄 Config: {args.config}")
    logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.mode == 'live':
            from live_trading.metatrader_bridge import MetaTraderBridge
            bridge = MetaTraderBridge()
            bridge.run()
            
        elif args.mode == 'backtest':
            from backtesting.historical_runner import HistoricalRunner
            runner = HistoricalRunner()
            runner.run()
            
        elif args.mode == 'dashboard':
            from dashboard.app import run_dashboard
            run_dashboard()
            
        else:
            # Analyze mode
            from core.quantum_engine import QuantumEngine
            engine = QuantumEngine()
            result = engine.analyze_market()
            print(f"\n{Fore.GREEN}📊 Analysis Result:{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}3-6-9 Confluence:{Style.RESET_ALL} {result.get('confluence', 'N/A')}")
            print(f"  {Fore.YELLOW}Fibonacci Probability:{Style.RESET_ALL} {result.get('fib_prob', 'N/A')}%")
            print(f"  {Fore.YELLOW}Macro Regime:{Style.RESET_ALL} {result.get('macro_regime', 'N/A')}")
            print(f"  {Fore.YELLOW}Signal:{Style.RESET_ALL} {result.get('signal', 'HOLD')}")
            print(f"  {Fore.YELLOW}Confidence:{Style.RESET_ALL} {result.get('confidence', 0)}%")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Shutdown requested. Exiting gracefully...")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    
    logger.info("✅ MARDUK-TRADING-RIG™ shutdown complete")
    logger.info("© 2026 Seliim Ahmed. All Rights Reserved.")

# ============================================================
# 🚀 ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
