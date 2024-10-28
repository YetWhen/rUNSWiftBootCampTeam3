import robot
from importlib import import_module
from util.Vector2D import Vector2D
import time
from body.skills.Crouch import Crouch
from body.skills.RaiseArm import RaiseArm
from math import floor
from BehaviourTask import BehaviourTask
from body.skills.WalkInCircle import WalkInCircle
from body.skills.Stand import Stand
from body.skills.Kick import Kick
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
            "Crouch": Crouch(self),
            "RaiseArm": RaiseArm(self),
            "WalkInCircle": WalkInCircle(self),
            "Kick": Kick(self)
        }

    def _reset(self):
        self._time = time.time()
        self._current_sub_task = "Stand"

    def _transition(self):
        if (time.time() - self._time > 30):
            pass
        if (floor(time.time() - self._time) % 5 == 0):
            robot.say("Attention Attention, this is an evacuation drill")
            self._current_sub_task = "WalkInCircle"
        elif(floor(time.time() - self._time) % 5 == 2):
            self._current_sub_task = "RaiseArm"
    

    def _tick(self):
        # Tick sub task!
        self._tick_sub_task()


