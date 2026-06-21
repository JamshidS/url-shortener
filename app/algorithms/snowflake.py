import time

from fastapi import Request

class SnowflakeIDGenerator:
    def __init__(self, machine_id: int, worker_id: int):
        self.datacenter_id = machine_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def next_id(self) -> int:
        timestamp = self._timestamp()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id.")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits for sequence
            if self.sequence == 0:
                while timestamp <= self.last_timestamp:
                    timestamp = self._timestamp()
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        id = ((timestamp << 22) | (self.datacenter_id << 17) | (self.worker_id << 12) | self.sequence)
        return id
    


def get_snowflake_id_generator(request: Request) -> SnowflakeIDGenerator:
    return request.app.state.snowflake_id_generator
