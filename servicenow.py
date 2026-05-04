import requests
from requests.auth import HTTPBasicAuth

# ── ServiceNow user map — synced from dev218436.service-now.com ───────────────
# These are real sys_ids for users created to match the mock data commit authors.
# When incidents/CHGs are raised, assigned_to is set to the correct user record.
SNOW_USER_MAP = {
    "jane.smith":    {"sys_id": "0de031cb832c0710900bc670ceaad3f6", "name": "Jane Smith",    "title": "Senior Backend Engineer",   "department": "Platform Engineering"},
    "grace.lee":     {"sys_id": "59e0794f832c0710900bc670ceaad3f9", "name": "Grace Lee",     "title": "Cloud Security Engineer",   "department": "Cloud Security"},
    "john.doe":      {"sys_id": "d1e0b94f832c0710900bc670ceaad30d", "name": "John Doe",      "title": "Full Stack Developer",      "department": "Application Dev"},
    "bob.wilson":    {"sys_id": "a5e0b94f832c0710900bc670ceaad314", "name": "Bob Wilson",    "title": "DevOps Engineer",           "department": "DevOps"},
    "alice.jones":   {"sys_id": "bde0b94f832c0710900bc670ceaad340", "name": "Alice Jones",   "title": "Site Reliability Engineer", "department": "SRE"},
    "diana.prince":  {"sys_id": "39e0b94f832c0710900bc670ceaad354", "name": "Diana Prince",  "title": "Security Architect",        "department": "Cloud Security"},
    "eve.carter":    {"sys_id": "cae0b94f832c0710900bc670ceaad35b", "name": "Eve Carter",    "title": "Backend Engineer",          "department": "Application Dev"},
    "frank.miller":  {"sys_id": "06e0b94f832c0710900bc670ceaad3df", "name": "Frank Miller",  "title": "Data Engineer",             "department": "Data Engineering"},
    "charlie.brown": {"sys_id": "d6e0b94f832c0710900bc670ceaad3e6", "name": "Charlie Brown", "title": "Infrastructure Engineer",   "department": "Platform Engineering"},
    "henry.ford":    {"sys_id": "eee0f94f832c0710900bc670ceaad312", "name": "Henry Ford",    "title": "Principal Engineer",        "department": "Architecture"},
}

# Severity → (urgency, impact)
SEVERITY_PRIORITY = {
    "CRITICAL": (1, 1),
    "HIGH":     (1, 2),
    "MEDIUM":   (2, 2),
    "LOW":      (3, 3),
}


def _resolve_user(commit_author: str) -> str:
    """Return the ServiceNow sys_id for a known commit author, or empty string."""
    entry = SNOW_USER_MAP.get(commit_author.lower().replace(" ", "."), {})
    return entry.get("sys_id", "")


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
        subcategory: str = "Security",
        assignment_group: str = "Cloud Security",
        commit_author: str = "",
        severity: str = "",
    ) -> dict:
        # Auto-derive urgency/impact from severity if provided
        if severity and severity.upper() in SEVERITY_PRIORITY:
            urgency, impact = SEVERITY_PRIORITY[severity.upper()]

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

        # Assign to the real user if commit author is known
        user_sys_id = _resolve_user(commit_author) if commit_author else ""
        if user_sys_id:
            payload["assigned_to"] = user_sys_id

        try:
            r = self._req("POST", "/table/incident", json=payload)
            if r.status_code == 201:
                res = r.json()["result"]
                return {
                    "ok":          True,
                    "number":      res["number"],
                    "sys_id":      res["sys_id"],
                    "url":         f"{self.base}/nav_to.do?uri=incident.do?sys_id={res['sys_id']}",
                    "assigned_to": SNOW_USER_MAP.get(commit_author, {}).get("name", "Unassigned"),
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
        assignment_group: str = "Cloud Security",
        commit_author: str = "",
        severity: str = "",
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

        user_sys_id = _resolve_user(commit_author) if commit_author else ""
        if user_sys_id:
            payload["assigned_to"] = user_sys_id

        try:
            r = self._req("POST", "/table/change_request", json=payload)
            if r.status_code == 201:
                res = r.json()["result"]
                return {
                    "ok":          True,
                    "number":      res["number"],
                    "sys_id":      res["sys_id"],
                    "url":         f"{self.base}/nav_to.do?uri=change_request.do?sys_id={res['sys_id']}",
                    "assigned_to": SNOW_USER_MAP.get(commit_author, {}).get("name", "Unassigned"),
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
