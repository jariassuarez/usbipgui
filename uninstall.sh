#!/usr/bin/env bash
# USBIP GUI Uninstallation Script
# Removes the USBIP GUI systemd service and application files

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Please run: sudo ./uninstall.sh"
   exit 1
fi

echo -e "${GREEN}=== USBIP GUI Service Uninstaller ===${NC}"
echo

# Configuration
SERVICE_NAME="usbipgui"
SERVICE_USER="usbipgui"
SERVICE_GROUP="usbipgui"
INSTALL_DIR="/opt/usbipgui"

read -p "Are you sure you want to uninstall USBIP GUI? (yes/no) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo

# Step 1: Stop and disable service
echo -e "${YELLOW}Step 1: Stopping and disabling service...${NC}"

if systemctl is-active --quiet "$SERVICE_NAME.service"; then
    echo "  Stopping service..."
    systemctl stop "$SERVICE_NAME.service"
    echo "  ✓ Service stopped"
fi

if systemctl is-enabled "$SERVICE_NAME.service" &> /dev/null; then
    echo "  Disabling service..."
    systemctl disable "$SERVICE_NAME.service"
    echo "  ✓ Service disabled"
fi

echo

# Step 2: Remove systemd service file
echo -e "${YELLOW}Step 2: Removing systemd service...${NC}"

if [[ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]]; then
    rm "/etc/systemd/system/${SERVICE_NAME}.service"
    systemctl daemon-reload
    echo "  ✓ Systemd service file removed"
fi

echo

# Step 3: Remove sudoers file
echo -e "${YELLOW}Step 3: Removing sudoers configuration...${NC}"

SUDOERS_FILE="/etc/sudoers.d/90-${SERVICE_NAME}"
if [[ -f "$SUDOERS_FILE" ]]; then
    rm "$SUDOERS_FILE"
    echo "  ✓ Sudoers file removed"
fi

echo

# Step 4: Remove application directory
echo -e "${YELLOW}Step 4: Removing application files...${NC}"

if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    echo "  ✓ Application directory removed"
fi

echo

# Step 5: Remove service user
echo -e "${YELLOW}Step 5: Removing service user and group...${NC}"

if id "$SERVICE_USER" &>/dev/null; then
    echo "  Removing user '$SERVICE_USER'..."
    userdel -r "$SERVICE_USER" 2>/dev/null || true
    echo "  ✓ User removed"
fi

echo

# Step 6: Clean up log directory
echo -e "${YELLOW}Step 6: Cleaning up log directory...${NC}"

LOG_DIR="/var/log/${SERVICE_NAME}"
if [[ -d "$LOG_DIR" ]]; then
    rm -rf "$LOG_DIR"
    echo "  ✓ Log directory removed"
fi

echo

# Step 7: Summary
echo -e "${GREEN}=== Uninstallation Complete ===${NC}"
echo
echo "USBIP GUI service has been successfully uninstalled."
echo
