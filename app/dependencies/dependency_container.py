from logging import Logger

from app.core.settings import GraphDBConfig
from app.dependencies.fetchers import FetchersContainer
from app.dependencies.services.http_client import HttpClient
from app.dependencies.services.logger import LogLevel, get_logger
from app.dependencies.services.neo4j.neo4j_connection import Neo4jConfig, Neo4jConnection
from app.dependencies.services.neo4j.repository import GraphRepositoryContainer


class DependencyContainer:
    _log_level: LogLevel = "INFO"
    _neo4j_config: Neo4jConfig | None = None

    _logger: Logger | None = None
    _neo4j_connection: Neo4jConnection | None = None
    _graph_repository_container: GraphRepositoryContainer | None = None
    _http_client: HttpClient | None = None
    _fetchers_container: FetchersContainer | None = None

    @classmethod
    def configure_logger(cls, log_level: LogLevel) -> None:
        cls._log_level = log_level

    @classmethod
    def configure_neo4j(cls, graph_db_config: GraphDBConfig) -> None:
        cls._neo4j_config = Neo4jConfig(
            url=graph_db_config.graph_db_url,
            user=graph_db_config.graph_db_user,
            password=graph_db_config.graph_db_password,
            db_name=graph_db_config.graph_db_name,
        )

    @property
    def logger(self) -> Logger:
        if not self._logger:
            self._logger = get_logger(self._log_level)
        return self._logger

    @property
    def graph_repository_container(self) -> GraphRepositoryContainer:
        if not self._graph_repository_container:
            self._graph_repository_container = GraphRepositoryContainer(
                connection=self.neo4j_connection,
                logger=self.logger,
            )
        return self._graph_repository_container

    @property
    def neo4j_connection(self) -> Neo4jConnection:
        if not self._neo4j_connection:

            if not self._neo4j_config:
                msg = "'neo4j' is not configured! Call 'DependencyContainer.configure_neo4j' method."
                raise ValueError(msg)

            self._neo4j_connection = Neo4jConnection(neo4j_config=self._neo4j_config, logger=self.logger)
        return self._neo4j_connection

    @property
    def fetchers_container(self) -> FetchersContainer:
        if not self._fetchers_container:
            self._fetchers_container = FetchersContainer(
                http_client=self.http_client,  # type: ignore
                logger=self.logger,
            )
        return self._fetchers_container

    @property
    def http_client(self) -> HttpClient:
        if not self._http_client:
            self._http_client = HttpClient()
        return self._http_client
