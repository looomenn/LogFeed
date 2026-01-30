import ast
import json
import textwrap

import streamlit as st


def load_css():
    """Injects custom CSS to style the timeline and remove default Streamlit padding."""
    st.markdown(
        """
    <style>
        /* 1. Remove Top Padding / Whitespace */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            margin-top: 0rem !important;
        }

        header {visibility: hidden;}

        /* 2. Global Fonts */
        body, .stMarkdown {
            font-family: 'Source Sans Pro', sans-serif;
        }

        /* 3. Timeline Layout */
        .timeline-row {
            display: flex;
            gap: 15px;
            padding-bottom: 0px;
            position: relative;
        }

        .timeline-time {
            min-width: 70px;
            text-align: right;
            font-size: 0.8rem;
            color: #888;
            padding-top: 2px;
            font-variant-numeric: tabular-nums;
        }

        .timeline-divider {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 20px;
        }

        .timeline-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-top: 5px;
            z-index: 2;
            box-shadow: 0 0 0 2px #0e1117;
        }

        .timeline-line {
            width: 2px;
            background-color: #333;
            flex-grow: 1;
            margin-top: -5px;
            min-height: 50px;
            z-index: 1;
        }

        .timeline-card {
            flex-grow: 1;
            background-color: #1a1c23;
            border: 1px solid #2d303d;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .timeline-card:hover {
            border-color: #4f5466;
            background-color: #232631;
            transform: translateY(-1px);
        }

        .detail-tag {
            display: inline-block;
            padding: 2px 8px;
            margin: 2px 4px 2px 0;
            background: #2d303d;
            color: #d1d5db;
            border-radius: 12px;
            font-size: 0.75rem;
            border: 1px solid #3f445b;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .event-title {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 0.3px;
        }

        .event-id-badge {
            font-size: 0.75rem;
            background: #2d2d2d;
            padding: 2px 6px;
            border-radius: 4px;
            color: #aaa;
            font-family: monospace;
            border: 1px solid #3e3e3e;
        }

        .card-body {
            font-size: 0.85rem;
            color: #b0b0b0;
            line-height: 1.4;
            word-break: break-all;
        }

        /* Severity Colors */
        .status-red { background-color: #ef4444; }
        .status-orange { background-color: #f59e0b; }
        .status-blue { background-color: #3b82f6; }
        .status-grey { background-color: #6b7280; }

        .border-red { border-left: 3px solid #ef4444; }
        .border-orange { border-left: 3px solid #f59e0b; }
        .border-blue { border-left: 3px solid #3b82f6; }
        .border-grey { border-left: 3px solid #6b7280; }

    </style>
    """,
        unsafe_allow_html=True,
    )


def get_severity_class(level):
    """Maps Event Level to a CSS class suffix."""
    try:
        lvl = int(level)
    except (ValueError, TypeError):
        lvl = 0

    if lvl == 1 or lvl == 2:
        return "red"
    if lvl == 3:
        return "orange"
    if lvl == 4:
        return "blue"
    return "grey"


def clean_event_id(raw_id):
    """Extracts a clean Event ID string from complex XML structures."""
    try:
        if isinstance(raw_id, dict):
            return str(raw_id.get("#text", "Unknown"))

        if isinstance(raw_id, str) and raw_id.strip().startswith("{"):
            try:
                parsed = ast.literal_eval(raw_id)
                if isinstance(parsed, dict):
                    return str(parsed.get("#text", raw_id))
            except (ValueError, SyntaxError):
                pass

        return str(raw_id)
    # Changed from Exception to specific errors that might occur during string conversion/access
    except (AttributeError, KeyError, TypeError):
        return str(raw_id)


def format_event_data(details_str):
    """Formats the JSON details string into a readable tag-based string."""
    try:
        # Note: Using replace single quotes for JSON is risky but kept per original logic
        valid_json = details_str.replace("'", '"')
        data = json.loads(valid_json)

        if isinstance(data, dict):
            html_tags = ""
            for k, v in list(data.items())[:6]:
                if v and v != "Unavailable":
                    html_tags += f'<span class="detail-tag"><b>{k}:</b> {v}</span> '
            return html_tags if html_tags else details_str[:200]
    # Changed bare except to catch specific JSON/Decoding errors
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

    return f'<span class="card-body-text">{details_str[:250]}</span>'


def render_event_card(row):
    """Renders a single event log card using HTML/CSS."""

    ts_obj = row["timestamp"]
    time_str = ts_obj.strftime("%H:%M:%S")
    date_tooltip = ts_obj.strftime("%Y-%m-%d")

    eid = clean_event_id(row["event_id"])
    provider = row.get("channel", "System")

    try:
        raw = json.loads(row["raw_json"])
        sys = raw.get("Event", {}).get("System", {})

        prov_data = sys.get("Provider", {})
        if isinstance(prov_data, dict):
            provider = prov_data.get("#attributes", {}).get("Name", provider)
        elif isinstance(prov_data, str):
            provider = prov_data
    # Changed from Exception to JSON/Key/Type errors
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    color_suffix = get_severity_class(row["level"])
    details_preview = format_event_data(row["details"])

    html = textwrap.dedent(
        f"""
    <div class="timeline-row" title="{date_tooltip}">
        <div class="timeline-time">{time_str}</div>
        <div class="timeline-divider">
            <div class="timeline-dot status-{color_suffix}"></div>
            <div class="timeline-line"></div>
        </div>
        <div class="timeline-card border-{color_suffix}">
            <div class="card-header">
                <span class="event-title">{provider}</span>
                <span class="event-id-badge">ID {eid}</span>
            </div>
            <div class="card-body">{details_preview}</div>
        </div>
    </div>
        """
    ).strip()

    st.markdown(html, unsafe_allow_html=True)
