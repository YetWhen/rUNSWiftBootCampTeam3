from BehaviourTask import BehaviourTask
from head.HeadFixedYawAndPitch import HeadFixedYawAndPitch
from math import radians
from util.Global import ballHeading, ballDistance

class HeadCentre(BehaviourTask):
    YAW = 0
    PITCH = 0
    CLOSE_DISTANCE = 800.0
    BEHIND_ANGLE = radians(60)

    def _initialise_sub_tasks(self):
        self._sub_tasks = {"HeadFixedYawAndPitch": HeadFixedYawAndPitch(self)}

    def _reset(self):
        self.PITCH_BEHIND = radians(0)
        self.PITCH_CLOSE = radians(19 + self.world.blackboard.kinematics.parameters.cameraPitchBottom)
        self.PITCH_FAR = radians(19*2 + self.world.blackboard.kinematics.parameters.cameraPitchBottom)
        self._current_sub_task = "HeadFixedYawAndPitch"

    def _tick(self):
        self.YAW = ballHeading()
        self.PITCH = self.PITCH_CLOSE if ballDistance() < self.CLOSE_DISTANCE else self.PITCH_FAR
        self.PITCH = self.PITCH_BEHIND if abs(yaw) > self.BEHIND_ANGLE else self.PITCH
        self._tick_sub_task(self.YAW, self.PITCH)
