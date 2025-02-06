from dataclasses import dataclass
from logging import Logger

from neo4j import AsyncGraphDatabase


@dataclass
class Neo4jConfig:
    url: str
    user: str
    password: str
    db_name: str


class Neo4jConnection:
    def __init__(self, neo4j_config: Neo4jConfig, logger: Logger) -> None:
        self.driver = AsyncGraphDatabase.driver(
            neo4j_config.url,
            auth=(neo4j_config.user, neo4j_config.password),
        )
        self.logger = logger
        self.db_name = neo4j_config.db_name

    async def close(self) -> None:
        if self.driver is not None:
            await self.driver.close()

    async def query(self, query: str, parameters: dict[str, str] | None = None) -> list[dict] | None:
        session = None

        try:
            session = self.driver.session(database=self.db_name) if self.db_name is not None else self.driver.session()

            async_result = await session.run(query, parameters=parameters)
            result = [res.data() async for res in async_result]
        except Exception:
            self.logger.exception("Query '%s' failed:", query)
        else:
            return result
        finally:
            if session is not None:
                await session.close()
