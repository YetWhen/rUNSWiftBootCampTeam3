from BehaviourTask import BehaviourTask
from body.skills.Walk import Walk
from util.CircularMotion import tangent_heading, distance_from_r1_to_r2_delta_theta
from util.Global import myPos, myHeading
from util.Vector2D import Vector2D
from math import pi, radians
from util.MathUtil import normalisedTheta, angleSignedDiff
from util.ObstacleAvoidance import walk_vec_with_avoidance

import robot


class CircleReport(BehaviourTask):

    """
    Description:
    A skill associated with walking to a specific position and heading,
    around a revolutionary centre. The movement is defined by the following
    constraints:
    - Revolutionary radius increases at a constant rate (to achieve final
      radius)
    - Robot's heading changes at a constant rate (to achieve final heading)
    The resulting motion ends up being a spiral shape, around the centre.
    NOTE:
    - Ensure any changes are well-tested, as this is a complicated skill,
    - Relies on the walk velocities being accurately executed by motion.
    """

    # This walk speed is for calculations and not passed to the walk function. mm/s
    WALK_SPEED = 100 #300

    HEADING_CLOSE = radians(3)
    DISTANCE_CLOSE = 30

    def _initialise_sub_tasks(self):
        self._sub_tasks = {"Walk": Walk(self)}

    def _reset(self):
        self._current_sub_task = "Walk"

    '''
    def _transition(self):
        #try this first, if there's no duplicate, keep that
        #if duplicate, add a timer and track the timer and _begun_speaking flag, move to WalkToBallAndReport
        s = "I found the ball"
        robot.say(s)
    '''
    def _tick(
        self,final_position=Vector2D(-1000, 0), final_heading=radians(0), target_radius=400, circle_centre=Vector2D(0, 0), speed=0.5
    ):
        # 1. Calculate some useful information first
        centre_to_my_pos = myPos().minus(circle_centre)
        current_radius = centre_to_my_pos.length()
        final_radius = target_radius

        # 2. Calculate time needed to circle around NO NEED, NO STOP


        # 3. Calculate turn rate 
        turn_diff = angleSignedDiff(final_heading, myHeading())
        if abs(turn_diff) < self.HEADING_CLOSE:
            turn_rate = 0
        else:
            # If we are more than 90 degrees off to our final heading,
            # Turn in the direction that allows us to keep the circle centre
            # in sight.
            # This is useful as objects we want to face and observe are
            # usually at the centre of the avoidance circle.
            if turn_diff > abs(radians(90)):
                to_centre_heading = circle_centre.minus(myPos()).heading()
                angle_to_face_centre = angleSignedDiff(to_centre_heading, myHeading())
                if angle_to_face_centre > 0:
                    clockwise_turn = False
                else:
                    clockwise_turn = True

                # ensure we're spinning in the direction specified,
                # unless one way is a lot closer
                if clockwise_turn:
                    turn_diff -= 2 * pi
                elif not clockwise_turn:
                    turn_diff += 2 * pi

            # calculate turn rate
            time_needed_to_circle = 1.0 #assuming s
            turn_rate = turn_diff / time_needed_to_circle

        # 4. Calculate circular move vector, using current radius
        circle_clockwise = True
        circular_move_vector = Vector2D(self.WALK_SPEED, 0).rotate(
            tangent_heading(myPos(), circle_centre, circle_clockwise)
        )
        circular_move_vector.rotate(-myHeading())

        # 5. Calculate radius change move vector, to increase radius at
        #    constant rate
        if abs(final_radius - current_radius) < self.DISTANCE_CLOSE:
            radius_move_vector = Vector2D(0, 0)
        else: 
            radius_change_rate = 30 #----------------------assume mm/s, 3cm/s
            radius_move_vector = Vector2D(radius_change_rate, 0).rotate(centre_to_my_pos.heading())  # noqa
            radius_move_vector.rotate(-myHeading())

        # 6. Sum the two move vectors, and send!
        move_vector = circular_move_vector.plus(radius_move_vector)

        # 7. Use some avoidance, if necessary
        move_vector = walk_vec_with_avoidance(move_vector)

        #turn_rate = move_vector.x / current_radius
        s = "I found the ball"
        robot.say(s)
        self._tick_sub_task(move_vector.x, move_vector.y, turn_rate, speed=speed)