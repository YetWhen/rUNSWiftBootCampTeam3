import robot
from importlib import import_module
from util.Vector2D import Vector2D
from BehaviourTask import BehaviourTask
from util.TeamStatus import get_teammate_pos
from body.skills.Stand import Stand
from body.skills.P2PPass import P2PPass
from util.Constants import FIELD_LENGTH, PENALTY_AREA_LENGTH, CENTER_CIRCLE_DIAMETER, LEDColour

from util.FieldGeometry import (
    ENEMY_GOAL_BEHIND_CENTER,
    ball_near_our_goal,
    calculateTimeToReachBall,
    calculateTimeToReachPose,
)

from util.Timer import WallTimer
from util import LedOverride

class FieldPlayer(BehaviourTask):
    def _initialise_sub_tasks(self):
        self._sub_tasks = {
            "Stand": Stand(self),
            "P2PPass": P2PPass(self),
        }

    def _reset(self):
        self._current_sub_task = "P2PPass"

    def _transition(self):
        pass

    def _tick(self):
        # Tick sub task!
        teammate_pos = get_teammate_pos(1)
        self._tick_sub_task(pass_target=teammate_pos)



