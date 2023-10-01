from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from perry.db.operations.agents import read_agent
from perry.agents.base import BaseAgent, AgentRegistry

from threading import Lock, Timer
from queue import PriorityQueue


class AgentManager:
    """Manage the lifetime of agent instances."""

    # TODO: Add memory management that scales with user demand. Will use singleton pattern for now
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls.reset()
        return cls._instance

    @classmethod
    def reset(cls):
        cls.agent_dict = {}
        cls.expiry_queue = PriorityQueue()
        cls.lock = Lock()
        cls._cleanup_timeout = timedelta(minutes=60)

    @classmethod
    def load_agent(self, db: Session, agent_id):
        if not isinstance(agent_id, int):
            raise ValueError("Agent ID must be an integer.")

        with self.lock:
            if agent_id in self.agent_dict:
                return self.agent_dict[agent_id]["agent"]

            db_agent = read_agent(db, agent_id)
            if not db_agent:
                raise ValueError(f"No agent found with ID {agent_id} in database.")

            agent_class = AgentRegistry().get_agent_class(db_agent.type)
            agent = agent_class(db, db_agent.config, agent_id)

            if not agent:
                raise ValueError(f"Failed to load agent with ID {agent_id}.")

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
