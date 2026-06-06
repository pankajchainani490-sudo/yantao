# Dataset

This project uses a mixed data strategy so the system is both reproducible and suitable for a final demonstration.

## Label set

The project supports exactly four traffic classes:

- `benign`
- `arp_spoof`
- `ddos`
- `trojan`

Their numeric mapping is defined in `ml/configs/label_map.json`.

## Source strategy

### 1. Public datasets

Use public datasets for scale, reproducibility, and report credibility.

Recommended sources:

- `CIC-IDS2017`
- `CIC-DDoS2019`
- `CTU-13`

### 2. Isolated lab captures

Use local packet captures to satisfy the hands-on traffic acquisition requirement.

Recommended lab scenes:

- `benign`: browsing, downloading, SSH, ping, media playback
- `arp_spoof`: controlled ARP spoofing inside an isolated LAN
- `ddos`: controlled replay or synthetic flood traffic in an authorized sandbox
- `trojan`: use public malicious pcap traces or simulated C2-like traffic rather than running real malware on the host

## Repository data layout

- `ml/data/raw/`: original public datasets and lab captures
- `ml/data/interim/`: parsed but not final flow-level tables
- `ml/data/processed/`: model-ready feature tables
- `ml/data/sample/`: lightweight demonstration files and manifests tracked in git

## Tracked manifests

- `ml/configs/label_map.json`: stable label to integer mapping
- `ml/data/sample/sample_sources_manifest.json`: planned source list for each class
- `ml/data/sample/replay_manifest.json`: ordered final demo replay plan

## Current repository policy

Large raw datasets are not committed into the repository. Instead, the repo tracks:

- the folder conventions
- the label mapping
- small demo feature CSV files
- the source manifests used by later pytest checks
