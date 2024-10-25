from BehaviourTask import BehaviourTask
from body.skills.Walk import Walk
from body.skills.Stand import Stand
from util.Vector2D import Vector2D
from util.Global import myPos, myHeading, ballRelPos

class WalkInLine(BehaviourTask):
    """
    description:
    a skill to walk in a line
    """

    #most of the members are called from body/BehaviorTask
    #it will set current (default) subtask as "walk", not walking yet.
    def _initialise_sub_tasks(self):
        self._sub_tasks = {"Walk": Walk(self),
                           "Stand": Stand(self),}
    #return to default
    def _reset(self):
        self._current_sub_task = "Stand"
    
    def _tick(self):
        mapPos = ballRelPos().scale(0.1)
        #print("ballRelPos:")
        #print(mapPos)
        #self._tick_sub_task(forward=50)
        #self._tick_sub_task()

    