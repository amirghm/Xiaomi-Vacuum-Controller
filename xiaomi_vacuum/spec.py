import requests


SPEC_CACHE = {}


def fetch_spec(model):
    if model in SPEC_CACHE:
        return SPEC_CACHE[model]
    url = f"https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:{model}:1"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    SPEC_CACHE[model] = data
    return data


def parse_services(spec):
    services = {}
    for svc in spec.get("services", []):
        sid = svc["iid"]
        props = {}
        for p in svc.get("properties", []):
            props[p["iid"]] = {
                "name": p["description"],
                "format": p["format"],
                "access": p.get("access", []),
                "values": {v["value"]: v["description"] for v in p.get("value-list", [])},
                "range": p.get("value-range"),
            }
        actions = {}
        for a in svc.get("actions", []):
            actions[a["iid"]] = {
                "name": a["description"],
                "in": a.get("in", []),
                "out": a.get("out", []),
            }
        services[sid] = {
            "name": svc["description"],
            "properties": props,
            "actions": actions,
        }
    return services
