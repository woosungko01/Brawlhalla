from game.local_vs_match import LocalVsMatch


class RealVsMatch(LocalVsMatch):
    #실제 게임에서는 hitbox 등 제거
    def __init__(self, screen_w: int, screen_h: int, p1_char: str, p2_char: str) -> None:
        super().__init__(screen_w, screen_h, p1_char, p2_char)

        self.show_hud = False
        self.show_hitboxes = False
        self.show_fighter_labels = False
        self.minimal_ui = True
        self.opening_text = "None"
        self.allow_debug_toggle = False