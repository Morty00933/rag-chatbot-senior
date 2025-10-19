param(
  [string]$Model = "qwen2.5:3b"
)

docker compose up -d qdrant redis ollama
Start-Sleep -Seconds 2
try {
  Invoke-RestMethod -Method Post -Uri "http://localhost:11434/api/pull" -Body (@{name=$Model} | ConvertTo-Json)
} catch {
  Write-Host "Skip pull model: $Model (maybe already present)"
}
docker compose up --build -d api worker frontend prometheus grafana loki
