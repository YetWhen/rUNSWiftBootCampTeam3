from BehaviourTask import BehaviourTask
from head.HeadFixedYawAndPitch import HeadFixedYawAndPitch
from util.Timer import Timer, WallTimer
from util.Vector2D import Vector2D
from util.Global import myPos, myHeading, ballRelPos, ballDistance
from math import radians, atan


class HeadTrackBall(BehaviourTask):

    """
    Description:
    A Headskill associated with localising.
    A wide scan is performed to cover a lot of area.
    """

    SEQUENCE = [
        radians(30),
        radians(-30),
        radians(-60),
        radians(-115),
        radians(-20),
        radians(20),
        radians(60),
        radians(115),
    ]

    SEQUENCE_FORWARD = [radians(-30), radians(30), radians(60), radians(20), radians(-20), radians(-60)]

    STARE_SECONDS = 0.7
    BEHIND_ANGLE = radians(60)
    NARROW_PERIOD = 5  # seconds

    def _initialise_sub_tasks(self):
        self._sub_tasks = {"FixedYawAndPitch": HeadFixedYawAndPitch(self)}

    def _reset(self):
        self.PITCH_BEHIND = radians(19)
        self.PITCH = radians(19 + self.world.blackboard.kinematics.parameters.cameraPitchBottom)
        self._current_sub_task = "FixedYawAndPitch"
        self._timer = Timer(self.STARE_SECONDS * 1000000)  # convert to micro-seconds  # noqa
        self._yaw_aim = 0
        self._sequence_counter = 0
        self._currently_moving = True
        self._timer_since_start = WallTimer()
        self._yaw_step = radians(1.5)  # Step size for smooth yaw movement
        self._pitch_step = radians(0.5)  # Step size for smooth pitch movement

    def _tick(self):
        self._sequence = self._choose_sequence()

        target_yaw = self._sequence[self._sequence_counter]
        ballPos = ballRelPos()
        target_yaw = atan(ballPos.y/ballPos.x)
        target_yaw = 0.5
        target_pitch = 0
        print("ballRelPos:")
        print(ballPos)
        print("ball Angle:")
        print(target_yaw)
        target_pitch = self._calculate_target_pitch(target_yaw)

        if abs(self._yaw_aim - target_yaw) < abs(self._yaw_step):
            self._yaw_aim = target_yaw
            self._increment_sequence_counter()
            target_yaw = self._sequence[self._sequence_counter]  # Get the next target immediately

        if self._yaw_aim < target_yaw:
            self._yaw_aim += self._yaw_step
        else:
            self._yaw_aim -= self._yaw_step

        if abs(self.PITCH - target_pitch) < abs(self._pitch_step):
            self.PITCH = target_pitch
        else:
            if self.PITCH < target_pitch:
                self.PITCH += self._pitch_step
            else:
                self.PITCH -= self._pitch_step

        self._tick_sub_task(yaw=self._yaw_aim, pitch=self.PITCH, yaw_speed=0.8, pitch_speed=0.2)

    def _calculate_target_pitch(self, target_yaw):
        if abs(target_yaw) <= self.BEHIND_ANGLE:
            return radians(19 + self.world.blackboard.kinematics.parameters.cameraPitchBottom)
        else:
            return radians(19)

    def _increment_sequence_counter(self):
        self._sequence_counter += 1
        if self._sequence_counter >= len(self._sequence):
            self._sequence_counter = 0

    # Don't allow robot to look back if robot is walking forwards, or backwards
    def _choose_sequence(self):
        if self.world.b_request.actions.body.forward == 0:
            return self.SEQUENCE
        else:
            return self.SEQUENCE_FORWARD
