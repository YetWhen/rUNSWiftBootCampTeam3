from util.actioncommand import raiseArm

from BehaviourTask import BehaviourTask


class PointBall(BehaviourTask):
    def _tick(self):
        self.world.b_request.actions.body = raiseArm()