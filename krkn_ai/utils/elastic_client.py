"""
Elasticsearch integration utilities for Krkn-AI.
Handles sending run results, fitness scores, and genetic algorithm data to Elasticsearch.
"""
import logging
from krkn_ai.models.config import ElasticConfig
from krkn_ai.models.app import CommandRunResult
from krkn_ai.utils.logger import get_logger

from krkn_lib.elastic.krkn_elastic import KrknElastic

logger = get_logger(__name__)


class ElasticSearchClient:
    """
    Client for sending Krkn-AI data to Elasticsearch.
    """
    
    def __init__(self, config: ElasticConfig):
        """
        Initialize Elasticsearch client.
        
        Args:
            config: Elasticsearch configuration
        """
        self.config = config

        # Hack to prevent any logging from KrknElastic client
        null_logger = logging.getLogger('null')
        null_logger.addHandler(logging.NullHandler())

        self.client = None
        if self.config.enable:
            try:
                self.client = KrknElastic(
                    safe_logger=null_logger,
                    elastic_url=self.config.server,
                    elastic_port=self.config.port,
                    username=self.config.username,
                    password=self.config.password,
                    verify_certs=self.config.verify_certs
                )
                self.__test_connection()
                logger.info("Elasticsearch client initialized: %s:%s", self.config.server, self.config.port)
            except Exception as e:
                logger.error("Failed to initialize Elasticsearch client: %s", e)
                logger.warning("Skipping Elasticsearch indexing")
                self.client = None
        else:
            logger.info("Elasticsearch indexing is disabled")
    
    def __test_connection(self) -> bool:
        es_info = self.client.es.info()
        return es_info is not None and 'version' in es_info
