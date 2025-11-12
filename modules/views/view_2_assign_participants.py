import streamlit as st
import pandas as pd
from modules.data import session_data
from modules.data.assignment_data import GroupData, SplitManager, ParticipantData
from modules.utils import format_currency


def controller():
    st.header("👥 Assign Participants")
    st.caption("Split the bill fairly by assigning items to each participant.")
    st.markdown("---")

    # Receipt Check
    receipt = session_data.uploaded_receipt.get()
    if not receipt:
        st.warning("Please upload and confirm a receipt first.")
        return

    # Persistent Session Setup
    group_data = session_data.group_data.get()
    if group_data is None:
        group_data = GroupData(name="Default Group")
        session_data.group_data.set(group_data)

    manager = session_data.split_manager.get()
    if manager is None:
        manager = SplitManager(group_data.participants, receipt.items)
        session_data.split_manager.set(manager)

    manager.receipt_items = receipt.items

    # Add Participants
    st.subheader("➕ Add Participants")
    with st.form("add_participant_form", clear_on_submit=True):
        name = st.text_input("Participant name", placeholder="e.g. Farhan, Taufiq")
        add_btn = st.form_submit_button("Add")
        if add_btn:
            if not name.strip():
                st.error("Please enter a valid name.")
            else:
                participant = ParticipantData(name=name)
                group_data.participants.append(participant)
                manager.add_participant(name)
                session_data.group_data.set(group_data)
                session_data.split_manager.set(manager)
                st.success(f"Added participant: {name}")
                st.rerun()

    if not manager.participants:
        st.info("No participants yet.")
        return

    st.markdown("---")

    # Receipt Items Table
    st.subheader("Receipt Items Overview")
    df = receipt.to_dataframe()[["name", "price", "category"]]
    df.columns = ["Item", "Price", "Category"]
    df["Price"] = df["Price"].apply(format_currency)
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.markdown("---")

    # Assign Items
    st.subheader("Assign Items to Participants")

    all_items = list(receipt.items.values())

    for pid, participant in manager.participants.items():
        st.markdown(f"### 👤 {participant.name}")

        # Ambil assigned items dari state
        assigned_items = manager.get_assignments(pid)
        assigned_ids = [a.item.id for a in assigned_items]
        available_items = [it for it in all_items if it.id not in assigned_ids]

        with st.form(f"assign_form_{pid}", clear_on_submit=True):
            selected_item = st.selectbox(
                f"Select item for {participant.name}",
                ["— Select —"] + [it.name for it in available_items],
                key=f"select_{pid}"
            )
            assign_btn = st.form_submit_button("Assign")

            if assign_btn:
                if selected_item == "— Select —":
                    st.error("Please select a valid item.")
                else:
                    # Temukan item berdasarkan nama
                    target = next(
                        (it for it in all_items if it.name.strip().lower() == selected_item.strip().lower()),
                        None
                    )
                    if target:
                        manager.assign_item(pid, target.id)
                        session_data.split_manager.set(manager)
                        st.success(f"Assigned **{selected_item}** to **{participant.name}**")
                        st.rerun()

        # Tampilkan hasil assignment langsung
        assigned_items = manager.get_assignments(pid)
        if assigned_items:
            table = pd.DataFrame(
                [{"Item": a.item.name, "Price": format_currency(a.item.price)} for a in assigned_items]
            )
            st.table(table)
        else:
            st.caption("No items assigned yet.")

        st.markdown("---")

    # Validation Section
    total_items = len(all_items)
    total_assigned = sum(len(v) for v in manager.participant_assignments.values())

    if total_assigned == total_items:
        st.success("All items assigned successfully!")
    else:
        st.warning(f"🟡 {total_assigned}/{total_items} items assigned.")

    st.markdown("---")

    # Confirm Split
    if st.button("Confirm Split", type="primary", disabled=(total_assigned < total_items)):
        st.session_state["split_confirmed"] = True
        st.success("Split confirmed! Proceed to the report page.")