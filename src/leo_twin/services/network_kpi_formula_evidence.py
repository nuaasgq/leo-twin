"""Product-facing network KPI formula evidence summary v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


NETWORK_KPI_FORMULA_EVIDENCE_V1_ID = "leo_twin.network_kpi_formula_evidence.v1"

NetworkKpiFormulaEvidenceV1 = dict[str, object]


def build_network_kpi_formula_evidence_v1(
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any],
    calibration: Mapping[str, Any],
) -> NetworkKpiFormulaEvidenceV1:
    """Combine KPI provenance and calibration into readable formula evidence.

    This function does not change KPI formulas. It only summarizes which
    runtime inputs selected each KPI value and whether the corresponding time
    series has moved over simulation time.
    """

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    if not isinstance(provenance, Mapping):
        raise TypeError("provenance must be a mapping")
    if not isinstance(calibration, Mapping):
        raise TypeError("calibration must be a mapping")

    calibration_by_metric = {
        str(item.get("metric", "")): item
        for item in _records(calibration.get("kpis"))
    }
    kpis = tuple(
        _formula_evidence_item(kpi, calibration_by_metric.get(str(kpi.get("metric", ""))))
        for kpi in _records(provenance.get("kpis"))
    )
    observed = tuple(item for item in kpis if item["status"] == "OBSERVED")
    missing_runtime = tuple(item for item in kpis if item["status"] != "OBSERVED")
    selected_input_count = sum(int(item["selected_input_count"]) for item in kpis)
    selected_observed_input_count = sum(
        int(item["selected_observed_input_count"]) for item in kpis
    )
    missing_selected_input_count = sum(
        int(item["missing_selected_input_count"]) for item in kpis
    )
    time_varying = tuple(
        item for item in kpis if item["variation_status"] == "TIME_VARYING"
    )
    flat = tuple(
        item
        for item in kpis
        if str(item["variation_status"]).startswith("FLAT")
    )
    return {
        "version": "v1",
        "evidence_id": NETWORK_KPI_FORMULA_EVIDENCE_V1_ID,
        "source": "NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
        "provenance_id": str(provenance.get("provenance_id", "")),
        "calibration_id": str(calibration.get("calibration_id", "")),
        "metric_model": str(
            provenance.get(
                "metric_model",
                metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY"),
            )
        ),
        "packet_level_simulation": bool(
            provenance.get("packet_level_simulation") is True
            or calibration.get("packet_level_simulation") is True
        ),
        "kpi_count": len(kpis),
        "observed_kpi_count": len(observed),
        "runtime_value_missing_count": len(missing_runtime),
        "selected_input_count": selected_input_count,
        "selected_observed_input_count": selected_observed_input_count,
        "missing_selected_input_count": missing_selected_input_count,
        "time_varying_kpi_count": len(time_varying),
        "flat_kpi_count": len(flat),
        "formula_evidence_status": _formula_evidence_status(
            kpi_count=len(kpis),
            missing_runtime_count=len(missing_runtime),
            missing_selected_input_count=missing_selected_input_count,
            sample_count=_int(calibration.get("sample_count")),
            time_varying_count=len(time_varying),
            flat_count=len(flat),
            observed_count=len(observed),
        ),
        "kpis": kpis,
        "caveats": _caveats(),
    }


def _formula_evidence_item(
    kpi: Mapping[str, Any],
    calibration: Mapping[str, Any] | None,
) -> dict[str, object]:
    formula_trace = _mapping(kpi.get("formula_trace"))
    inputs = tuple(_records(kpi.get("formula_inputs")))
    selected_inputs = tuple(
        item for item in inputs if item.get("selected_for_current_value") is True
    )
    selected_observed = tuple(
        item for item in selected_inputs if item.get("observed") is True
    )
    missing_selected = tuple(
        item for item in selected_inputs if item.get("observed") is not True
    )
    calibration_record = {} if calibration is None else dict(calibration)
    status = str(kpi.get("status", ""))
    variation_status = str(
        calibration_record.get("variation_status", "MISSING_CALIBRATION")
    )
    return {
        "metric": str(kpi.get("metric", "")),
        "display_name": str(kpi.get("display_name", "")),
        "runtime_summary_key": str(kpi.get("runtime_summary_key", "")),
        "current_value": _json_value(kpi.get("current_value")),
        "unit": str(kpi.get("unit", "")),
        "status": status,
        "observed_source": str(_mapping(kpi.get("observed_source")).get("source", "")),
        "observed_source_label": str(
            _mapping(kpi.get("observed_source")).get("label", "")
        ),
        "formula_summary": str(kpi.get("formula_summary", "")),
        "selection_policy": str(formula_trace.get("selection_policy", "")),
        "selected_input_count": len(selected_inputs),
        "selected_observed_input_count": len(selected_observed),
        "missing_selected_input_count": len(missing_selected),
        "selected_inputs": tuple(_selected_input_record(item) for item in selected_inputs),
        "variation_status": variation_status,
        "flat_reason": str(calibration_record.get("flat_reason", "")),
        "latest_is_zero": calibration_record.get("latest_is_zero") is True,
        "evidence_status": _kpi_evidence_status(
            status=status,
            missing_selected_input_count=len(missing_selected),
            variation_status=variation_status,
        ),
    }


def _kpi_evidence_status(
    *,
    status: str,
    missing_selected_input_count: int,
    variation_status: str,
) -> str:
    if status != "OBSERVED":
        return "MISSING_RUNTIME_VALUE"
    if missing_selected_input_count > 0:
        return "MISSING_SELECTED_INPUT"
    if variation_status == "TIME_VARYING":
        return "FORMULA_AND_TIME_VARYING"
    if variation_status in {"MISSING_CALIBRATION", "MISSING_SAMPLE_VALUE"}:
        return "FORMULA_ONLY_NO_SAMPLE"
    return "FORMULA_READY_FLAT_OR_LIMITED_SERIES"


def _formula_evidence_status(
    *,
    kpi_count: int,
    missing_runtime_count: int,
    missing_selected_input_count: int,
    sample_count: int,
    time_varying_count: int,
    flat_count: int,
    observed_count: int,
) -> str:
    if kpi_count == 0:
        return "NO_KPI_PROVENANCE"
    if missing_runtime_count > 0:
        return "PARTIAL_RUNTIME_VALUES"
    if missing_selected_input_count > 0:
        return "MISSING_SELECTED_INPUTS"
    if time_varying_count > 0:
        return "FORMULA_AND_TIME_EVIDENCE_READY"
    if sample_count < 2:
        return "FORMULA_READY_INSUFFICIENT_SERIES"
    if flat_count >= observed_count:
        return "FORMULA_READY_FLAT_SERIES"
    return "FORMULA_READY"


def _selected_input_record(input_record: Mapping[str, Any]) -> dict[str, object]:
    return {
        "field": str(input_record.get("field", "")),
        "current_value": _json_value(input_record.get("current_value")),
        "observed": input_record.get("observed") is True,
        "role": str(input_record.get("role", "")),
        "selection_reason": str(input_record.get("selection_reason", "")),
    }


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _json_value(value: object) -> str | int | float | bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    return None


def _caveats() -> tuple[str, ...]:
    return (
        "Formula evidence summarizes backend flow-level proxy inputs; it is not packet-level telemetry.",
        "Time-varying evidence comes from kpi_time_series_v1 calibration and can remain flat when route, flow, and pressure inputs are unchanged.",
        "Selected inputs explain why the current runtime value was chosen from the declared formula inputs.",
    )


__all__ = [
    "NETWORK_KPI_FORMULA_EVIDENCE_V1_ID",
    "NetworkKpiFormulaEvidenceV1",
    "build_network_kpi_formula_evidence_v1",
]
