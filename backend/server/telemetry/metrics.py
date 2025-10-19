from prometheus_client import Counter, Histogram

http_requests_total = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"])
llm_tokens_total = Counter("llm_tokens_total", "Tokens used", ["provider"])
request_latency = Histogram("request_latency_seconds", "Request latency", ["route"])