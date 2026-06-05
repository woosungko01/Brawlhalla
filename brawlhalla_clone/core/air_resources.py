# core/air_resources.py
#
# 브롤할라식 공중 자원 관리.
# bool 하나가 아니라 count 기반으로 관리해야
# 나중에 recovery, total 제한 등을 쉽게 붙일 수 있음.


class AirResources:
    """
    공중에서 소모하는 자원 카운터.

    jumps_used          : 공중에서 사용한 점프 횟수
    recoveries_used     : (예약) recovery move 사용 횟수
    total_air_rises_used: jump + recovery 합산 — 나중에 총량 제한용
    """

    __slots__ = ("jumps_used", "recoveries_used", "total_air_rises_used")

    def __init__(self) -> None:
        self.jumps_used:           int = 0
        self.recoveries_used:      int = 0
        self.total_air_rises_used: int = 0

    def reset(self) -> None:
        """착지 또는 벽 접촉 시 호출해서 자원 회복"""
        self.jumps_used           = 0
        self.recoveries_used      = 0
        self.total_air_rises_used = 0

    def consume_jump(self) -> None:
        self.jumps_used           += 1
        self.total_air_rises_used += 1

    def consume_recovery(self) -> None:
        self.recoveries_used      += 1
        self.total_air_rises_used += 1
