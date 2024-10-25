from BehaviourTask import BehaviourTask
from body.skills.Walk import Walk

class WalkInCircle(BehaviourTask):
    """
    description:
    a skill to walk in a circle
    In: speed (mm/s), radius (mm)
    """
    #most of the members are called from body/BehaviorTask
    #it will set current (default) subtask as "walk", not walking yet.
    def _initialise_sub_tasks(self):
        self._sub_tasks = {"Walk": Walk(self)}
    #return to default
    def _reset(self):
        self._current_sub_task = "Walk"

    def _tick(self):
        #todo: calculate the forward (tangential speed) and turn (omega)
        #from input
        v = 50 #speed or velocity - mm/s
        r = 300 #radius - mm
        w = v/r
        self._tick_sub_task(forward=v, turn=w)