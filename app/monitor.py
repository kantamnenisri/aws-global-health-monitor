import random
from datetime import datetime
from typing import List
from .models import RegionHealth, Incident, GlobalHealth

REGIONS = [
    {"code": "us-east-1", "name": "N. Virginia"},
    {"code": "us-west-2", "name": "Oregon"},
    {"code": "eu-west-1", "name": "Ireland"},
    {"code": "ap-southeast-1", "name": "Singapore"},
    {"code": "ap-northeast-1", "name": "Tokyo"},
    {"code": "sa-east-1", "name": "São Paulo"},
]

def calculate_region_score(latency: float, status: str) -> float:
    base_score = 100.0
    
    # Latency penalty: 0.1 per ms over 50ms
    latency_penalty = max(0, (latency - 50) * 0.1)
    
    # Status penalty
    status_penalty = 0
    if status == "degraded":
        status_penalty = 30
    elif status == "outage":
        status_penalty = 80
        
    return max(0.0, base_score - latency_penalty - status_penalty)

async def get_global_health() -> GlobalHealth:
    regions_health = []
    active_incidents = []
    
    for r in REGIONS:
        # Simulate realistic latency (random for demo)
        latency = random.uniform(20.0, 150.0)
        
        # Randomly simulate some degradation for variety
        status = "healthy"
        roll = random.random()
        if roll > 0.95:
            status = "outage"
        elif roll > 0.85:
            status = "degraded"
            
        score = calculate_region_score(latency, status)
        
        regions_health.append(RegionHealth(
            region_code=r["code"],
            region_name=r["name"],
            status=status,
            score=round(score, 1),
            latency_ms=round(latency, 2),
            last_updated=datetime.now()
        ))
        
        if status != "healthy":
            active_incidents.append(Incident(
                id=f"INC-{random.randint(1000, 9999)}",
                service="EC2" if roll > 0.9 else "Lambda",
                status=status.upper(),
                description=f"Issue detected in {r['name']} affecting core networking services.",
                startTime=datetime.now()
            ))
            
    return GlobalHealth(
        timestamp=datetime.now(),
        regions=regions_health,
        active_incidents=active_incidents
    )
