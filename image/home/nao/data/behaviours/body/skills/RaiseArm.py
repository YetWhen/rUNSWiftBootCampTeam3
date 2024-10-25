from BehaviourTask import BehaviourTask
from util.actioncommand import raiseArm
from util.actioncommand import crouch
from util.ObstacleAvoidance import sonar_left_obstacle, sonar_right_obstacle
import robot

class RaiseArm(BehaviourTask):
    def _tick(self):
        self.world.b_request.actions.body = raiseArm()
        
