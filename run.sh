#!/bin/bash
# ============================================================
# 🚀 RUN.SH - MARDUK-TRADING-RIG™ LAUNCHER
# ============================================================
#
# © 2026 Seliim Ahmed. All Rights Reserved.
#
# ============================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================
# BANNER
# ============================================================

clear
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}           🚀 MARDUK-TRADING-RIG™${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}           Part of the Marduk System™${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================
# CHECK IF SETUP IS COMPLETE
# ============================================================

if [ ! -f "config/settings.json" ]; then
    echo -e "${RED}❌ config/settings.json not found!${NC}"
    echo -e "${YELLOW}Please run ./setup.sh first${NC}"
    exit 1
fi

# ============================================================
# MENU
# ============================================================

echo -e "${CYAN}📋 Select mode:${NC}"
echo ""
echo -e "${GREEN}[1] ${NC}📊 Dashboard Mode"
echo -e "${GREEN}[2] ${NC}📈 Live Trading Mode"
echo -e "${GREEN}[3] ${NC}🔬 Backtest Mode"
echo -e "${GREEN}[4] ${NC}📊 Analysis Mode"
echo -e "${GREEN}[5] ${NC}⚙️  Configure"
echo -e "${GREEN}[6] ${NC}🚪 Exit"
echo ""

read -p "Choose (1-6): " CHOICE

case $CHOICE in
    1)
        echo -e "${CYAN}📊 Starting dashboard...${NC}"
        python3 main.py --mode dashboard
        ;;
    2)
        echo -e "${CYAN}📈 Starting live trading...${NC}"
        read -p "Symbol (default: GBPUSD): " SYMBOL
        SYMBOL=${SYMBOL:-GBPUSD}
        read -p "Timeframe (default: M1): " TIMEFRAME
        TIMEFRAME=${TIMEFRAME:-M1}
        python3 main.py --mode live --symbol "$SYMBOL" --timeframe "$TIMEFRAME"
        ;;
    3)
        echo -e "${CYAN}🔬 Starting backtest...${NC}"
        read -p "Symbol (default: GBPUSD): " SYMBOL
        SYMBOL=${SYMBOL:-GBPUSD}
        read -p "Timeframe (default: H1): " TIMEFRAME
        TIMEFRAME=${TIMEFRAME:-H1}
        python3 main.py --mode backtest --symbol "$SYMBOL" --timeframe "$TIMEFRAME"
        ;;
    4)
        echo -e "${CYAN}📊 Starting analysis...${NC}"
        read -p "Symbol (default: GBPUSD): " SYMBOL
        SYMBOL=${SYMBOL:-GBPUSD}
        python3 main.py --mode analyze --symbol "$SYMBOL"
        ;;
    5)
        echo -e "${CYAN}⚙️  Configuring...${NC}"
        nano config/settings.json
        echo -e "${GREEN}✅ Configuration updated${NC}"
        sleep 2
        exec ./run.sh
        ;;
    6)
        echo -e "${GREEN}Bye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        sleep 2
        exec ./run.sh
        ;;
esac
