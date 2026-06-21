# entities/dummy_fighter.py

from entities.fighter import Fighter


class DummyFighter(Fighter):
    #로봇 설정 (샌드백)
    def __init__(self, x: float, y: float, character) -> None:
        super().__init__(x, y, character)
        self.is_training_dummy = True
        self.is_controllable = False