"""
Generate a synthetic coastal water-level time series.

The dataset is designed for an engineering-style portfolio project:
- semi-diurnal tide
- seasonal water-level variation
- random measurement noise
- several storm-surge events
- optional long-term sea-level rise trend

The data is synthetic and should not be used for real design decisions.
However, the workflow is transferable to measured tide-gauge data.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_water_level(
    start: str = "2022-01-01",
    end: str = "2023-12-31 23:00",
    freq: str = "1h",
    seed: int = 42,
    output_path: str | Path = "data/synthetic_water_level.csv",
) -> pd.DataFrame:
    """
    Generate synthetic hourly coastal water-level data.

    Parameters
    ----------
    start:
        Start datetime.
    end:
        End datetime.
    freq:
        Time step frequency.
    seed:
        Random seed for reproducibility.
    output_path:
        CSV path where the generated dataset will be saved.

    Returns
    -------
    pandas.DataFrame
        DataFrame with timestamp and water-level components.
    """

    rng = np.random.default_rng(seed)
    time = pd.date_range(start=start, end=end, freq=freq)
    n = len(time)

    # Time vectors
    hours = np.arange(n)
    days = hours / 24.0

    # Semi-diurnal tide, approximate M2 period ~12.42 hours
    tide = 0.75 * np.sin(2 * np.pi * hours / 12.42)

    # Smaller diurnal inequality component
    diurnal = 0.18 * np.sin(2 * np.pi * hours / 24.0 + 0.8)

    # Seasonal water-level variation
    seasonal = 0.12 * np.sin(2 * np.pi * days / 365.25 - 0.6)

    # Long-term sea-level rise trend, exaggerated slightly for visibility over 2 years
    # 6 mm/year converted to metres over the generated time axis
    trend = (0.006 / 365.25) * days

    # Random measurement/environmental noise
    noise = rng.normal(loc=0.0, scale=0.08, size=n)

    # Storm surge events represented as Gaussian-shaped pulses
    surge = np.zeros(n)

    storm_events = [
        # center date, peak surge [m], duration scale [hours]
        ("2022-02-18 06:00", 0.95, 18),
        ("2022-10-29 18:00", 1.15, 24),
        ("2023-01-14 12:00", 0.90, 20),
        ("2023-09-22 03:00", 1.25, 30),
        ("2023-12-05 09:00", 1.05, 22),
    ]

    for center_date, amplitude, width_hours in storm_events:
        center_index = np.argmin(np.abs(time - pd.Timestamp(center_date)))
        surge += amplitude * np.exp(-0.5 * ((hours - center_index) / width_hours) ** 2)

    water_level_m = tide + diurnal + seasonal + trend + noise + surge

    df = pd.DataFrame(
        {
            "timestamp": time,
            "water_level_m": water_level_m,
            "tide_m": tide + diurnal,
            "seasonal_m": seasonal,
            "trend_m": trend,
            "surge_m": surge,
            "noise_m": noise,
        }
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "data" / "synthetic_water_level.csv"

    df = generate_synthetic_water_level(output_path=output)

    print(f"Synthetic dataset saved to: {output}")
    print(f"Rows: {len(df):,}")
    print(df.head())
