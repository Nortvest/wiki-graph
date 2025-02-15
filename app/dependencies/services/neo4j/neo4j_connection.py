from dataclasses import dataclass
from logging import Logger

from neo4j import AsyncDriver, AsyncGraphDatabase


@dataclass
class Neo4jConfig:
    url: str
    user: str
    password: str
    db_name: str


class Neo4jConnection:
    _driver: AsyncDriver | None = None

    def __init__(self, neo4j_config: Neo4jConfig, logger: Logger) -> None:
        self.neo4j_config = neo4j_config
        self.logger = logger
        self.db_name = neo4j_config.db_name

    @property
    def driver(self) -> AsyncDriver:
        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(
                self.neo4j_config.url,
                auth=(self.neo4j_config.user, self.neo4j_config.password),
            )
        return self._driver

    async def close(self) -> None:
        if self.driver is not None:
            await self.driver.close()

    async def query(self, query: str, parameters: dict[str, str] | None = None) -> list[dict]:
        session = None

        try:
            session = self.driver.session(database=self.db_name) if self.db_name is not None else self.driver.session()

            async_result = await session.run(query, parameters=parameters)
            result = [res.data() async for res in async_result]
        except Exception:
            self.logger.exception("Query '%s' failed. Params: %s", query, parameters)
            raise
        else:
            return result
        finally:
            if session is not None:
                await session.close()
