# Covariance Shapes (KiDS BandPower EE+nE Bridge)

## Shape of Processed Covariance

- **EE block**: (100, 100)
- **nE block**: (100, 100)
- **EE+nE combined**: (200, 200)

The full 300×300 bandpower covariance exists but only the first 200×200
(EE+nE) is used in the v1.2 diagnostic bridge. The nn block (rows 200–299)
remains unavailable locally — see `phase5_nn_sourcing/`.

## Normalization

Covariance matrices are stored in the standardized format produced by
`convert_kids_bandpower_to_standard_csv.py`. Units and normalization
conventions follow the KiDS-1000 bandpower release.

## Validation

- The first 200×200 block has been validated against the EE+nE bridge.
- Shape consistency: (200, 200) for the combined diagnostic block.
- No off-diagonal truncation anomalies detected in the EE+nE region.
