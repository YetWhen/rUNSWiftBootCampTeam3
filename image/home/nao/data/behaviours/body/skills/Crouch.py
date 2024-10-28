from BehaviourTask import BehaviourTask
import robot
from util.actioncommand import crouch
from util.ObstacleAvoidance import sonar_left_obstacle, sonar_right_obstacle


class Crouch(BehaviourTask):

    def _tick(self, power = 0.4):
        self.world.b_request.actions.body = crouch(power=power)