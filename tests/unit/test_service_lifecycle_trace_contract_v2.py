from __future__ import annotations

import json

from leo_twin.schema.service_lifecycle_trace_contract import (
    SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID,
    service_lifecycle_trace_contract_v2_to_dict,
)


def test_service_lifecycle_trace_contract_v2_is_deterministic_and_json_ready() -> None:
    first = service_lifecycle_trace_contract_v2_to_dict()
    second = service_lifecycle_trace_contract_v2_to_dict()

    assert first == second
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID
    )
    assert first["source_summary"] == "service_latency_history_v1"
    assert first["trace_kind"] == "COMMUNICATION_COMPUTE_SERVICE_TRACE"
    assert tuple(item["stage"] for item in first["stage_contracts"]) == (
        "INPUT_NETWORK",
        "COMPUTE_QUEUE",
        "COMPUTE_EXECUTION",
        "OUTPUT_NETWORK",
        "TERMINAL",
    )
    assert first["terminal_states"] == ("RUNNING", "COMPLETE", "INCOMPLETE")
    assert "PACKET_LEVEL_TIMELINE" in first["excluded_semantics"]
    assert "EXTERNAL_NETWORK_SIMULATOR" in first["excluded_semantics"]
