import argparse
import json
import sys
import os

from .device import XiaomiVacuum


def resolve_token(token_arg: str | None) -> str:
    if token_arg:
        return token_arg
    env = os.environ.get("XIAOMI_VACUUM_TOKEN")
    if env:
        return env
    config_path = os.path.expanduser("~/.xiaomi-vacuum.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f).get("token", "")
    raise SystemExit("token not found. pass --token, set XIAOMI_VACUUM_TOKEN, or create ~/.xiaomi-vacuum.json")


def resolve_model(model_arg: str | None, info: dict) -> str:
    if model_arg:
        return model_arg
    env = os.environ.get("XIAOMI_VACUUM_MODEL")
    if env:
        return env
    config_path = os.path.expanduser("~/.xiaomi-vacuum.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            m = json.load(f).get("model")
            if m:
                return m
    return info.get("model", "")


def main():
    parser = argparse.ArgumentParser(prog="xiaomi-vacuum", description="Control Xiaomi/Dreame robot vacuums via MIoT")
    parser.add_argument("--ip", required=True, help="vacuum IP address")
    parser.add_argument("--token", help="device token (or set XIAOMI_VACUUM_TOKEN)")
    parser.add_argument("--model", help="device model (or set XIAOMI_VACUUM_MODEL)")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "start", "stop", "pause", "resume", "home",
                                 "info", "services", "list-props"])
    parser.add_argument("--set", nargs=2, metavar=("PROPERTY", "VALUE"), help="set a property value")
    parser.add_argument("--get", metavar="PROPERTY", help="read a property value")
    parser.add_argument("--json", action="store_true", help="output as JSON")

    args = parser.parse_args()
    token = resolve_token(args.token)

    vac = XiaomiVacuum(args.ip, token)

    info = vac.info()
    model = resolve_model(args.model, info)
    if model and not vac.services:
        vac.load_spec(model)

    if args.get:
        parts = args.get.split(".")
        if len(parts) == 2:
            val = vac.read_property(parts[0], parts[1])
        else:
            val = vac.read_property("vacuum", args.get)
        if args.json:
            print(json.dumps({"value": val}))
        else:
            print(val)
        return

    if args.set:
        prop_name, value = args.set
        parts = prop_name.split(".")
        if len(parts) == 2:
            svc_kw, prop_kw = parts
        else:
            svc_kw, prop_kw = "vacuum", prop_name
        try:
            value = int(value)
        except ValueError:
            if value.lower() in ("true", "yes", "on"):
                value = True
            elif value.lower() in ("false", "no", "off"):
                value = False
        result = vac.write_property(svc_kw, prop_kw, value)
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ok: {result}")
        return

    cmd = args.command

    if cmd == "info":
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            for k, v in info.items():
                if isinstance(v, dict):
                    print(f"{k}:")
                    for sk, sv in v.items():
                        print(f"  {sk}: {sv}")
                else:
                    print(f"{k}: {v}")

    elif cmd == "services":
        services = vac.list_services()
        if args.json:
            print(json.dumps(services, indent=2))
        else:
            for svc in services:
                print(f"  [{svc['iid']}] {svc['name']} ({svc['properties']} props, {svc['actions']} actions)")

    elif cmd == "list-props":
        vacuum_sid = vac._find_service("vacuum") or vac._find_service("robot cleaner")
        if not vacuum_sid:
            print("vacuum service not found")
            return
        svc = vac.services[vacuum_sid]
        if args.json:
            print(json.dumps(svc["properties"], indent=2))
        else:
            for pid, prop in svc["properties"].items():
                access = ",".join(prop["access"])
                vals = prop["values"]
                val_str = ""
                if vals:
                    val_str = " | ".join(f"{k}={v}" for k, v in vals.items())
                elif prop["range"]:
                    val_str = f"range: {prop['range']}"
                print(f"  [{pid}] {prop['name']} ({prop['format']}, {access}) {val_str}")

    elif cmd == "status":
        try:
            st = vac.status()
            if args.json:
                print(json.dumps(st, indent=2, ensure_ascii=False))
            else:
                for k, v in st.items():
                    print(f"  {k}: {v}")
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

    elif cmd in ("start", "stop", "pause", "resume", "home"):
        result = vac.vacuum_action(cmd if cmd != "home" else "gocharge")
        if args.json:
            print(json.dumps(result))
        else:
            print(f"ok: {result}")


if __name__ == "__main__":
    main()
