"""
CRUD Operations page for Cricbuzz LiveStats
"""
import streamlit as st
from utils.crud_players import (
    fetch_players, create_player, update_player, delete_player, get_next_player_id
)


def render():
    """Render CRUD operations page"""
    st.title("🛠 CRUD Operations (Players)")

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Create", "📄 Read", "✏️ Update", "🗑 Delete"])

    # ---------------- CREATE ----------------
    with tab1:
        st.subheader("Add New Player")
        
        # Auto-generate next player ID
        next_id = get_next_player_id()
        st.info(f"💡 Next available Player ID: **{next_id}**")

        with st.form("create_player_form"):
            name = st.text_input("Name*", placeholder="e.g., MS Dhoni")
            country = st.text_input("Country", placeholder="e.g., India")
            role = st.selectbox("Role", ["Batter", "Bowler", "Allrounder", "Wicketkeeper"])
            batting_style = st.text_input("Batting Style", placeholder="e.g., Right-hand bat")
            bowling_style = st.text_input("Bowling Style", placeholder="e.g., Right-arm medium")

            submitted = st.form_submit_button("Create Player", type="primary")

        if submitted:
            try:
                if not name.strip():
                    st.error("❌ Name is required.")
                else:
                    create_player(next_id, name.strip(), country.strip(), role, batting_style.strip(), bowling_style.strip())
                    st.toast(f"✅ Player '{name}' created successfully!", icon="✅")
                    st.success(f"✅ Player created successfully with ID: {next_id}")
                    st.rerun()
            except Exception as e:
                st.toast(f"❌ Create failed: {e}", icon="❌")
                st.error(f"❌ Create failed: {e}")

    # ---------------- READ ----------------
    with tab2:
        st.subheader("View Players")
        search = st.text_input("Search by name/country/role", placeholder="e.g., England / Batter / Buttler")

        try:
            df = fetch_players(search)
            st.dataframe(df, width='stretch')
            st.caption(f"Total players: {len(df)}")
        except Exception as e:
            st.error(f"Read failed: {e}")

    # ---------------- UPDATE ----------------
    with tab3:
        st.subheader("Update Player")

        df_all = fetch_players("")
        if df_all.empty:
            st.warning("No players available to update.")
        else:
            options = df_all.to_dict("records")
            selected = st.selectbox(
                "Select player",
                options,
                format_func=lambda x: f"{x['player_id']} - {x['name']}"
            )

            with st.form("update_player_form"):
                name = st.text_input("Name", value=selected["name"] or "")
                country = st.text_input("Country", value=selected["country"] or "")
                role = st.text_input("Role", value=selected["role"] or "")
                batting_style = st.text_input("Batting Style", value=selected["batting_style"] or "")
                bowling_style = st.text_input("Bowling Style", value=selected["bowling_style"] or "")

                updated = st.form_submit_button("Update Player")

            if updated:
                try:
                    update_player(int(selected["player_id"]), name.strip(), country.strip(), role.strip(), batting_style.strip(), bowling_style.strip())
                    st.toast(f"✅ Player '{name}' updated successfully!", icon="✅")
                    st.success("✅ Player updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.toast(f"❌ Update failed: {e}", icon="❌")
                    st.error(f"❌ Update failed: {e}")

    # ---------------- DELETE ----------------
    with tab4:
        st.subheader("Delete Player")

        df_all = fetch_players("")
        if df_all.empty:
            st.warning("No players available to delete.")
        else:
            options = df_all.to_dict("records")
            selected = st.selectbox(
                "Select player to delete",
                options,
                format_func=lambda x: f"{x['player_id']} - {x['name']}",
                key="delete_select"
            )

            st.error("⚠️ This action cannot be undone.")
            confirm = st.checkbox("I confirm I want to delete this player")

            if st.button("Delete Player"):
                if not confirm:
                    st.warning("Please confirm before deleting.")
                else:
                    try:
                        player_name = selected["name"]
                        delete_player(int(selected["player_id"]))
                        st.toast(f"🗑️ Player '{player_name}' deleted successfully!", icon="🗑️")
                        st.success("✅ Player deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.toast(f"❌ Delete failed: {e}", icon="❌")
                        st.error(f"❌ Delete failed: {e}")
