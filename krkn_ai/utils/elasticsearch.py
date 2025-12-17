"""
Elasticsearch integration utilities for Krkn-AI.
Handles sending run results, fitness scores, and genetic algorithm data to Elasticsearch.
"""
import json
import uuid
from typing import Dict, Optional, Any
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from krkn_ai.models.config import ElasticConfig
from krkn_ai.models.app import CommandRunResult
from krkn_ai.utils.logger import get_logger

logger = get_logger(__name__)

import numpy as np


class ElasticsearchClient:
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
        self.enabled = config.enable_elastic and config.elastic_url != ""
        
        if not self.enabled:
            logger.debug("Elasticsearch integration is disabled")
            return
        
        # Build Elasticsearch URL
        if not config.elastic_url.startswith(('http://', 'https://')):
            self.base_url = f"https://{config.elastic_url}:{config.elastic_port}"
        else:
            # URL already has protocol, check if it already has a port
            # Check if URL already contains a port (format: http://host:port or https://host:port)
            if ':' in config.elastic_url.split('://')[1].split('/')[0]:
                # URL already contains port, use as is
                self.base_url = config.elastic_url
            else:
                # URL has protocol but no port, add port
                self.base_url = f"{config.elastic_url}:{config.elastic_port}"
        
        # Setup authentication if provided
        self.auth = None
        if config.username and config.password:
            self.auth = HTTPBasicAuth(config.username, config.password)
        
        logger.info("Elasticsearch client initialized: %s", self.base_url)
    
    def _convert_to_json_serializable(self, obj: Any) -> Any:
        """
        Recursively convert numpy types and other non-JSON-serializable types to Python native types.
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON-serializable object
        """

        if isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8,
                           np.int16, np.int32, np.int64, np.uint8, np.uint16,
                           np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_json_serializable(item) for item in obj]
        else:
            return obj
    
    def test_connection(self) -> bool:
        """
        Test connection to Elasticsearch.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Elasticsearch integration is disabled")
            return False
        
        try:
            # Try to get cluster info
            url = f"{self.base_url}/_cluster/health"
            response = requests.get(
                url,
                auth=self.auth,
                verify=self.config.verify_certs,
                timeout=10
            )
            response.raise_for_status()
            health = response.json()
            logger.info("Successfully connected to Elasticsearch. Cluster status: %s", health.get('status', 'unknown'))
            return True
        except requests.exceptions.RequestException as e:
            logger.error("Failed to connect to Elasticsearch: %s", e)
            return False
    
    def _send_document(self, index: str, document: Dict[str, Any]) -> bool:
        """
        Send a document to Elasticsearch.
        
        Args:
            index: Elasticsearch index name
            document: Document to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        url = f"{self.base_url}/{index}/_doc"
        
        # Convert numpy types to JSON-serializable types
        document = self._convert_to_json_serializable(document)
        
        try:
            response = requests.post(
                url,
                json=document,
                auth=self.auth,
                verify=self.config.verify_certs,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Successfully sent document to Elasticsearch index: %s (ID: %s)", 
                       index, result.get('_id', 'unknown'))
            return True
        except requests.exceptions.RequestException as e:
            logger.warning("Failed to send document to Elasticsearch index %s: %s", index, e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.warning("Elasticsearch error details: %s", error_detail)
                except:
                    logger.warning("Elasticsearch error response: %s", e.response.text)
            return False
    
    def send_scenario_result(self, result: CommandRunResult, run_uuid: str, config_data: Dict[str, Any]) -> bool:
        """
        Send a scenario run result to Elasticsearch.
        
        Args:
            result: CommandRunResult containing scenario execution details
            run_uuid: Unique identifier for the entire Krkn-AI run
            config_data: Genetic algorithm configuration data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        # Helper function to convert datetime to ISO string
        def to_iso_string(dt):
            if isinstance(dt, datetime):
                return dt.isoformat()
            elif hasattr(dt, 'isoformat'):
                return dt.isoformat()
            else:
                return str(dt)
        
        # Calculate duration
        try:
            if isinstance(result.start_time, datetime) and isinstance(result.end_time, datetime):
                duration_seconds = (result.end_time - result.start_time).total_seconds()
            else:
                duration_seconds = None
        except (TypeError, AttributeError):
            duration_seconds = None
        
        document = {
            "@timestamp": to_iso_string(result.start_time),
            "run_uuid": run_uuid,
            "generation_id": result.generation_id,
            "scenario_id": result.scenario_id,
            "scenario": {
                "name": result.scenario.name,  # BaseScenario always has name (base.py:23)
                "type": type(result.scenario).__name__,
            },
            "execution": {
                "command": result.cmd,
                "returncode": result.returncode,
                "start_time": to_iso_string(result.start_time),
                "end_time": to_iso_string(result.end_time),
                "duration_seconds": duration_seconds,
            },
            "fitness": {
                "overall_score": result.fitness_result.fitness_score,
                "health_check_failure_score": result.fitness_result.health_check_failure_score,
                "health_check_response_time_score": result.fitness_result.health_check_response_time_score,
                "krkn_failure_score": result.fitness_result.krkn_failure_score,
                "slo_scores": [
                    {
                        "id": score.id,
                        "fitness_score": score.fitness_score,
                        "weighted_score": score.weighted_score
                    }
                    for score in result.fitness_result.scores
                ]
            },
            "health_checks": {
                "results": {
                    app_name: [
                        {
                            "name": check.name,
                            "timestamp": check.timestamp,
                            "response_time": check.response_time,
                            "status_code": check.status_code,
                            "success": check.success,
                            "error": check.error
                        }
                        for check in checks
                    ]
                    for app_name, checks in result.health_check_results.items()
                }
            },
            "genetic_algorithm": {
                "generations": config_data.get("generations"),  # Optional[int] in ConfigFile
                "population_size": config_data.get("population_size"),  # int in ConfigFile
                "mutation_rate": config_data.get("mutation_rate"),  # float in ConfigFile
                "scenario_mutation_rate": config_data.get("scenario_mutation_rate"),  # float in ConfigFile
                "crossover_rate": config_data.get("crossover_rate"),  # float in ConfigFile
                "composition_rate": config_data.get("composition_rate"),  # float in ConfigFile
                "population_injection_rate": config_data.get("population_injection_rate"),  # float in ConfigFile
                "population_injection_size": config_data.get("population_injection_size"),  # int in ConfigFile
            },
            "fitness_function": {
                "query": config_data.get("fitness_function", {}).get("query"),  # Union[str, None] in FitnessFunction
                "type": config_data.get("fitness_function", {}).get("type"),  # FitnessFunctionType in FitnessFunction
                "include_krkn_failure": config_data.get("fitness_function", {}).get("include_krkn_failure"),  # bool in FitnessFunction
                "include_health_check_failure": config_data.get("fitness_function", {}).get("include_health_check_failure"),  # bool in FitnessFunction
                "include_health_check_response_time": config_data.get("fitness_function", {}).get("include_health_check_response_time"),  # bool in FitnessFunction
                "items": config_data.get("fitness_function", {}).get("items", [])  # List[FitnessFunctionItem] in FitnessFunction
            }
        }
        
        # Add scenario parameters if available
        if hasattr(result.scenario, 'parameters'):
            document["scenario"]["parameters"] = [
                {
                    "name": param.get_name() if hasattr(param, 'get_name') else str(type(param).__name__),
                    "value": str(param.get_value() if hasattr(param, 'get_value') else param)
                }
                for param in result.scenario.parameters
            ]
        
        return self._send_document(self.config.results_index, document)
    
    def send_run_summary(self, run_uuid: str, config_data: Dict[str, Any], 
                         best_results: list, total_generations: int) -> bool:
        """
        Send a summary of the entire Krkn-AI run to Elasticsearch.
        
        Args:
            run_uuid: Unique identifier for the run
            config_data: Genetic algorithm configuration data
            best_results: List of best results from each generation
            total_generations: Total number of generations completed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        # Calculate summary statistics
        if best_results:
            best_fitness = max(r.fitness_result.fitness_score for r in best_results)
            worst_fitness = min(r.fitness_result.fitness_score for r in best_results)
            avg_fitness = sum(r.fitness_result.fitness_score for r in best_results) / len(best_results)
        else:
            best_fitness = worst_fitness = avg_fitness = 0.0
        
        document = {
            "@timestamp": datetime.now().isoformat(),
            "run_uuid": run_uuid,
            "run_type": "summary",
            "summary": {
                "total_generations": total_generations,
                "best_fitness_score": best_fitness,
                "worst_fitness_score": worst_fitness,
                "average_fitness_score": avg_fitness,
                "total_scenarios_run": len(best_results) if best_results else 0
            },
            "genetic_algorithm": {
                "generations": config_data.get("generations"),
                "population_size": config_data.get("population_size"),
                "mutation_rate": config_data.get("mutation_rate"),
                "scenario_mutation_rate": config_data.get("scenario_mutation_rate"),
                "crossover_rate": config_data.get("crossover_rate"),
                "composition_rate": config_data.get("composition_rate"),
                "population_injection_rate": config_data.get("population_injection_rate"),
                "population_injection_size": config_data.get("population_injection_size"),
            },
            "fitness_function": {
                "query": config_data.get("fitness_function", {}).get("query"),
                "type": config_data.get("fitness_function", {}).get("type"),
                "include_krkn_failure": config_data.get("fitness_function", {}).get("include_krkn_failure"),
                "include_health_check_failure": config_data.get("fitness_function", {}).get("include_health_check_failure"),
                "include_health_check_response_time": config_data.get("fitness_function", {}).get("include_health_check_response_time"),
                "items": config_data.get("fitness_function", {}).get("items", [])
            }
        }
        
        return self._send_document(self.config.results_index, document)

