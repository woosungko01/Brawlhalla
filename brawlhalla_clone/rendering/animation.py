# rendering/animation.py

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AnimationClip:
    name: str
    frame_count: int
    frame_time: float
    loop: bool = True


class AnimationPlayer:
    def __init__(self) -> None:
        self.current: AnimationClip | None = None
        self.current_name: str | None = None
        self.time: float = 0.0
        self.frame_index: int = 0

    def play(self, clip: AnimationClip, restart: bool = False) -> None:
        if self.current_name == clip.name and not restart:
            return

        self.current = clip
        self.current_name = clip.name
        self.time = 0.0
        self.frame_index = 0

    def update(self, dt: float) -> None:
        if self.current is None:
            return

        if self.current.frame_count <= 1 or self.current.frame_time <= 0.0:
            self.frame_index = 0
            return

        self.time += dt

        total_duration = self.current.frame_count * self.current.frame_time
        if self.current.loop:
            while self.time >= total_duration:
                self.time -= total_duration
        else:
            self.time = min(self.time, total_duration - 0.0001)

        self.frame_index = int(self.time / self.current.frame_time)
        if self.frame_index >= self.current.frame_count:
            self.frame_index = self.current.frame_count - 1