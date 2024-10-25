from BehaviourTask import BehaviourTask
from body.skills.Walk import Walk
import math
import time


class WalkInCircle(BehaviourTask):
    def _initialise_sub_tasks(self):
        self._sub_tasks = {"WalkInCircle": Walk(self)}
        self._time = time.time()
    
    def _reset(self):
        
        self._current_sub_task = "WalkInCircle"
    
    def _tick(self):
        self._tick_sub_task(turn=3.14)