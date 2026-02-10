#!/bin/bash
# EcoStream AI Forecasting Service Startup Script
# Automatically checks Python, activates virtual environment, installs dependencies, and starts the service

set -e  # Exit on error

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting EcoStream AI Forecasting Service...${NC}"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Python 3.9+ from https://www.python.org/downloads/${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}Found: ${PYTHON_VERSION}${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to service directory
SERVICE_DIR="${SCRIPT_DIR}/services/ai-forecasting-python"
if [ ! -d "$SERVICE_DIR" ]; then
    echo -e "${RED}Error: Service directory not found at ${SERVICE_DIR}${NC}"
    exit 1
fi

cd "$SERVICE_DIR"

# Check for virtual environment
VENV_PATH="${SERVICE_DIR}/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment (cross-platform)
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [ -f "${VENV_PATH}/Scripts/activate" ]; then
    # Windows (Git Bash)
    source "${VENV_PATH}/Scripts/activate"
elif [ -f "${VENV_PATH}/bin/activate" ]; then
    # Linux/Mac
    source "${VENV_PATH}/bin/activate"
else
    echo -e "${RED}Error: Could not find virtual environment activation script${NC}"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    exit 1
fi

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

# Try to upgrade pip (non-blocking - continue even if it fails)
echo -e "${GRAY}Upgrading pip (if needed)...${NC}"
pip install --upgrade pip > /dev/null 2>&1 || echo -e "${YELLOW}Warning: Could not upgrade pip (this is usually okay)${NC}"

# Install project dependencies (this is critical)
echo -e "${YELLOW}Installing project dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies from requirements.txt${NC}"
    exit 1
fi
echo -e "${GREEN}Dependencies installed successfully!${NC}"

# Start the service
echo -e "${GREEN}Starting AI Forecasting Service on port 5000...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the service${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload