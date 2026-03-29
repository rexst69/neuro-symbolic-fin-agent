from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def render_queue() -> None:
    """Render a mock human-in-the-loop escalation queue."""
    st.subheader("Escalation Queue")

    rows: List[Dict[str, Any]] = [
        {
            "transaction_id": "txn_1001",
            "status": "AWAITING_RECOVERY",
            "amount": 12850.75,
            "reason": "Rollback action failed",
        },
        {
            "transaction_id": "txn_1002",
            "status": "ESCALATED_TO_HUMAN",
            "amount": 54000.00,
            "reason": "Amount exceeds autonomous threshold",
        },
        {
            "transaction_id": "txn_1003",
            "status": "AWAITING_RECOVERY",
            "amount": 9120.40,
            "reason": "Policy decision requires manual review",
        },
    ]

    queue_df = pd.DataFrame(rows)
    st.dataframe(queue_df, use_container_width=True)

    selected_transaction_id = st.selectbox(
        "Select transaction for manual action",
        options=queue_df["transaction_id"].tolist(),
    )

    if st.button("Approve Manual Match"):
        st.success(f"Manual match approved for {selected_transaction_id}.")
