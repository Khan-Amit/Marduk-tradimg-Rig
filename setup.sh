#!/bin/bash
# ============================================================
# 🚀 SETUP.SH - MARDUK-TRADING-RIG™ INSTALLATION
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
echo -e "${PURPLE}           🚀 MARDUK-TRADING-RIG™ SETUP${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}           Part of the Marduk System™${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================
# CHECK PREREQUISITES
# ============================================================

echo -e "${CYAN}📋 Checking prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} installed${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✅ pip installed${NC}"
else
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Check git
if command -v git &> /dev/null; then
    echo -e "${GREEN}✅ git installed${NC}"
else
    echo -e "${RED}❌ git not found. Please install git${NC}"
    exit 1
fi

echo ""

# ============================================================
# INSTALL DEPENDENCIES
# ============================================================

echo -e "${CYAN}📦 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# ============================================================
# CONFIGURE SETTINGS
# ============================================================

echo -e "${CYAN}⚙️  Configuring settings...${NC}"

if [ ! -f "config/settings.json" ]; then
    cp config/settings.example.json config/settings.json
    echo -e "${GREEN}✅ Created config/settings.json${NC}"
    echo -e "${YELLOW}⚠️  Please edit config/settings.json with your preferences${NC}"
else
    echo -e "${GREEN}✅ config/settings.json already exists${NC}"
fi

echo ""

# ============================================================
# CREATE DIRECTORIES
# ============================================================

echo -e "${CYAN}📁 Creating directories...${NC}"

mkdir -p logs
mkdir -p data
mkdir -p reports
mkdir -p backtesting/results

echo -e "${GREEN}✅ Directories created${NC}"

echo ""

# ============================================================
# SET PERMISSIONS
# ============================================================

echo -e "${CYAN}🔒 Setting permissions...${NC}"

chmod +x main.py
chmod +x setup.sh

echo -e "${GREEN}✅ Permissions set${NC}"

echo ""

# ============================================================
# COMPLETION
# ============================================================

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ MARDUK-TRADING-RIG™ INSTALLATION COMPLETE!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}📋 Next steps:${NC}"
echo -e "  1. Edit config/settings.json with your preferences"
echo -e "  2. Run: ${GREEN}python main.py --mode dashboard${NC}"
echo -e "  3. Open browser: ${GREEN}http://localhost:8080${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}© 2026 Seliim Ahmed. All Rights Reserved.${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
