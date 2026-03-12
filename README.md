# USBIP GUI

A modern web-based graphical interface for managing USBIP (USB over IP) on Linux systems. This project provides an intuitive dashboard for both USBIP server and client operations, eliminating the need for command-line interactions.

## Table of Contents

- [What is USBIP?](#what-is-usbip)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development](#development)
- [Documentation & Resources](#documentation--resources)

## What is USBIP?

**USBIP (USB over IP)** is a Linux kernel subsystem that allows you to use USB devices remotely over a network as if they were physically connected to your computer. It consists of two main components:

- **USBIP Server**: Exposes local USB devices over the network, allowing remote clients to access them
- **USBIP Client**: Connects to a remote USBIP server and attaches remote USB devices to your system

### Key Use Cases

- Share USB devices across a network (printers, scanners, security tokens, etc.)
- Access USB devices from virtual machines or containers
- Centralize USB device management in data centers
- Remote device testing and development

### How It Works

USBIP operates at the kernel level (Linux kernel modules):
1. `usbip_core` - Core USBIP functionality
2. `usbip_host` - Server-side module for sharing USB devices
3. `vhci_hcd` - Virtual Host Controller Interface for client-side attachment

USB communication is tunneled over TCP/IP, maintaining compatibility with standard USB protocols.

## Features

- **Web-Based Interface**: Modern, responsive dashboard accessible from any web browser
- **USBIP Server Management**:
  - View daemon status and host module information
  - List available USB devices with detailed information (vendor ID, product ID, names)
  - Enable/disable device sharing
  
- **USBIP Client Management**:
  - Connect to remote USBIP servers
  - Browse remote devices
  - Attach/detach remote USB devices
  - View attached ports and connection status
  - Monitor virtual host controller interface (vhci) status

- **Real-time Status Updates**: Dynamic status monitoring for server and client operations
- **Async Architecture**: FastAPI-based async runtime for responsive interactions
- **Security**: Support for privilege escalation via sudo with passwordless configuration

## Requirements

- **Operating System**: Linux (USBIP is Linux-specific)
- **Kernels**: Linux 4.7+ (USBIP support in mainline kernel)
- **USBIP Command-line Tools**: `usbip` package must be installed
  ```bash
  # Ubuntu/Debian
  sudo apt install usbip

  # Fedora/RHEL
  sudo dnf install usbip

  # Arch
  sudo pacman -S usbip
  ```
- **Python**: 3.10 or higher
- **Privileges**: Must run with root access or sudo privileges for USBIP operations

### Python Dependencies

- FastAPI >= 0.110.0
- Uvicorn[standard] >= 0.27.0
- Jinja2 >= 3.1.3
- python-multipart >= 0.0.9
- pydantic-settings >= 2.2.0

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/usbipgui.git
cd usbipgui
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify USBIP Installation

```bash
usbip --version
```

## Configuration

Configuration is handled via environment variables with the `USBIPGUI_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `USBIPGUI_HOST` | `0.0.0.0` | Web server bind address |
| `USBIPGUI_PORT` | `8000` | Web server port |
| `USBIPGUI_USBIP_PORT` | `3240` | USBIP daemon port |
| `USBIPGUI_USE_SUDO` | `true` | Use sudo for USBIP commands |
| `USBIPGUI_LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |

### Example: Custom Configuration

```bash
export USBIPGUI_HOST=127.0.0.1
export USBIPGUI_PORT=9000
export USBIPGUI_USE_SUDO=true
export USBIPGUI_LOG_LEVEL=debug
```

### Sudoers Configuration (Optional)

To run USBIP commands without password prompts, configure sudoers:

```bash
sudo visudo
```

Add the following lines (replace `username` with your user):

```
username ALL=(ALL) NOPASSWD: /usr/bin/usbip
username ALL=(ALL) NOPASSWD: /bin/lsmod
username ALL=(ALL) NOPASSWD: /usr/bin/pgrep
username ALL=(ALL) NOPASSWD: /usr/bin/pkill
```

## Usage

### Running the Application

#### Using the Provided Script

```bash
./run.sh
```

#### Using uvicorn Directly

```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Using Environmental Variables

```bash
USBIPGUI_HOST=127.0.0.1 USBIPGUI_PORT=8080 ./run.sh
```

### Accessing the Web Interface

Once running, open your web browser and navigate to:

```
http://localhost:8000
```

### Server Operations

1. Navigate to the **Server** tab
2. View the daemon status and connected devices
3. Monitor device sharing status

### Client Operations

1. Navigate to the **Client** tab
2. Enter the remote USBIP server details
3. Browse and attach remote USB devices
4. View attached ports and connection status

## Project Structure

```
usbipgui/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── run.sh                 # Startup script
└── src/
    ├── main.py           # FastAPI application entry point
    ├── config.py         # Configuration and settings
    ├── models/           # Pydantic data models
    │   ├── client.py     # Client models (RemoteDevice, AttachedPort)
    │   └── server.py     # Server models
    ├── parsers/          # Command output parsers
    │   ├── local_list.py    # Parse local USB device listings
    │   ├── port_list.py     # Parse attached port information
    │   └── remote_list.py   # Parse remote device listings
    ├── services/         # Business logic
    │   ├── executor.py         # Command executor with async support
    │   ├── client_service.py   # Client service logic
    │   └── server_service.py   # Server service logic
    ├── routers/          # API and page routes
    │   ├── pages.py      # Web page routes
    │   ├── client.py     # Client API endpoints
    │   └── server.py     # Server API endpoints
    ├── static/           # Static files (CSS, JS, images)
    └── templates/        # Jinja2 HTML templates
        ├── base.html
        ├── index.html
        ├── client/
        └── server/
```

## Development

### Project Architecture

- **Framework**: FastAPI (async web framework)
- **Templating**: Jinja2 (HTML rendering)
- **Models**: Pydantic (data validation)
- **Async Runtime**: asyncio + uvicorn

### Code Organization

- **Models** (`models/`): Data structures for USB devices, ports, and daemon status
- **Parsers** (`parsers/`): Parse output from USBIP command-line tools
- **Services** (`services/`): Core business logic for server/client operations
- **Routers** (`routers/`): HTTP endpoints and page handlers
- **Templates** (`templates/`): HTML rendering with Jinja2

### Command Execution

The `executor.py` module handles running USBIP commands with:
- Automatic sudo privilege escalation (configurable)
- Async subprocess execution
- Timeout handling
- Error capture and reporting

### Adding New Features

1. Define models in `models/`
2. Create parsers for command output in `parsers/`
3. Implement service logic in `services/`
4. Add API routes in `routers/`
5. Create HTML templates in `templates/`

## Documentation & Resources

### USBIP Documentation

- **Official Linux Kernel Documentation**: https://www.kernel.org/doc/html/latest/usb/usbip.html
- **USBIP GitHub Repository**: https://github.com/torvalds/linux/tree/master/tools/usb/usbip
- **Man Pages**:
  - `man usbip` - USBIP command reference
  - `man usbip-server` - Server-side operations
  - `man usbip-client` - Client-side operations

### Related Resources

- **Linux USB Project**: https://www.linux-usb.org/
- **Kernel Modules**: https://wiki.archlinux.org/title/USBIP
- **Network USB**: https://en.wikipedia.org/wiki/USBIP

### FastAPI & Dependencies

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Uvicorn Documentation**: https://www.uvicorn.org/
- **Jinja2 Documentation**: https://jinja.palletsprojects.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the project repository.

---

**Note**: USBIP operations require elevated privileges. Always ensure you understand the security implications of sharing USB devices over a network.
