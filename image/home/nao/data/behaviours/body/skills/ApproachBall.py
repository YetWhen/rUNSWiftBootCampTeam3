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
from body.skills.LineUp import LineUp
from robot import Foot
from util.ObstacleAvoidance import calculate_tangent_point

# from util import LedOverride
# from util.Constants import LEDColour


# Some values for preventing task switching, near boundary values
EVADE_DISTANCE_MARGIN = 100  # mm
ANGLE_CLOSE = radians(30)  # rad
ANGLE_NOT_CLOSE = radians(40)  # rad


class ApproachBall(BehaviourTask):
    line_up_data, line_up_max_x, line_up_max_y = LineUpDataReader.readData("line_up_data.lud")

    def _initialise_sub_tasks(self):
        self._sub_tasks = {
            "Unobstructed": WalkStraightToPose(self),
            "LineUp": LineUp(self),
            "CircleToPose": CircleToPose(self),
            "TangentialWalk": WalkStraightToPose(self),
        }

    def _reset(self):
        self._current_sub_task = "Unobstructed"

        self.close = False
        self.position_aligned = False  # The kick_foot's position is colinear \
        # with the kick_target and ball
        self.heading_aligned = False  # The robot is facing kick_target

    # TODO: include a slow param in penalty
    def _tick(
        self,
        target=ENEMY_GOAL_BEHIND_CENTER,
        kick_foot=Foot.LEFT,
        lineup_distance=90,
        evade_distance=200,
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
        if tangent_point is None:
            tangent_point = ball

        tangent_walk_final_heading = ball.minus(my_pos).heading()
        tangent_length = tangent_point.minus(my_pos).length()

        # Calculate some values to help decide between sub tasks
        angle_my_heading_to_kick_vector = angleSignedDiff(kick_vector.heading(), my_heading)
        angle_ball_vector_to_kick_vector = angleSignedDiff(kick_vector.heading(), ball_vector.heading())

        toe_distance = toe_kick_position.minus(toe_pos).length()
        # Transition to the appropriate sub task

        if self._current_sub_task == "LineUp":
            # If we're far away from ball,
            if tangent_length > evade_distance + EVADE_DISTANCE_MARGIN:
                if toe_distance < tangent_length:
                    self._current_sub_task = "Unobstructed"
                else:
                    self._current_sub_task = "TangentialWalk"

            # If we're not facing the correct direction,
            elif (
                abs(angle_my_heading_to_kick_vector) > ANGLE_NOT_CLOSE
                or abs(angle_ball_vector_to_kick_vector) > ANGLE_NOT_CLOSE
            ):
                self._current_sub_task = "CircleToPose"

        elif self._current_sub_task == "CircleToPose":
            # If we're far away from the ball,
            if tangent_length > evade_distance + EVADE_DISTANCE_MARGIN:
                if toe_distance < tangent_length:
                    self._current_sub_task = "Unobstructed"
                else:
                    self._current_sub_task = "TangentialWalk"

            # If we're facing the correct direction,
            elif (
                abs(angle_my_heading_to_kick_vector) < ANGLE_CLOSE
                and abs(angle_ball_vector_to_kick_vector) < ANGLE_CLOSE
            ):
                self._current_sub_task = "LineUp"

        elif self._current_sub_task == "Unobstructed":
            # If its closer to walk to tangent than directly to kick position
            if toe_distance > tangent_length:
                self._current_sub_task = "TangentialWalk"

            # If we're close,
            elif tangent_length < evade_distance:
                # If we're facing the correct direction,
                if (
                    abs(angle_my_heading_to_kick_vector) < ANGLE_CLOSE
                    and abs(angle_ball_vector_to_kick_vector) < ANGLE_CLOSE
                ):
                    self._current_sub_task = "LineUp"

                # If we're not facing the correct direction,
                else:
                    self._current_sub_task = "CircleToPose"

        elif self._current_sub_task == "TangentialWalk":
            # If its closer to walk to kick position than to a tangent
            if toe_distance < tangent_length:
                self._current_sub_task = "Unobstructed"

            # If we're close,
            elif tangent_length < evade_distance:
                # If we're facing the correct direction,
                if (
                    abs(angle_my_heading_to_kick_vector) < ANGLE_CLOSE
                    and abs(angle_ball_vector_to_kick_vector) < ANGLE_CLOSE
                ):
                    self._current_sub_task = "LineUp"

                # If we're not facing the correct direction,
                else:
                    self._current_sub_task = "CircleToPose"

        # Tick sub task
        if self._current_sub_task == "Unobstructed":
            self._tick_sub_task(final_pos=kick_position, final_heading=ball_vector.heading(), speed=1.0)
        elif self._current_sub_task == "LineUp":
            self._tick_sub_task(
                rel_theta=angle_my_heading_to_kick_vector, kick_vector=kick_vector, kick_position=kick_position
            )

            # Notify others we're about to kick
            self.world.b_request.behaviourSharedData.kickNotification = True
        elif self._current_sub_task == "CircleToPose":
            self._tick_sub_task(
                circle_centre=ball, final_heading=kick_vector.heading(), final_position=kick_position, speed=1.0
            )
        elif self._current_sub_task == "TangentialWalk":
            self._tick_sub_task(final_pos=tangent_point, final_heading=tangent_walk_final_heading, speed=1.0)
        else:
            self._tick_sub_task()

        # Update some flags for parent tasks to check if the robot is lined up
        if use_line_up_map:
            # divide ballRelPos by 10 to get map x and y positions
            mapPos = ballRelPos().scale(0.1)
            print("ballRelPos: ")
            print(ballRelPos())
            #robot.say(ballRelPos())
            # If foot is right,then invert y sign to match the map coordinates
            if kick_foot is Foot.RIGHT:
                mapPos.y = -1 * mapPos.y

            if mapPos.x < 0 or mapPos.x >= self.line_up_max_x or mapPos.y < 0 or mapPos.y >= self.line_up_max_y:
                self.close = False
                self.position_aligned = False
            elif self.line_up_data[int(mapPos.x)][int(mapPos.y)] in (1, 2):
                self.close = True
                self.position_aligned = True
            else:
                self.close = False
                self.position_aligned = False
        else:
            self.close = toe_distance < distance_error
            self.position_aligned = angleDiff(ball_vector.heading(), kick_vector.heading()) < heading_error

        self.heading_aligned = abs(angle_my_heading_to_kick_vector) < heading_error
