from perry.db.operations.agents import (
    create_agent,
    delete_agent,
    read_agent,
    update_agent,
)
from perry.db.session import DatabaseSessionManager as DSM
from perry.agents.base import BaseAgent

from threading import Lock, Timer
from queue import PriorityQueue
import time


class AgentManager:
    def __init__(self):
        self.agent_dict = {}
        self.expiry_queue = PriorityQueue()
        self.lock = Lock()

    def load_agent(self, agent_id):
        with self.lock:
            if agent_id in self.agent_dict:
                return self.agent_dict[agent_id]["agent"]

            if not read_agent(DSM.get_db_session(), agent_id):
                raise ValueError(f"No agent found with ID {agent_id} in database.")

            agent = BaseAgent.load(DSM.get_db_session(), agent_id)

            agent.busy = False

            expiry_time = time.time() + 600
            self.agent_dict[agent_id] = {"agent": agent, "expiry_time": expiry_time}

            self.expiry_queue.put((expiry_time, agent_id))

            return agent

    def _remove_agent(self, agent_id):
        with self.lock:
            if (
                agent_id in self.agent_dict
                and not self.agent_dict[agent_id]["agent"].busy
            ):
                del self.agent_dict[agent_id]

    def _cleanup(self):
        while not self.expiry_queue.empty():
            expiry_time, agent_id = self.expiry_queue.get()
            if expiry_time <= time.time():
                self._remove_agent(agent_id)
            else:
                self.expiry_queue.put((expiry_time, agent_id))
                break

        Timer(60, self._cleanup).start()

    def start(self):
        self._cleanup()
