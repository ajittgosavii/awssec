import requests
from requests.auth import HTTPBasicAuth


class ServiceNowClient:
    PRIORITY_MAP = {
        (1, 1): "1", (1, 2): "2", (1, 3): "3",
        (2, 1): "2", (2, 2): "3", (2, 3): "4",
        (3, 1): "3", (3, 2): "4", (3, 3): "4",
    }

    def __init__(self, instance_url: str, username: str, password: str):
        self.base    = instance_url.rstrip("/")
        self.auth    = HTTPBasicAuth(username, password)
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def _req(self, method: str, path: str, **kwargs) -> requests.Response:
        return requests.request(
            method,
            f"{self.base}/api/now{path}",
            auth=self.auth,
            headers=self.headers,
            timeout=kwargs.pop("timeout", 20),
            **kwargs,
        )

    def test_connection(self) -> dict:
        try:
            r = self._req("GET", "/table/incident?sysparm_limit=1")
            if r.status_code == 200:
                count = len(r.json().get("result", []))
                return {"ok": True, "msg": f"Connected — ServiceNow responded (fetched {count} record)"}
            return {"ok": False, "msg": f"HTTP {r.status_code}: {r.text[:200]}"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def create_incident(
        self,
        short_description: str,
        description: str,
        urgency: int = 2,
        impact: int = 2,
        category: str = "Cloud Services",
        subcategory: str = "Backup & Recovery",
        assignment_group: str = "Cloud Infrastructure",
    ) -> dict:
        priority = self.PRIORITY_MAP.get((urgency, impact), "3")
        payload = {
            "short_description": short_description[:160],
            "description":       description,
            "urgency":           str(urgency),
            "impact":            str(impact),
            "priority":          priority,
            "category":          category,
            "subcategory":       subcategory,
            "assignment_group":  assignment_group,
            "state":             "1",
        }
        try:
            r = self._req("POST", "/table/incident", json=payload)
            if r.status_code == 201:
                res = r.json()["result"]
                return {
                    "ok":     True,
                    "number": res["number"],
                    "sys_id": res["sys_id"],
                    "url":    f"{self.base}/nav_to.do?uri=incident.do?sys_id={res['sys_id']}",
                }
            return {"ok": False, "error": f"HTTP {r.status_code}", "detail": r.text[:400]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def create_change_request(
        self,
        short_description: str,
        description: str,
        change_type: str = "Normal",
        risk: str = "Moderate",
        assignment_group: str = "Cloud Infrastructure",
    ) -> dict:
        payload = {
            "short_description": short_description[:160],
            "description":       description,
            "type":              change_type.lower(),
            "risk":              risk,
            "assignment_group":  assignment_group,
            "category":          "Cloud Services",
            "state":             "-5",
        }
        try:
            r = self._req("POST", "/table/change_request", json=payload)
            if r.status_code == 201:
                res = r.json()["result"]
                return {
                    "ok":     True,
                    "number": res["number"],
                    "sys_id": res["sys_id"],
                    "url":    f"{self.base}/nav_to.do?uri=change_request.do?sys_id={res['sys_id']}",
                }
            return {"ok": False, "error": f"HTTP {r.status_code}", "detail": r.text[:400]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_incidents(self, query: str = "", limit: int = 100) -> dict:
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        try:
            r = self._req("GET", "/table/incident", params=params)
            if r.status_code == 200:
                return {"ok": True, "data": r.json()["result"]}
            return {"ok": False, "error": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update_incident(self, sys_id: str, fields: dict) -> dict:
        try:
            r = self._req("PATCH", f"/table/incident/{sys_id}", json=fields)
            if r.status_code == 200:
                return {"ok": True, "data": r.json()["result"]}
            return {"ok": False, "error": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
