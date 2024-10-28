import math

from robot import Foot
from BehaviourTask import BehaviourTask
from body.skills.ApproachBall import ApproachBall
from body.skills.Kick import Kick
from body.skills.Stand import Stand
from util.FieldGeometry import ENEMY_GOAL_BEHIND_CENTER

LINEUP_DISTANCE_KICK = 100  # mm


class P2PPass(BehaviourTask):
    def _initialise_sub_tasks(self):
        self._sub_tasks = {"ApproachBall": ApproachBall(self), 
                            "Kick": Kick(self),
                            "Stand": Stand(self),
                            }

    def _reset(self):
        self._current_sub_task = "ApproachBall"
        self.has_finished_kick = False
        self._mode = "Kick"

    def _transition(self):
        if self._current_sub_task == "ApproachBall":
            self.has_finished_kick = False
            if (
                self._sub_tasks[self._current_sub_task].close
                and self._sub_tasks[self._current_sub_task].position_aligned
                and self._sub_tasks[self._current_sub_task].heading_aligned  # noqa
            ):
                self._current_sub_task = self._mode

        elif self._current_sub_task == "Kick":
            if self._sub_tasks[self._current_sub_task].is_finished:
                self._current_sub_task = "Stand"
                self.has_finished_kick = True

    def _tick(self, pass_target=None, can_abort=True, lineup_dist=100, kickhard=False):
        (
            mode,
            target,
            foot,
            hard,
            heading_error,
            distance_error,
            lineup_distance,
            use_line_up_map,
        ) = self._decide_shoot_parameters(pass_target, lineup_dist, kickhard)

        self._mode = mode

        # Write some debug info
        debug_info = self.world.b_request.behaviourDebugInfo
        debug_info.haveBallManoeuvreTarget = True
        debug_info.ballManoeuvreTargetX = target.x
        debug_info.ballManoeuvreTargetY = target.y
        debug_info.ballManoeuvreHeadingError = heading_error
        debug_info.ballManoeuvreType = "KICK" if mode == "Kick" else "DRIBBLE"
        debug_info.ballManoeuvreHard = hard

        if self._current_sub_task == "ApproachBall":
            self._tick_sub_task(
                target=target,
                kick_foot=foot,
                heading_error=heading_error,
                lineup_distance=lineup_distance,
                use_line_up_map=use_line_up_map,
            )

        elif self._current_sub_task == "Kick":
            self._tick_sub_task(
                target=target,
                foot=foot,
                hard=hard,
                heading_error=heading_error,
                can_abort=can_abort,
                extra_stable=True,  # currently, we only pass when stability and precision is required over execution time  # noqa
            )

    def _decide_shoot_parameters(self, pass_target, lineup_dist, kickhard):
        # @ijnek: TODO implement logic here
        if pass_target is not None:
            mode = "Kick"
            target = pass_target
            foot = Foot.LEFT
            hard = kickhard
            heading_error = math.radians(10)
            distance_error = 30
            lineup_distance = lineup_dist  # LINEUP_DISTANCE_KICK
            use_line_up_map = True

        else:
            mode = "Kick"
            target = ENEMY_GOAL_BEHIND_CENTER
            foot = Foot.LEFT
            hard = True
            heading_error = math.radians(10)
            distance_error = 30
            lineup_distance = LINEUP_DISTANCE_KICK
            use_line_up_map = True

        return (mode, target, foot, hard, heading_error, distance_error, lineup_distance, use_line_up_map)