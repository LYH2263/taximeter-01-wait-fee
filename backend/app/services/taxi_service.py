from app.db import connect
from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.modules.wait_fee import repository as wait_repo
from app.modules.wait_fee.engine import calc_wait_fee
from app.repositories import runs, settings, tariff, trips

class TaxiService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_trips(self): return trips.list_all(self._c)
    def trip(self, tid): return trips.get(self._c, tid)
    def tariff(self): return tariff.get_active(self._c)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def list_wait_rules(self): return wait_repo.list_all(self._c)
    def active_wait_rule(self): return wait_repo.get_active(self._c)
    def create_wait_rule(self, free_min, per_min_price, active=True):
        return wait_repo.insert(self._c, free_min, per_min_price, active)
    def update_wait_rule(self, rule_id, changes):
        return wait_repo.update(self._c, rule_id, changes)
    def disable_wait_rule(self, rule_id):
        return wait_repo.update(self._c, rule_id, {"active": False})
    def fare(self, distance_km, slow_min, night, trip_id, persist, wait_min=0.0):
        t = tariff.get_active(self._c)
        wrule = wait_repo.get_active(self._c)
        w = calc_wait_fee(wait_min, wrule)
        w["wait_min"] = wait_min
        r = calc_fare(distance_km, slow_min, night, t, w)
        rid = runs.insert(self._c, "fare", {"distance_km": distance_km, "slow_min": slow_min, "wait_min": wait_min, "night": night}, r, trip_id) if persist else None
        return {"run_id": rid, **r}
    def compare(self, distance_km, slow_min, persist):
        t = tariff.get_active(self._c)
        r = compare_day_night(distance_km, slow_min, t)
        rid = runs.insert(self._c, "compare", {"distance_km": distance_km, "slow_min": slow_min}, r, None) if persist else None
        return {"run_id": rid, **r}
    def dashboard(self):
        items = trips.list_all(self._c)
        clean = [x for x in items if "种子" not in x["label"]]
        dirty = [x for x in items if "种子" in x["label"]]
        return {"trip_count": len(items), "clean": len(clean), "dirty": len(dirty)}
