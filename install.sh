#!/usr/bin/env bash
# USBIP GUI Installation Script
# Installs USBIP GUI as a systemd service for automatic startup without sudo

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Please run: sudo ./install.sh"
   exit 1
fi

echo -e "${GREEN}=== USBIP GUI Service Installer ===${NC}"
echo

# Configuration
SERVICE_NAME="usbipgui"
SERVICE_USER="usbipgui"
SERVICE_GROUP="usbipgui"
INSTALL_DIR="/opt/usbipgui"
PYTHON_VENV="${INSTALL_DIR}/venv"
APP_DIR="${INSTALL_DIR}/src"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Service name: $SERVICE_NAME"
echo "  Service user: $SERVICE_USER"
echo "  Install directory: $INSTALL_DIR"
echo

# Step 1: Check dependencies
echo -e "${YELLOW}Step 1: Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  ✓ Python $PYTHON_VERSION found"

# Check linux-tools
if ! command -v usbip &> /dev/null; then
    echo -e "${YELLOW}Warning: usbip tools not found. Installing linux-tools-generic...${NC}"
    apt-get update
    apt-get install -y linux-tools-generic
fi
echo "  ✓ USBIP tools found"

echo

# Step 2: Create service user and group
echo -e "${YELLOW}Step 2: Setting up service user and group...${NC}"

if id "$SERVICE_USER" &>/dev/null; then
    echo "  ✓ User '$SERVICE_USER' already exists"
else
    echo "  Creating user '$SERVICE_USER'..."
    useradd -r -s /bin/false -d /var/lib/$SERVICE_USER -m $SERVICE_USER
    echo "  ✓ User created"
fi

if grep -q "^${SERVICE_GROUP}:" /etc/group; then
    echo "  ✓ Group '$SERVICE_GROUP' already exists"
else
    echo "  Creating group '$SERVICE_GROUP'..."
    groupadd -r $SERVICE_GROUP
    echo "  ✓ Group created"
fi

# Add user to group
usermod -a -G $SERVICE_GROUP $SERVICE_USER 2>/dev/null || true
echo "  ✓ User added to group"

echo

# Step 3: Install application
echo -e "${YELLOW}Step 3: Installing application files...${NC}"

if [[ -d "$INSTALL_DIR" ]]; then
    echo "  Cleaning existing installation..."
    rm -rf "$INSTALL_DIR"
fi

echo "  Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "  Copying application files..."
cp -r src requirements.txt run.sh "$INSTALL_DIR/"

echo "  ✓ Application files installed"

echo

# Step 4: Set up Python virtual environment
echo -e "${YELLOW}Step 4: Setting up Python virtual environment...${NC}"

echo "  Creating virtual environment..."
python3 -m venv "$PYTHON_VENV"

echo "  Installing Python dependencies..."
# Use absolute path to the venv python
"${PYTHON_VENV}/bin/pip" install --upgrade pip setuptools wheel > /dev/null
"${PYTHON_VENV}/bin/pip" install -r "$INSTALL_DIR/requirements.txt" > /dev/null

echo "  ✓ Virtual environment set up"

echo

# Step 5: Set permissions
echo -e "${YELLOW}Step 5: Setting up permissions...${NC}"

# Set ownership
chown -R $SERVICE_USER:$SERVICE_GROUP "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chmod 755 "$APP_DIR"

# Make sure venv is accessible
chmod -R 755 "$PYTHON_VENV/bin"

# Create state directory
STATE_DIR="/var/lib/$SERVICE_USER"
mkdir -p "$STATE_DIR"
chown -R $SERVICE_USER:$SERVICE_GROUP "$STATE_DIR"
chmod 750 "$STATE_DIR"

# Create log directory
LOG_DIR="/var/log/$SERVICE_NAME"
mkdir -p "$LOG_DIR"
chown -R $SERVICE_USER:$SERVICE_GROUP "$LOG_DIR"
chmod 750 "$LOG_DIR"

echo "  ✓ Permissions set"

echo

# Step 6: Configure sudoers for USBIP commands
echo -e "${YELLOW}Step 6: Configuring sudoers for USBIP commands...${NC}"

SUDOERS_FILE="/etc/sudoers.d/90-$SERVICE_NAME"

if [[ -f "$SUDOERS_FILE" ]]; then
    echo "  ✓ Sudoers file already exists"
else
    cat > "$SUDOERS_FILE" << 'SUDOERS_EOF'
# Allow usbipgui service user to run USBIP commands without password
Defaults:usbipgui !authenticate, !requiretty, !use_pty
usbipgui ALL=(ALL) NOPASSWD: /usr/bin/usbip
usbipgui ALL=(ALL) NOPASSWD: /usr/bin/usbipd
usbipgui ALL=(ALL) NOPASSWD: /usr/lib/linux-tools/*/usbip
usbipgui ALL=(ALL) NOPASSWD: /usr/lib/linux-tools/*/usbipd
usbipgui ALL=(ALL) NOPASSWD: /sbin/modprobe
usbipgui ALL=(ALL) NOPASSWD: /bin/lsmod
usbipgui ALL=(ALL) NOPASSWD: /usr/bin/pgrep
usbipgui ALL=(ALL) NOPASSWD: /usr/bin/pkill
SUDOERS_EOF
    chmod 440 "$SUDOERS_FILE"
    # Verify sudoers syntax
    if visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1; then
        echo "  ✓ Sudoers file created and verified"
    else
        echo -e "${RED}Error: Invalid sudoers configuration${NC}"
        rm "$SUDOERS_FILE"
        exit 1
    fi
fi

echo

# Step 7: Create and install systemd service
echo -e "${YELLOW}Step 7: Creating systemd service...${NC}"

SYSTEMD_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > "$SYSTEMD_FILE" << SYSTEMD_EOF
[Unit]
Description=USBIP GUI - Web Interface for USB over IP
Documentation=file://$INSTALL_DIR/README.md
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
ExecStart=${PYTHON_VENV}/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info
Restart=on-failure
RestartSec=10

# Environment
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONDONTWRITEBYTECODE=1"

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

chmod 644 "$SYSTEMD_FILE"
echo "  ✓ Systemd service file created"

echo

# Step 8: Reload systemd and enable service
echo -e "${YELLOW}Step 8: Enabling systemd service...${NC}"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"
echo "  ✓ Service enabled for autostart"

echo

# Step 9: Summary and next steps
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo
echo -e "${GREEN}Summary:${NC}"
echo "  - Application installed to: $INSTALL_DIR"
echo "  - Service user created: $SERVICE_USER"
echo "  - Systemd service: $SERVICE_NAME.service"
echo "  - Log file: $LOG_DIR/${SERVICE_NAME}.log"
echo
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Start the service:"
echo "     ${YELLOW}sudo systemctl start $SERVICE_NAME${NC}"
echo
echo "  2. Check service status:"
echo "     ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
echo
echo "  3. View logs:"
echo "     ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo
echo "  4. Access the web interface:"
echo "     ${YELLOW}http://localhost:8080${NC}"
echo
echo -e "${YELLOW}To uninstall:${NC}"
echo "  ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
echo "  ${YELLOW}sudo systemctl disable $SERVICE_NAME${NC}"
echo "  ${YELLOW}sudo rm $SYSTEMD_FILE${NC}"
echo "  ${YELLOW}sudo systemctl daemon-reload${NC}"
echo "  ${YELLOW}sudo userdel $SERVICE_USER${NC}"
echo "  ${YELLOW}sudo rm -rf $INSTALL_DIR${NC}"
echo
