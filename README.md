# xiaomi-vacuum

Local control for Xiaomi and Dreame robot vacuums via the MIoT protocol.

If your vacuum gives you `user ack timeout` when using classic `miio` commands — this library is the fix.

## Install

```bash
pip install xiaomi-vacuum
```

Or from source:

```bash
git clone https://github.com/amirghm/Xiaomi-Vacuum-Controller.git
cd Xiaomi-Vacuum-Controller
pip install .
```

## Quick Start

```python
from xiaomi_vacuum import XiaomiVacuum

vac = XiaomiVacuum("192.168.1.100", "your_token_here", "xiaomi.vacuum.d109gl")

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

## Finding Your Token

Use [Xiaomi Cloud Tokens Extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) to get your device token.

## Configuration

Instead of passing token/model every time, create `~/.xiaomi-vacuum.json`:

```json
{
    "token": "your_32char_token",
    "model": "xiaomi.vacuum.d109gl"
}
```

Or use environment variables:

```bash
export XIAOMI_VACUUM_TOKEN="***" XIAOMI_VACUUM_MODEL="xiaomi.vacuum.d109gl"
```

## Supported Devices

Any Xiaomi/Dreame vacuum with a MIoT spec on [miot-spec.org](https://miot-spec.org). The library auto-fetches the spec for your model.

Tested:
- Xiaomi Robot Vacuum X20 Max (`xiaomi.vacuum.d109gl`)

## How It Works

Newer Xiaomi vacuums dropped support for the classic `miio` RPC protocol. Commands like `get_status` and `get_prop` timeout with `user ack timeout`.

This library uses the **MIoT action** protocol instead — the same one the Mi Home app uses internally. It fetches the device spec from Xiaomi's official spec database and maps service/property IDs automatically.

## License

MIT
