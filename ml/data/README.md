# Data Layout

This directory stores all traffic datasets used by the project.

## Directory roles

- `raw/`: immutable source material, including downloaded public datasets and isolated lab packet captures.
- `interim/`: normalized but not yet model-ready tables, such as parsed flow CSV exports.
- `processed/`: final feature tables used for training and evaluation.
- `sample/`: lightweight demonstration assets and metadata safe to keep in the repository.

## Naming guidance

- Keep public datasets under `raw/public/<dataset_name>/`.
- Keep isolated lab captures under `raw/lab/<attack_type>/`.
- Keep replay-oriented demo files under `sample/replay/`.
- Keep schema and source manifests close to the data root so pytest can validate them.

## Label policy

The project uses exactly four labels:

- `benign`
- `arp_spoof`
- `ddos`
- `trojan`

Their numeric mapping is defined in `ml/configs/label_map.json` and must remain stable across feature extraction, training, inference, and replay.
