# AWS Global Health Monitor

**Live Demo**: [https://aws-global-health-monitor.onrender.com](https://aws-global-health-monitor.onrender.com)

A real-time dashboard that monitors the health and availability of AWS services across major global regions. It provides reliability scores and incident tracking to ensure infrastructure transparency.

## Features
- **Global Overview**: Real-time status for 6 major AWS regions.
- **Reliability Scoring**: Per-region scores based on latency and service status.
- **Incident Feed**: Centralized view of active service degradations and outages.
- **Modern Dashboard**: Responsive UI with status pulse indicators and high-contrast visuals.
- **Docker-Ready**: Optimized for containerized deployment.

## Scoring Formula
Health Score (0-100) = `100.0 - Latency Penalty - Status Penalty`
- **Latency Penalty**: 0.1 per ms over 50ms.
- **Status Penalty**: 30 for Degraded, 80 for Outage.

## Setup

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker
```bash
docker build -t aws-health-monitor .
docker run -p 8000:8000 aws-health-monitor
```

## 💡 Inspiration
This project is a reference implementation exploring concepts related to 
multi-cloud reliability engineering. The author holds USPTO patent 
applications in this domain (US 19/325,718 and US 19/344,864).

## Health Check
- Added /ping endpoint for automated health monitoring.
