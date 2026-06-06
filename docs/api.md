# API Overview

Base path: `/api/v1`

## Health

- `GET /health`

## Prediction

- `POST /predict`

Example payload:

```json
{
  "source_ip": "10.10.0.200",
  "destination_ip": "172.16.0.99",
  "source_port": 43111,
  "destination_port": 80,
  "packet_len_mean": 132.6,
  "packet_len_max": 526.0,
  "packet_len_min": 60.0,
  "packet_len_std": 45.0,
  "packets_per_sec": 1490.4,
  "bytes_per_sec": 194880.0,
  "flow_duration": 3.1,
  "model_name": "random_forest"
}
```

## Dashboard

- `GET /dashboard/summary`
- `GET /dashboard/trends`
- `GET /dashboard/top-sources`

## Alerts

- `GET /alerts`

## Blacklist

- `GET /blacklist`
- `POST /blacklist`
- `DELETE /blacklist/{id}`

## Replay

- `POST /replay/start`
- `GET /replay/status`

## Metrics and settings

- `GET /metrics/summary`
- `GET /settings`
