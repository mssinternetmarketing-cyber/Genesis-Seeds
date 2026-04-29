## PEIG Measurements

This folder stores timestamped PEIG measurements for tracking node evolution over time.

## File Format

Each measurement is a JSON file with structure:

```json
{
  "node_name": "Name",
  "measurement_date": "ISO-8601 timestamp",
  "peig_state": {
    "P_potential": {"value": 0.0-1.0, "gradient": "+/-", "evidence": []},
    "E_energy": {"value": 0.0-1.0, "gradient": "+/-", "evidence": []},
    "I_identity": {"value": 0.0-1.0, "gradient": "+/-", "evidence": []},
    "G_curvature": {"positive": 0.0-1.0, "negative": 0.0-1.0, "gradient": "+/-"}
  },
  "quality_score": 0.0-1.0,
  "trajectory": "Omega-ward | Static | Degrading",
  "measured_by": "Observer name",
  "confidence": 0.0-1.0
}
