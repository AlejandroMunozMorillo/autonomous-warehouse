import os

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision  # type: ignore
    from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False


class InfluxWriter:
    """Writes metrics to InfluxDB if available."""
    
    def __init__(self):
        """Initialize InfluxDB writer."""
        self.enabled = False
        
        if not INFLUX_AVAILABLE:
            print("[INFO] InfluxDB client not installed")
            return
        
        influx_url = os.getenv('INFLUXDB_URL')
        if not influx_url:
            print("[INFO] INFLUXDB_URL not set - telemetry disabled")
            return
        
        try:
            self.client = InfluxDBClient(
                url=influx_url,
                token=os.getenv('INFLUXDB_TOKEN', 'default-token'),
                org=os.getenv('INFLUXDB_ORG', 'warehouse-org')
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.bucket = os.getenv('INFLUXDB_BUCKET', 'inventory-metrics')
            self.enabled = True
            print(f"[INFO] InfluxDB telemetry enabled → {self.bucket}")
        except Exception as e:
            print(f"[WARN] InfluxDB connection failed: {e}")
            self.enabled = False
    
    def write_daily_metrics(self, scenario: str, day: int, metrics: dict):
        """Write daily KPIs to InfluxDB."""
        if not self.enabled:
            return
        
        try:
            point = Point("daily_metrics") \
                .tag("scenario", scenario) \
                .field("day", day) \
                .field("fill_rate", float(metrics.get('fill_rate', 0.0))) \
                .field("lost_sales", int(metrics.get('lost_sales', 0))) \
                .field("stock_total", int(metrics.get('stock_total', 0))) \
                .field("budget_spent", float(metrics.get('budget_spent', 0.0))) \
                .field("revenue", float(metrics.get('revenue', 0.0)))
            
            self.write_api.write(bucket=self.bucket, record=point)
        except Exception as e:
            print(f"[WARN] Failed to write daily metrics: {e}")
    
    def write_sku_metrics(self, scenario: str, day: int, sku: str, 
                          stock: int, demand: int, sales: int):
        """Write per-SKU metrics to InfluxDB."""
        if not self.enabled:
            return
        
        try:
            point = Point("sku_metrics") \
                .tag("scenario", scenario) \
                .tag("sku", sku) \
                .field("day", day) \
                .field("stock", int(stock)) \
                .field("demand", int(demand)) \
                .field("sales", int(sales)) \
                .field("lost", int(demand - sales))
            
            self.write_api.write(bucket=self.bucket, record=point)
        except Exception as e:
            print(f"[WARN] Failed to write SKU metrics: {e}")
    
    def close(self):
        """Close InfluxDB connection."""
        if self.enabled and hasattr(self, 'client'):
            try:
                self.client.close()
                print("[INFO] InfluxDB connection closed")
            except Exception as e:
                print(f"[WARN] Error closing InfluxDB: {e}")
