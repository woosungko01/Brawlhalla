# entities/dummy_fighter.py

from entities.fighter import Fighter


class DummyFighter(Fighter):
    def __init__(self, x: float, y: float, character) -> None:
        super().__init__(x, y, character)
        self.width = 52
        self.height = 72

        # 피격 반응
        self.hitstun_timer = 0.0

        # 훈련장용 더미 옵션
        self.is_training_dummy = True