from math import radians
from util.Global import myPos, myHeading, ballRelPos
from util.BallMovement import stopWorldPos
from BehaviourTask import BehaviourTask
from util.Constants import TOE_CENTRE_X, HIP_OFFSET, HALF_FIELD_LENGTH, HALF_FIELD_WIDTH
from util.Vector2D import Vector2D
from util.MathUtil import angleSignedDiff, angleDiff
from util.FieldGeometry import ENEMY_GOAL_BEHIND_CENTER
from util import LineUpDataReader
from body.skills.WalkStraightToPose import WalkStraightToPose
from body.skills.CircleToPose import CircleToPose
from body.skills.CircleReport import CircleReport
from body.skills.PointBall import PointBall
from body.skills.Stand import Stand
from robot import Foot
import robot
from util.ObstacleAvoidance import calculate_tangent_point
from util.Timer import Timer

# from util import LedOverride
# from util.Constants import LEDColour


# Some values for preventing task switching, near boundary values
EVADE_DISTANCE_MARGIN = 100  # mm
ANGLE_CLOSE = radians(30)  # rad
ANGLE_NOT_CLOSE = radians(40)  # rad


class WalkToBallAndReport(BehaviourTask):
    line_up_data, line_up_max_x, line_up_max_y = LineUpDataReader.readData("line_up_data.lud")
    _ArmRaised = False
    _Stabled = False

    def _initialise_sub_tasks(self):
        self._sub_tasks = {
            "Unobstructed": WalkStraightToPose(self),
            #"LineUp": LineUp(self),
            "CircleToPose": CircleToPose(self), #replace this with CircleReporting
            "CircleReport": CircleReport(self),
            "TangentialWalk": WalkStraightToPose(self),
            "Point": PointBall(self),
            "Stand": Stand(self),
        }

    def _reset(self):
        self._current_sub_task = "Unobstructed"
        self.close = False
        self.position_aligned = False  # The kick_foot's position is colinear \
        # with the kick_target and ball
        self.heading_aligned = False  # The robot is facing kick_target
        self._armTimer = Timer(timeTarget=1000000)

    def _transition(self):
        #if the first time go into the CircleReport, first time approach to the ball
        #shift to Point, to raise the arm to point to the ball
        if self._current_sub_task == "CircleReport" and not self._Stabled:
            self._current_sub_task = "Stand"
            self._Stabled = True
            self._armTimer.start()
        elif self._current_sub_task == "Stand" and self._armTimer.finished():
            self._current_sub_task = "Point"
            self._ArmRaised = True
            self._armTimer.start()
        elif self._current_sub_task == "Point" and self._armTimer.finished():
            self._current_sub_task = "CircleReport"
        
      

    # TODO: include a slow param in penalty
    def _tick(
        self,
        target=ENEMY_GOAL_BEHIND_CENTER,
        kick_foot=Foot.LEFT,
        lineup_distance=90,
        evade_distance=300,
        distance_error=50,
        heading_error=radians(10),
        use_line_up_map=False,
    ):
        my_pos = myPos()
        my_heading = myHeading()

        # Calculate where we would like to take the eventual kick from

        ball = stopWorldPos()
        kick_vector = target.minus(ball).normalise(lineup_distance)

        toe_vector = Vector2D(TOE_CENTRE_X, HIP_OFFSET * (1 if kick_foot is Foot.LEFT else -1))
        toe_vector_relative_to_me = toe_vector.clone().rotate(my_heading)
        toe_vector_relative_to_kick = toe_vector.clone().rotate(kick_vector.heading())

        toe_kick_position = ball.minus(kick_vector)
        kick_position = toe_kick_position.minus(toe_vector_relative_to_kick)

        # Calculate possible tangential paths \
        # in order to avoid hitting the ball

        toe_pos = my_pos.plus(toe_vector_relative_to_me)
        ball_vector = ball.minus(toe_pos)

        # Pick which way we'll approach the ball
        # Encourage aproaching rounding the ball goalside if it is near our goal
        goal_side_adjustment = radians(10) * (ball.y / HALF_FIELD_WIDTH) * max(0, -ball.x / HALF_FIELD_LENGTH)
        angle_ball_vec_to_kick_vec = angleSignedDiff(kick_position.minus(toe_pos).heading(), ball_vector.heading())
        direction = angle_ball_vec_to_kick_vec + goal_side_adjustment > 0
        tangent_point = calculate_tangent_point(centre=ball, radius=evade_distance, left_side=direction)

        # tangent point is None if we're within the radius of the avoidance
        # circle. In this case, just point to the ball so it doesn't cause
        # python errors
        ''' For bootsCamp most of the cases would be no tangent_point since there's no goal info'''
        if tangent_point is None:
            tangent_point = ball

        tangent_walk_final_heading = ball.minus(my_pos).heading()
        ''' in bootsCamp most of the cases this would be distance from ball to robot'''
        tangent_length = tangent_point.minus(my_pos).length()

        # Calculate some values to help decide between sub tasks
        angle_my_heading_to_kick_vector = angleSignedDiff(kick_vector.heading(), my_heading)
        angle_ball_vector_to_kick_vector = angleSignedDiff(kick_vector.heading(), ball_vector.heading())

        toe_distance = toe_kick_position.minus(toe_pos).length()
        # Transition to the appropriate sub task

        if self._current_sub_task == "CircleReport":
            # If we're far away from the ball,
            if tangent_length > evade_distance + EVADE_DISTANCE_MARGIN:
                if toe_distance < tangent_length:
                    self._current_sub_task = "Unobstructed"
                else:
                    self._current_sub_task = "TangentialWalk"

        elif self._current_sub_task == "Unobstructed":
            # If its closer to walk to tangent than directly to kick position
            if toe_distance > tangent_length:
                self._current_sub_task = "TangentialWalk"

            # If we're close,
            elif tangent_length < evade_distance:
                # If we're not facing the correct direction,
                '''which is always the case since there's no target info in this task'''
                self._current_sub_task = "CircleReport"
                #self._current_sub_task = "Stand" #debug

        elif self._current_sub_task == "TangentialWalk":
            # If its closer to walk to kick position than to a tangent
            if toe_distance < tangent_length:
                self._current_sub_task = "Unobstructed"

            # If we're close,
            elif tangent_length < evade_distance:
                # If we're not facing the correct direction,
                self._current_sub_task = "CircleReport"
                #self._current_sub_task = "Stand" #debug

        # Tick sub task
        if self._current_sub_task == "Unobstructed":
            self._tick_sub_task(final_pos=kick_position, final_heading=ball_vector.heading(), speed=1.0)
        elif self._current_sub_task == "CircleReport":
            self._tick_sub_task(
                target_radius= 300, circle_centre=ball, speed=1.0
            )
        elif self._current_sub_task == "TangentialWalk":
            self._tick_sub_task(final_pos=tangent_point, final_heading=tangent_walk_final_heading, speed=1.0)
        else:
            self._tick_sub_task()

