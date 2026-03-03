from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Incident(BaseModel):
    id: str
    service: str
    status: str
    description: str
    startTime: datetime

class RegionHealth(BaseModel):
    region_code: str
    region_name: str
    status: str # healthy, degraded, outage
    score: float
    latency_ms: float
    last_updated: datetime

class GlobalHealth(BaseModel):
    timestamp: datetime
    regions: List[RegionHealth]
    active_incidents: List[Incident]
