from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from perry.db.operations.agents import read_agent
from perry.agents.base import BaseAgent

from threading import Lock, Timer
from queue import PriorityQueue


class AgentManager:
    def __init__(self, db_session: Session):
        """Manage previously created agents in memory."""
        self.agent_dict = {}
        self.expiry_queue = PriorityQueue()
        self.lock = Lock()
        self._db_session = db_session
        self._cleanup_timeout = timedelta(minutes=60)

    def load_agent(self, agent_id):
        with self.lock:
            if agent_id in self.agent_dict:
                return self.agent_dict[agent_id]["agent"]

            if not read_agent(self._db_session, agent_id):
                raise ValueError(f"No agent found with ID {agent_id} in database.")

            agent = BaseAgent.load(self._db_session, agent_id)

            agent.busy = False

            expiry_time = datetime.utcnow() + self._cleanup_timeout
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
            if expiry_time <= datetime.utcnow():
                self._remove_agent(agent_id)
            else:
                self.expiry_queue.put((expiry_time, agent_id))
                break

        Timer(60, self._cleanup).start()

    def start(self):
        self._cleanup()
