"""Prometheus-style metrics tracking."""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import Request


class MetricsCollector:
    """Simple metrics collector for API requests and ETL runs."""
    
    def __init__(self):
        self.request_count: Dict[str, int] = defaultdict(int)
        self.request_duration: Dict[str, list] = defaultdict(list)
        self.etl_runs: int = 0
        self.etl_failures: int = 0
        self.etl_last_run: float = 0
        
    def record_request(self, method: str, path: str, duration: float, status_code: int):
        """Record an API request."""
        endpoint = f"{method} {path}"
        self.request_count[endpoint] += 1
        self.request_duration[endpoint].append(duration)
        
    def record_etl_run(self, success: bool = True):
        """Record an ETL run."""
        self.etl_runs += 1
        if not success:
            self.etl_failures += 1
        self.etl_last_run = time.time()
        
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = [
            "# HELP api_requests_total Total number of API requests",
            "# TYPE api_requests_total counter",
        ]
        
        for endpoint, count in self.request_count.items():
            lines.append(f'api_requests_total{{endpoint="{endpoint}"}} {count}')
        
        lines.extend([
            "",
            "# HELP api_request_duration_seconds API request duration",
            "# TYPE api_request_duration_seconds summary",
        ])
        
        for endpoint, durations in self.request_duration.items():
            if durations:
                # Calculate percentiles
                sorted_durations = sorted(durations)
                count = len(sorted_durations)
                p50 = sorted_durations[int(count * 0.5)] if count > 0 else 0
                p95 = sorted_durations[int(count * 0.95)] if count > 0 else 0
                p99 = sorted_durations[int(count * 0.99)] if count > 0 else 0
                total = sum(sorted_durations)
                
                lines.append(f'api_request_duration_seconds_count{{endpoint="{endpoint}"}} {count}')
                lines.append(f'api_request_duration_seconds_sum{{endpoint="{endpoint}"}} {total:.3f}')
                lines.append(f'api_request_duration_seconds{{endpoint="{endpoint}",quantile="0.5"}} {p50:.3f}')
                lines.append(f'api_request_duration_seconds{{endpoint="{endpoint}",quantile="0.95"}} {p95:.3f}')
                lines.append(f'api_request_duration_seconds{{endpoint="{endpoint}",quantile="0.99"}} {p99:.3f}')
        
        lines.extend([
            "",
            "# HELP etl_runs_total Total number of ETL runs",
            "# TYPE etl_runs_total counter",
            f"etl_runs_total {self.etl_runs}",
            "",
            "# HELP etl_failures_total Total number of ETL failures",
            "# TYPE etl_failures_total counter",
            f"etl_failures_total {self.etl_failures}",
            "",
            "# HELP etl_last_run_timestamp Unix timestamp of last ETL run",
            "# TYPE etl_last_run_timestamp gauge",
            f"etl_last_run_timestamp {self.etl_last_run}",
        ])
        
        return "\n".join(lines) + "\n"


# Global metrics collector
metrics = MetricsCollector()


async def metrics_middleware(request: Request, call_next):
    """Middleware to track request metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    metrics.record_request(
        request.method,
        request.url.path,
        duration,
        response.status_code
    )
    
    return response
