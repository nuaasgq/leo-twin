from __future__ import annotations

import json

from leo_twin.schema import (
    CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID,
    ComputeServiceActionKind,
    ComputeServiceActionStatus,
    cache_offload_migration_contract_v1_to_dict,
)


def test_cache_offload_migration_contract_v1_is_deterministic_and_json_ready() -> None:
    first = cache_offload_migration_contract_v1_to_dict()
    second = cache_offload_migration_contract_v1_to_dict()

    assert first == second
    assert first["contract_id"] == CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID
    assert first["version"] == "v1"
    assert first["optimization_scope"] == (
        "CONTRACT_AND_OBSERVABILITY_ONLY_FOR_SATELLITE_HOSTED_COMPUTE_SERVICES"
    )
    assert first["canonical_statuses"] == tuple(
        status.value for status in ComputeServiceActionStatus
    )
    assert tuple(item["action"] for item in first["action_contracts"]) == tuple(
        action.value for action in ComputeServiceActionKind
    )
    assert "REAL_CACHE_ENGINE" in first["excluded_semantics"]
    assert "THREAD_OR_PROCESS_MIGRATION" in first["excluded_semantics"]
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        CACHE_OFFLOAD_MIGRATION_CONTRACT_V1_ID
    )


def test_cache_offload_migration_contract_v1_exposes_observability_fields() -> None:
    contract = cache_offload_migration_contract_v1_to_dict()
    by_action = {
        item["action"]: item for item in contract["action_contracts"]
    }

    assert by_action["CACHE_LOOKUP"]["runtime_observability_fields"] == (
        "cache_lookup_status",
        "cache_hit",
        "cache_node_id",
        "cache_age_s",
    )
    assert by_action["TASK_OFFLOAD"]["decision_fields"] == (
        "offload_status",
        "offload_source_node_id",
        "offload_target_node_id",
        "offload_reason",
    )
    assert by_action["SERVICE_MIGRATION"]["excluded_semantics"] == (
        "REAL_PROCESS_CHECKPOINT_RESTORE",
        "MEMORY_PAGE_TRANSFER",
        "CONSISTENCY_PROTOCOL",
    )
