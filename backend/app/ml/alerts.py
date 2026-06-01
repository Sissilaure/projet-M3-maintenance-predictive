from __future__ import annotations

from backend.app.schemas.prediction import Alert


def _value(values: dict, *names: str) -> float | None:
    lowered = {str(k).lower(): v for k, v in values.items()}
    for name in names:
        for key, val in lowered.items():
            if name in key:
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return None
    return None


def risk_level(probability: float, rul: float | None = None) -> str:
    if probability >= 0.75 or (rul is not None and rul <= 10):
        return "critique"
    if probability >= 0.45 or (rul is not None and rul <= 30):
        return "moyen"
    return "faible"


def generate_alerts(equipment_id: str, values: dict, failure_probability: float = 0.0, rul: float | None = None) -> list[Alert]:
    alerts: list[Alert] = []
    level = risk_level(failure_probability, rul)
    if level != "faible":
        alerts.append(Alert(
            equipment_id=equipment_id,
            level=level,
            title="Risque de panne élevé",
            message=f"Probabilité de panne estimée à {failure_probability:.0%}.",
            recommendation="Planifier une inspection ciblée et réduire la charge de production si possible.",
            score=float(failure_probability),
        ))

    temp = _value(values, "temp", "temperature")
    vib = _value(values, "vib", "vibration")
    pressure = _value(values, "pressure", "pression")
    thresholds = [
        (temp, 85, "Température anormale", "Contrôler refroidissement, lubrification et charge moteur."),
        (vib, 55, "Vibrations excessives", "Inspecter roulements, alignement et fixation mécanique."),
        (pressure, 120, "Pression anormale", "Vérifier circuits hydrauliques, filtres et valves."),
    ]
    for value, threshold, title, reco in thresholds:
        if value is not None and value >= threshold:
            alerts.append(Alert(equipment_id=equipment_id, level="critique", title=title, message=f"Valeur mesurée: {value:.2f}, seuil: {threshold}.", recommendation=reco, score=float(value / threshold)))
    if rul is not None and rul <= 10:
        alerts.append(Alert(equipment_id=equipment_id, level="critique", title="RUL critique", message=f"Durée de vie résiduelle estimée: {rul:.1f}.", recommendation="Créer un ordre de maintenance préventive immédiat.", score=float(max(0, 1 - rul / 10))))
    return alerts
