"""
An example showing how to create a trajector based on polyline
Also shows how to create a vehicle from start

Some features used:


- SpeedProfileAction

"""

from scenariogeneration import ScenarioGenerator, xodr, xosc

START_SPEED = [10, 20, 30]  # [km/h]
MAX_SPEED = [40, 60]  # [km/h]


class Scenario(ScenarioGenerator):
    """Scenario"""

    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.open_scenario_version = 2
        self.parameters = {}
        self.parameters["start_speed"] = [x / 3.6 for x in START_SPEED]  # unit: [m/s]
        self.parameters["max_speed"] = [x / 3.6 for x in MAX_SPEED]  # unit: [m/s]
        self.parameters["acc"] = [1, 2]
        self.parameters["decel"] = [1, 2]
        self.parameters["start_speed_time"] = [3]
        self.parameters["const_speed_time"] = [6]
        self.parameters["finishing_time"] = [3]

        self.naming = "parameter"

    def road(self, **kwargs):
        """
        road

        Returns:
            xodr.OpenDrive: The generated road network.

        """
        road = xodr.create_road(geometry=xodr.Line(5000), id=1)

        odr = xodr.OpenDrive("straight_road")
        odr.add_road(road)
        odr.adjust_roads_and_lanes()

        return odr

    def scenario(self, **kwargs):
        """
        scenario

        Returns:
            xosc.Scenario: The generated scenario.

        """
        ##################
        ### PARAMETERS ###
        ##################
        acceleration = kwargs["acc"]  # unit: [m/s²]
        deceleration = kwargs["decel"]
        acceleration_time = (kwargs["max_speed"] - kwargs["start_speed"]) / acceleration
        deceleration_time = (kwargs["max_speed"] - kwargs["start_speed"]) / deceleration
        acceleration_start = kwargs["start_speed_time"]
        const_speed_time = kwargs["const_speed_time"]
        deceleration_start = acceleration_start + acceleration_time + const_speed_time
        finishing_time = kwargs["finishing_time"]
        total_time = deceleration_start + deceleration_time + finishing_time

        ### create catalogs
        catalog = xosc.Catalog()
        catalog.add_catalog("VehicleCatalog", "../../xml/xosc/Catalogs/Vehicles")

        ### create road
        road = xosc.RoadNetwork(roadfile=self.road_file)

        ## create entities

        egoname = "Ego"
        targetname = "Target"

        entities = xosc.Entities()
        entities.add_scenario_object(egoname, xosc.CatalogReference("VehicleCatalog", "car_white"))
        entities.add_scenario_object(targetname, xosc.CatalogReference("VehicleCatalog", "car_red"))

        ### create init

        # create init
        init = xosc.Init()
        step_time = xosc.TransitionDynamics(
            xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 0
        )

        egospeed = xosc.AbsoluteSpeedAction(kwargs["start_speed"], step_time)
        egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -1, 1))
        egoactivatecontrol = xosc.ActivateControllerAction(True, True)
        init.add_init_action(egoname, egospeed)
        init.add_init_action(egoname, egostart)
        init.add_init_action(egoname, egoactivatecontrol)

        init.add_init_action(targetname, egospeed)
        init.add_init_action(targetname, egostart)

        # accelerate car to max_speed
        ego_acc_action = xosc.AbsoluteSpeedAction(
            kwargs["max_speed"],
            xosc.TransitionDynamics(
                xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, acceleration_time
            ),
        )
        ego_acc_trigger = xosc.ValueTrigger(
            "ego_acc_trigger",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(acceleration_start, xosc.Rule.greaterThan),
        )

        eventegoacc = xosc.Event("egospeedchange_acc", xosc.Priority.override)
        eventegoacc.add_action("acc_speed", ego_acc_action)
        eventegoacc.add_trigger(ego_acc_trigger)

        # decelerate car to start_speed
        ego_brake_action = xosc.AbsoluteSpeedAction(
            kwargs["start_speed"],
            xosc.TransitionDynamics(
                xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, deceleration_time
            ),
        )
        ego_brake_trigger = xosc.ValueTrigger(
            "ego_brake_trigger",
            0,
            xosc.ConditionEdge.none,
            xosc.SimulationTimeCondition(deceleration_start, xosc.Rule.greaterThan),
        )

        eventegobrake = xosc.Event("egospeedchange_brake", xosc.Priority.override)
        eventegobrake.add_action("brake_speed", ego_brake_action)
        eventegobrake.add_trigger(ego_brake_trigger)

        # create maneuvers/maneuvergroups
        ego_man = xosc.Maneuver("ego_man")
        ego_man.add_event(eventegoacc)
        ego_man.add_event(eventegobrake)

        ref_man = xosc.Maneuver("ref_man")
        ref_man.add_event(eventegoacc)
        ref_man.add_event(eventegobrake)

        ego_mangr = xosc.ManeuverGroup("ego_man_gr")
        ego_mangr.add_actor(egoname)
        ego_mangr.add_maneuver(ego_man)

        ref_mangr = xosc.ManeuverGroup("ref_man_gr")
        ref_mangr.add_actor(targetname)
        ref_mangr.add_maneuver(ref_man)

        act = xosc.Act("act")
        act.add_maneuver_group(ego_mangr)
        act.add_maneuver_group(ref_mangr)

        # create the storyboard
        sb = xosc.StoryBoard(
            init,
            stoptrigger=xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(total_time, xosc.Rule.greaterThan),
                "stop",
            ),
        )
        sb.add_act(act)

        # create and return the scenario
        sce = xosc.Scenario(
            "Speed Profile - v_i: "
            + str(kwargs["start_speed"])
            + "| v_f: "
            + str(kwargs["max_speed"]),
            "User",
            parameters=xosc.ParameterDeclarations(),
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
        )

        return sce


if __name__ == "__main__":
    sce = Scenario()

    sce.generate(".")
