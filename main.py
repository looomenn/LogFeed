import os
import tempfile

import polars as pl
import streamlit as st

from modules.parser import parse_evtx
from modules.ui import load_css, render_event_card

st.set_page_config(page_title="LogFeed", layout="wide")

load_css()

with st.sidebar:
    st.title("LogFeed")
    uploaded_file = st.file_uploader(
        "Drop .evtx file here", type=["evtx"], accept_multiple_files=False, width=300
    )

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".evtx") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Parsing events..."):
        df = parse_evtx(tmp_path)

    os.remove(tmp_path)

    if not df.is_empty():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Events", df.height)
        col2.metric("Computers", df["computer"].n_unique())
        col3.metric("Errors", df.filter(pl.col("level") == 2).height)
        last_time = df["timestamp"].max()
        col4.metric("Last Activity", last_time.strftime("%H:%M:%S"))

        st.markdown("---")

        # Пошук
        search_query = st.text_input(
            "Search logs...",
            placeholder="Type Event ID (4625), process name, or user...",
        )

        filtered_df = df
        if search_query:
            filtered_df = df.filter(
                pl.col("raw_json").str.to_lowercase().str.contains(search_query.lower())
            )

        for row in filtered_df.head(100).iter_rows(named=True):
            render_event_card(row)

        if filtered_df.height > 100:
            st.warning("Showing first 100 events. Use search to refine.")

    else:
        st.error("Could not parse file. Is it a valid .evtx?")

else:
    st.markdown(
        """
    ## Nothing there yet.

    Upload .evtx file in the sidebar.
    """
    )
