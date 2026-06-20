from miio.miioprotocol import MiIOProtocol
from .spec import fetch_spec, parse_services


class XiaomiVacuum:
    def __init__(self, ip: str, token: str, model: str = None):
        self.ip = ip
        self.token = token
        self.model = model
        self.proto = MiIOProtocol(ip, token)
        self.proto.send_handshake()
        self.services = {}
        if model:
            self.load_spec(model)

    def load_spec(self, model: str):
        raw = fetch_spec(model)
        self.services = parse_services(raw)
        self.model = model

    def _find_service(self, keyword: str) -> int | None:
        keyword = keyword.lower()
        for sid, svc in self.services.items():
            if keyword in svc["name"].lower():
                return sid
        return None

    def _find_action(self, service_id: int, keyword: str) -> int | None:
        keyword = keyword.lower()
        svc = self.services.get(service_id, {})
        for aid, act in svc.get("actions", {}).items():
            if keyword in act["name"].lower():
                return aid
        return None

    def _find_property(self, service_id: int, keyword: str) -> int | None:
        keyword = keyword.lower()
        svc = self.services.get(service_id, {})
        for pid, prop in svc.get("properties", {}).items():
            if keyword in prop["name"].lower():
                return pid
        return None

    def action(self, siid: int, aiid: int, params=None):
        return self.proto.send("action", {
            "siid": siid,
            "aiid": aiid,
            "in": params or [],
        })

    def get_properties(self, props: list[dict]):
        return self.proto.send("get_properties", props)

    def set_property(self, siid: int, piid: int, value):
        return self.proto.send("set_properties", [{
            "siid": siid,
            "piid": piid,
            "value": value,
        }])

    def info(self):
        return self.proto.send("miIO.info", [])

    def vacuum_action(self, name: str):
        sid = self._find_service("vacuum") or self._find_service("robot cleaner")
        if not sid:
            raise RuntimeError("vacuum service not found in spec")
        aid = self._find_action(sid, name)
        if not aid:
            raise RuntimeError(f"action '{name}' not found in vacuum service")
        return self.action(sid, aid)

    def read_property(self, service_keyword: str, property_keyword: str):
        sid = self._find_service(service_keyword)
        if not sid:
            raise RuntimeError(f"service '{service_keyword}' not found")
        pid = self._find_property(sid, property_keyword)
        if not pid:
            raise RuntimeError(f"property '{property_keyword}' not found in service '{service_keyword}'")
        result = self.get_properties([{"siid": sid, "piid": pid}])
        if result and result[0].get("code") == 0:
            return result[0]["value"]
        raise RuntimeError(f"failed to read property: {result}")

    def write_property(self, service_keyword: str, property_keyword: str, value):
        sid = self._find_service(service_keyword)
        if not sid:
            raise RuntimeError(f"service '{service_keyword}' not found")
        pid = self._find_property(sid, property_keyword)
        if not pid:
            raise RuntimeError(f"property '{property_keyword}' not found in service '{service_keyword}'")
        return self.set_property(sid, pid, value)

    def start(self):
        return self.vacuum_action("start")

    def stop(self):
        return self.vacuum_action("stop")

    def pause(self):
        return self.vacuum_action("pause")

    def resume(self):
        return self.vacuum_action("continue")

    def home(self):
        return self.vacuum_action("gocharge") or self.vacuum_action("charge")

    def status(self):
        vacuum_sid = self._find_service("vacuum") or self._find_service("robot cleaner")
        battery_sid = self._find_service("battery")
        result = {}
        if vacuum_sid:
            for pid, prop in self.services[vacuum_sid]["properties"].items():
                if "read" in prop["access"]:
                    result[prop["name"]] = self.read_property(
                        self.services[vacuum_sid]["name"], prop["name"]
                    )
        if battery_sid:
            for pid, prop in self.services[battery_sid]["properties"].items():
                if "read" in prop["access"]:
                    result[prop["name"]] = self.read_property(
                        self.services[battery_sid]["name"], prop["name"]
                    )
        return result

    def list_services(self):
        output = []
        for sid, svc in self.services.items():
            props = list(svc["properties"].keys())
            actions = list(svc["actions"].keys())
            output.append({
                "iid": sid,
                "name": svc["name"],
                "properties": len(props),
                "actions": len(actions),
            })
        return output
