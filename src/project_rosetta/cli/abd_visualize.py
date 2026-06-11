import argparse
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
from scenariogeneration import xosc

from project_rosetta.utils.run_esmini import run_esmini, setup_run_config

CAR_MODELS = ["car_white.osgb", "car_blue.osgb", "car_red.osgb", "car_yellow.osgb"]
SUBJECT_COLUMNS = [
    "System Time",
    "Actual X (front axle)",
    "Actual Y (front axle)",
    "Actual X (rear axle)",
    "Actual Y (rear axle)",
]
OBJECT_X_PATTERN = re.compile(r"^Object (?P<id>\d+) actual X \(front axle\)$")


def read_trajectories(log_path: Path) -> dict[str, pd.DataFrame]:
    """
    Read subject and object coordinates from an ABD tab log.

    Returns:
        Actor trajectories with x, y, time, and yaw columns.

    Raises:
        ValueError: If required subject channels are missing.

    """
    data = pd.read_csv(
        log_path,
        sep="\t",
        header=2,
        encoding="ISO-8859-1",
        keep_default_na=False,
        low_memory=False,
    )
    data = data.iloc[1:].replace(",", ".", regex=True).apply(pd.to_numeric, errors="coerce")
    missing = [column for column in SUBJECT_COLUMNS if column not in data]
    if missing:
        raise ValueError(f"Missing ABD channels: {', '.join(missing)}")

    frames = {
        "subject": pd.DataFrame(
            {
                "x": (data["Actual X (front axle)"] + data["Actual X (rear axle)"]) / 2,
                "y": (data["Actual Y (front axle)"] + data["Actual Y (rear axle)"]) / 2,
                "time": data["System Time"],
            }
        )
    }
    for column in data:
        match = OBJECT_X_PATTERN.match(column)
        if match:
            object_id = match.group("id")
            y_column = f"Object {object_id} actual Y (front axle)"
            if y_column in data:
                frames[f"object_{object_id}"] = pd.DataFrame(
                    {"x": data[column], "y": data[y_column], "time": data["System Time"]}
                )

    for name, frame in frames.items():
        frame.dropna(inplace=True)
        frame["time"] -= frame["time"].iloc[0]
        dx = frame["x"].diff()
        dy = frame["y"].diff()
        yaw = pd.Series(np.where(np.hypot(dx, dy) > 0.001, np.arctan2(dy, dx), np.nan))
        frame["yaw"] = np.unwrap(yaw.ffill().bfill().fillna(0).to_numpy())
        frames[name] = frame
    return frames


def write_scenario(frames: dict[str, pd.DataFrame], output_path: Path) -> None:
    """Write a roadless OpenSCENARIO replay using logged coordinates directly."""
    entities = xosc.Entities()
    init = xosc.Init()
    stop_time = max(frame["time"].iloc[-1] for frame in frames.values())
    act = xosc.Act("abd_replay", stoptrigger=_time_trigger("act_stop", stop_time, "stop"))

    for index, (name, frame) in enumerate(frames.items()):
        entities.add_scenario_object(
            name,
            _vehicle(name, CAR_MODELS[index % len(CAR_MODELS)]),
        )
        init.add_init_action(name, xosc.TeleportAction(_position(frame.iloc[0])))

        trajectory = xosc.Trajectory(f"{name}_trajectory", closed=False)
        trajectory.add_shape(
            xosc.Polyline(
                time=frame["time"].tolist(),
                positions=[_position(row) for row in frame.itertuples()],
            )
        )
        event = xosc.Event(f"{name}_event", xosc.Priority.overwrite)
        event.add_action(
            f"{name}_action",
            xosc.FollowTrajectoryAction(
                trajectory,
                following_mode=xosc.FollowingMode.position,
                reference_domain=xosc.ReferenceContext.absolute,
                scale=1,
                offset=0,
            ),
        )
        event.add_trigger(_time_trigger(f"{name}_start", 0, "start"))
        maneuver = xosc.Maneuver(f"{name}_maneuver")
        maneuver.add_event(event)
        group = xosc.ManeuverGroup(f"{name}_group")
        group.add_actor(name)
        group.add_maneuver(maneuver)
        act.add_maneuver_group(group)

    storyboard = xosc.StoryBoard(init, _time_trigger("scenario_stop", stop_time, "stop"))
    storyboard.add_act(act)
    scenario = xosc.Scenario(
        "ABD log replay",
        "project-rosetta",
        xosc.ParameterDeclarations(),
        entities,
        storyboard,
        xosc.RoadNetwork(),
        xosc.Catalog(),
        osc_minor_version=1,
    )
    scenario.write_xml(str(output_path))


def _vehicle(name: str, model: str) -> xosc.Vehicle:
    return xosc.Vehicle(
        f"{name}_vehicle",
        xosc.VehicleCategory.car,
        xosc.BoundingBox(1.8, 4.5, 1.8, 1.5, 0, 0.9),
        xosc.Axle(0.5, 0.6, 1.6, 3.1, 0.3),
        xosc.Axle(0, 0.6, 1.6, 0, 0.3),
        69,
        10,
        10,
        model3d=model,
    )


def _position(row) -> xosc.WorldPosition:
    return xosc.WorldPosition(x=row.x, y=row.y, h=row.yaw)


def _time_trigger(name: str, time: float, point: str) -> xosc.ValueTrigger:
    return xosc.ValueTrigger(
        name,
        0,
        xosc.ConditionEdge.none,
        xosc.SimulationTimeCondition(float(time), xosc.Rule.greaterThan),
        triggeringpoint=point,
    )


def main(argv: list[str] | None = None) -> int:
    """
    Replay an ABD log in the esmini viewer.

    Returns:
        Exit status code.

    """
    parser = argparse.ArgumentParser(description="Replay an ABD log in esmini.")
    parser.add_argument("abd_log", type=Path)
    parsed_args = parser.parse_args(argv)

    with TemporaryDirectory() as temporary_directory:
        work_dir = Path(temporary_directory)
        scenario_path = work_dir / "abd_replay.xosc"
        write_scenario(read_trajectories(parsed_args.abd_log), scenario_path)
        config_path = setup_run_config(
            scenario_path,
            work_dir / "abd_replay",
            window=True,
            output_path=work_dir / "esmini.yml",
        )
        result = run_esmini(config_path)
    return result.returncode
