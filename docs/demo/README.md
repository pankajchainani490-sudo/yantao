# Demo

This document defines the recommended project demonstration flow.

## Demo goals

- Show the system can classify benign and malicious traffic
- Show the model effect and feature importance
- Show blacklist creation and management
- Show replay-based step-by-step presentation

## Recommended demo sequence

### 1. Dashboard overview

- Open the homepage dashboard
- Explain total predictions, malicious ratio, open alerts, and blacklist count
- Point out top malicious sources and latest alerts

### 2. Detection workflow

- Open the `Detection` page
- Keep the default DDoS-style feature sample
- Click `Run Prediction`
- Explain:
  - source/destination endpoints
  - packet length statistics
  - packets per second
  - confidence and risk level
  - top feature importance items

### 3. Blacklist mechanism

- Open the `Blacklist` page
- Explain auto-blacklist records seeded from repeated alerts
- Add one manual blacklist entry
- Delete that entry to show management capability

### 4. Replay demo

- Open the `Replay` page
- Trigger stage 1 to show benign baseline
- Trigger stage 2 or 3 to show ARP spoof or DDoS progression
- Explain how replay is useful on Ubuntu or classroom networks where live capture is unstable

### 5. Metrics explanation

- Open the `Metrics` page
- Compare decision tree and random forest
- Explain confusion matrix and feature importance

## Presenter notes

- Prefer replay mode over live capture in formal defense settings
- If the audience asks about online capture, explain that the architecture supports it but the demo uses controlled replay for stability
- Emphasize that blacklisting is driven by model output plus threshold rules, not by one-shot prediction only
