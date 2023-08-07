import time
from spellchecker import SpellChecker
class Tracker:

    def __init__(self):
        self._backspace = 0
        self._num_pauses=0
        self._total_time_pauses=0
        self._last_timestamp=round(time.time())
        self._has_paused= False
        self._prev_diff_time=0
        self._has_typed= False
        self._spell=SpellChecker()

    def reset(self):
        self._backspace=0
        self._has_paused=0
        self._last_timestamp=round(time.time())
        self._has_typed= False
    def get_n_backspace(self):
        return self._backspace

    def _check_pauses(self):
        current_timestamp= round(time.time())
        diff_time= current_timestamp-self._last_timestamp
        duration= 3
        if diff_time > duration:
            self._total_time_pauses+=(diff_time-self._prev_diff_time)
            self._prev_diff_time=diff_time
            if not self._has_paused:
                self._has_paused=True
                self._num_pauses+=1
        else:
            self._prev_diff_time=0
            self._last_timestamp=round(time.time())
            self._has_paused = False

    def key_pressed(self,event):
        self._has_typed=True
        print(event.keysym)
        self._check_pauses()
        if event.keysym== 'BackSpace':
            self._backspace+=1

    def get_n_pauses(self):
        return {'Number of pauses': self._num_pauses, 'Total time of pause':self._total_time_pauses}

    def user_has_typed(self):
        return self._has_typed

    def get_n_typos(self, words):
        misspelled = self._spell.unknown(words)
        return len(misspelled)
