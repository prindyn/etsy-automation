from app.core.config import settings

broker_url = settings.REDIS_URL
# result_backend = settings.REDIS_URL

# === Task Settings ===
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# === Worker Settings ===
worker_concurrency = 1  # prevent concurrent Google requests
task_acks_late = True  # ensures task won't be lost if worker crashes
task_reject_on_worker_lost = True

# === Retry Settings ===
task_default_retry_delay = 60  # seconds
task_max_retries = 3

# === Rate Limiting (optional per task too) ===
# Set globally or use @task(rate_limit="1/m") decorator
# rate_limit = '1/s'

# === Timezone ===
timezone = "UTC"
enable_utc = True
