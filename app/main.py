import http.server
import socketserver
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

PORT = 8000

# Major AWS Regions to monitor
REGIONS = [
    {"code": "us-east-1", "name": "N. Virginia"},
    {"code": "us-west-2", "name": "Oregon"},
    {"code": "eu-west-1", "name": "Ireland"},
    {"code": "ap-southeast-1", "name": "Singapore"},
    {"code": "ap-northeast-1", "name": "Tokyo"},
    {"code": "sa-east-1", "name": "São Paulo"},
]

class RawAWSHealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(base_dir, 'static', 'index.html'), 'rb') as f:
                self.wfile.write(f.read())
            return
            
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = self.fetch_raw_aws_data()
            self.wfile.write(json.dumps(data).encode())
            return
        
        elif self.path == "/ping":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return
            
        else:
            return super().do_GET()

    def fetch_rss_item(self, region_code):
        """Fetches the actual latest raw RSS item from AWS for EC2."""
        url = f"https://status.aws.amazon.com/rss/ec2-{region_code}.rss"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                root = ET.fromstring(content)
                items = root.findall('.//item')
                
                if not items:
                    return {
                        "status": "Healthy",
                        "title": "Service is operating normally",
                        "description": "AWS reports no issues for this region.",
                        "pubDate": datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
                    }
                
                # Get the absolute raw data from the first item
                latest = items[0]
                return {
                    "status": "Issue Reported" if "operating normally" not in latest.find('title').text.lower() else "Healthy",
                    "title": latest.find('title').text,
                    "description": latest.find('description').text,
                    "pubDate": latest.find('pubDate').text if latest.find('pubDate') is not None else "N/A"
                }
        except Exception as e:
            return {
                "status": "Unknown",
                "title": f"Feed Unavailable for {region_code}",
                "description": str(e),
                "pubDate": "N/A"
            }

    def fetch_raw_aws_data(self):
        regions_health = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_region = {executor.submit(self.fetch_rss_item, r["code"]): r for r in REGIONS}
            
            for future in future_to_region:
                r = future_to_region[future]
                raw_item = future.result()
                
                regions_health.append({
                    "region_code": r["code"],
                    "region_name": r["name"],
                    "raw": raw_item,
                    "last_updated": datetime.now().isoformat()
                })

        return {
            "timestamp": datetime.now().isoformat(),
            "regions": regions_health,
            "mode": "PURE-LIVE-FEED"
        }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    socketserver.TCPServer.allow_reuse_address = True
    env_port = int(os.environ.get("PORT", PORT))
    
    with socketserver.TCPServer(("0.0.0.0", env_port), RawAWSHealthHandler) as httpd:
        print(f"PURE LIVE AWS Health Monitor started at http://localhost:{env_port}")
        httpd.serve_forever()
