import json

import polars as pl
from evtx import PyEvtxParser


def parse_evtx(file_path):
    """Converts .evtx file to Polars DataFrame."""
    records = []

    try:
        parser = PyEvtxParser(file_path)

        for record in parser.records_json():
            if record is None:
                continue

            if isinstance(record, Exception):
                continue

            try:
                data = record.get("data") if isinstance(record, dict) else record

                if isinstance(data, str):
                    data = json.loads(data)

                if not isinstance(data, dict):
                    continue

                event_root = data.get("Event", {})
                system = event_root.get("System", {})
                event_data = event_root.get("EventData", {})

                row = {
                    "timestamp": system.get("TimeCreated", {})
                    .get("#attributes", {})
                    .get("SystemTime"),
                    "event_id": system.get("EventID"),
                    "computer": system.get("Computer"),
                    "channel": system.get("Channel"),
                    "level": system.get("Level"),
                    "raw_json": json.dumps(data, default=str),
                    "details": str(event_data) if event_data else "No details",
                }
                records.append(row)

            except Exception:
                continue

        if not records:
            return pl.DataFrame()

        df = pl.DataFrame(records)

        df = df.with_columns(
            pl.col("timestamp").str.to_datetime(strict=False, time_zone="UTC")
        )

        return df.sort("timestamp", descending=True)

    except Exception as e:
        print(f"Error parsing log: {e}")
        return pl.DataFrame()
