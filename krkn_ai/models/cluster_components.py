from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator

class Container(BaseModel):
    name: str

class Pod(BaseModel):
    name: str
    labels: Dict[str, str] = {}
    containers: List[Container] = []

class PVC(BaseModel):
    name: str
    labels: Dict[str, str] = {}
    current_usage_percentage: Optional[float] = None

class ServicePort(BaseModel):
    port: int
    target_port: Optional[Union[int, str]] = None
    protocol: str = "TCP"


class Service(BaseModel):
    name: str
    labels: Dict[str, str] = {}
    ports: List[ServicePort] = []


class VMI(BaseModel):
    name: str

class Namespace(BaseModel):
    name: str
    pods: List[Pod] = []
    services: List[Service] = []
    pvcs: List[PVC] = []
    vmis: List[VMI] = []

class Node(BaseModel):
    name: str
    labels: Dict[str, str] = {}
    free_cpu: float = 0
    free_mem: float = 0
    interfaces: List[str] = []
    taints: List[str] = []


class ClusterComponents(BaseModel):
    namespaces: List[Namespace] = []
    nodes: List[Node] = []
