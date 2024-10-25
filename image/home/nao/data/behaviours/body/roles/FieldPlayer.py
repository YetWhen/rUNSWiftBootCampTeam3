import robot
from importlib import import_module
from util.Vector2D import Vector2D
from BehaviourTask import BehaviourTask
from body.skills.Stand import Stand
from body.skills.WalkInLine import WalkInLine
from body.skills.WalkInCircle import WalkInCircle
from body.skills.ApproachBall import ApproachBall
from util.Constants import FIELD_LENGTH, PENALTY_AREA_LENGTH, CENTER_CIRCLE_DIAMETER, LEDColour
import time
from util.FieldGeometry import (
    ENEMY_GOAL_BEHIND_CENTER,
    ball_near_our_goal,
    calculateTimeToReachBall,
    calculateTimeToReachPose,
)

from util.Timer import WallTimer
from util import LedOverride

class FieldPlayer(BehaviourTask):
    v = 50 #speed or velocity - mm/s
    r = 300 #radius - mm
    w = v/r
    timespan = 2*3.14*r/v
    start_time = time.time()
    def _initialise_sub_tasks(self):
        self._sub_tasks = {
            "Stand": Stand(self),
            "WalkInLine": WalkInLine(self),
            "WalkInCircle": WalkInCircle(self),
            "ApproachBall": ApproachBall(self),
        }

    def _reset(self):
        self._current_sub_task = "WalkInCircle"

    def _transition(self):
        '''if time.time()-self.start_time <= self.timespan:

            self._current_sub_task = "WalkInLine"
        else:
            #self._current_sub_task = "Stand"
            self._current_sub_task = "WalkInCircle"
        '''
        #self._current_sub_task = "ApproachBall"
        self._current_sub_task = "WalkInLine"

    def _tick(self):
        # Tick sub task!
        #print(self._current_sub_task)
        self._tick_sub_task()



