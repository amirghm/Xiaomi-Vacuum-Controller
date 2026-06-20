# xiaomi-vacuum 🤖

Local control for Xiaomi and Dreame robot vacuums via the MIoT protocol.

Control your vacuum from Python, build custom dashboards, or integrate with AI agents — all without the cloud.

## 🏠 Use Cases

- **Home automation**: Integrate your vacuum with Home Assistant, OpenHAB, or any custom automation system
- **Voice control**: Build a voice assistant that controls your vacuum ("Alexa, tell the vacuum to clean the living room")
- **AI agents**: Let AI agents manage your cleaning schedule and preferences
- **Custom dashboards**: Create web interfaces to monitor and control your vacuum
- **Multi-device control**: Manage multiple vacuums from a single script
- **Scheduled cleaning**: Set up automated cleaning routines with custom logic
- **Status monitoring**: Get real-time battery, cleaning progress, and consumable status
- **Energy optimization**: Track battery usage and optimize cleaning patterns

## 🚀 Install

```bash
pip install xiaomi-vacuum
```

Or from source:

```bash
git clone https://github.com/amirghm/Xiaomi-Vacuum-Controller.git
cd Xiaomi-Vacuum-Controller
pip install .
```

## ⚡ Quick Start

### Python

```python
from xiaomi_vacuum import XiaomiVacuum

vac = XiaomiVacuum("192.168.1.100", "your_32char_token_here", "xiaomi.vacuum.d109gl")

vac.start()
vac.stop()
vac.home()

status = vac.status()
print(status)
```

### CLI

```bash
xiaomi-vacuum --ip 192.168.1.100 --token YOUR_TOKEN --model xiaomi.vacuum.d109gl status
xiaomi-vacuum --ip 192.168.1.100 --token YOUR_TOKEN --model xiaomi.vacuum.d109gl start
```

### AI Agent Integration

```python
# Example: Simple AI agent for vacuum control
from xiaomi_vacuum import XiaomiVacuum

def handle_command(command: str, vac: XiaomiVacuum) -> str:
    """Process natural language commands and control the vacuum."""
    command = command.lower()

    if "start" in command or "clean" in command:
        vac.start()
        return "Vacuum started cleaning"
    elif "stop" in command:
        vac.stop()
        return "Vacuum stopped"
    elif "home" in command or "charge" in command:
        vac.home()
        return "Vacuum returning to charger"
    elif "status" in command or "battery" in command:
        status = vac.status()
        return f"Battery: {status.get('battery_level', 'unknown')}%, Status: {status.get('status', 'unknown')}"
    else:
        return "Unknown command. Try: start, stop, home, status"

# Usage
vac = XiaomiVacuum("192.168.1.100", "your_token", "xiaomi.vacuum.d109gl")
response = handle_command("start cleaning", vac)
print(response)
```

## 🔑 Finding Your Token

Use [Xiaomi Cloud Tokens Extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) to get your device token.

## ⚙️ Configuration

Instead of passing token/model every time, create `~/.xiaomi-vacuum.json`:

```json
{
    "token": "your_32char_token",
    "model": "xiaomi.vacuum.d109gl"
}
```

Or use environment variables:

```bash
export XIAOMI_VACUUM_TOKEN=*** XIAOMI_VACUUM_MODEL="xiaomi.vacuum.d109gl"
```

## 📱 Supported Devices

Any Xiaomi/Dreame vacuum with a MIoT spec on [miot-spec.org](https://miot-spec.org). The library auto-fetches the spec for your model.

Tested:
- Xiaomi Robot Vacuum X20 Max (`xiaomi.vacuum.d109gl`)

## 🔧 How It Works

Newer Xiaomi vacuums dropped support for the classic `miio` RPC protocol. Commands like `get_status` and `get_prop` timeout with `user ack timeout`.

This library uses the **MIoT action** protocol instead — the same one the Mi Home app uses internally. It fetches the device spec from Xiaomi's official spec database and maps service/property IDs automatically.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
