from leo_twin.models import NetworkEngine
from leo_twin.schema import CoverageSlot, GroundUserProfile, SatelliteProfile


def test_network_engine_supports_72_satellite_1000_user_baseline() -> None:
    cell_count = 100
    satellites = tuple(
        SatelliteProfile(
            satellite_id=f"sat-{index:03d}",
            coverage=(
                CoverageSlot(
                    slot=0,
                    cell_ids=(
                        f"cell-{index % cell_count:03d}",
                        f"cell-{(index + 1) % cell_count:03d}",
                    ),
                ),
            ),
            link_latency=10.0 + float(index % 5),
            link_capacity=100.0,
        )
        for index in range(72)
    )
    ground_users = tuple(
        GroundUserProfile(
            user_id=f"user-{index:04d}",
            cell_id=f"cell-{index % cell_count:03d}",
        )
        for index in range(1000)
    )
    engine = NetworkEngine(satellites=satellites, ground_users=ground_users)

    events = engine.update_topology(0.0)

    assert len(engine.compute_access()) == 1440
    assert len(events) == 2880
