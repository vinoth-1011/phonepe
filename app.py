
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text

# =========================
# DB CONFIG
# =========================
DB_HOST = "dpg-d2c1kier433s73a8a7p0-a.singapore-postgres.render.com"
DB_NAME = "phonepe_data"
DB_USER = "phonepe_m8o9_user"
DB_PASS = "zkVsinSHsjx0wachLF0CJEL7AJP1ySKa"
DB_PORT = 5432

st.set_page_config(page_title="PhonePe: All-in-One Insights", layout="wide")

# =========================
# HELPERS
# =========================
@st.cache_resource(show_spinner=False)
def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)

@st.cache_data(ttl=600, show_spinner=False)
def run_sql(sql: str, params: dict | None = None) -> pd.DataFrame:
    eng = get_engine()
    with eng.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})

def kfmt(n):
    try:
        n = float(n)
        if n >= 1e9:  return f"{n/1e9:.2f}B"
        if n >= 1e6:  return f"{n/1e6:.2f}M"
        if n >= 1e3:  return f"{n/1e3:.2f}K"
        return f"{n:,.0f}"
    except Exception:
        return "-"

def section_title(title: str, subtitle: str = ""):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)

def warn_if_empty(df: pd.DataFrame, msg="No data found for this block."):
    if df is None or df.empty:
        st.info(msg)
        return True
    return False

# Build WHERE clause only when filters are applied (to avoid cast/param syntax issues)
def add_where_filters(base_sql: str, year_opt, q_opt, table_alias: str = ""):
    alias = (table_alias + ".") if table_alias else ""
    clauses = []
    params = {}
    if (year_opt is not None) and (str(year_opt) != "All"):
        clauses.append(f"{alias}year = :yr")
        params["yr"] = int(year_opt)
    if (q_opt is not None) and (str(q_opt) != "All"):
        clauses.append(f"{alias}quarter = :qt")
        params["qt"] = int(q_opt)
    if clauses:
        if " where " in base_sql.lower():
            base_sql += " AND " + " AND ".join(clauses)
        else:
            base_sql += " WHERE " + " AND ".join(clauses)
    return base_sql, params

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📚 Navigation")

section = st.sidebar.selectbox(
    "Choose a section",
    [
        "Dashboard",
        "Use Case 1: Decoding Transaction Dynamics on PhonePe",
        "Use Case 2: Device Dominance & User Engagement",
        "Use Case 3: Insurance Penetration & Growth Potential",
        "Use Case 4: Transaction Analysis for Market Expansion",
        "Use Case 5: User Engagement & Growth Strategy",
    ],
    index=0
)

# =========================
# DASHBOARD (Map in center)
# =========================
if section == "Dashboard":
    st.title("📊 PhonePe Dashboard")

    # No filter dropdowns
    year_opt = None
    q_opt = None

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    base_tx_sql = "SELECT SUM(transaction_amount) AS total_amount, SUM(transaction_count) AS total_count FROM aggregated_transaction_data"
    sql_tx, p_tx = add_where_filters(base_tx_sql, year_opt, q_opt)
    tx_df = run_sql(sql_tx, p_tx)
    total_amount = tx_df["total_amount"].iloc[0] if not tx_df.empty else 0
    total_count  = tx_df["total_count"].iloc[0] if not tx_df.empty else 0
    col1.metric("Total Transaction Amount", f"₹ {kfmt(total_amount)}")
    col2.metric("Total Transactions (Count)", kfmt(total_count))

    base_user_sql = "SELECT SUM(registered_users) AS total_users, SUM(app_opens) AS total_opens FROM map_user_data"
    sql_us, p_us = add_where_filters(base_user_sql, year_opt, q_opt)
    user_df = run_sql(sql_us, p_us)
    total_users = user_df["total_users"].iloc[0] if not user_df.empty else 0
    total_opens = user_df["total_opens"].iloc[0] if not user_df.empty else 0
    col3.metric("Registered Users", kfmt(total_users))
    col4.metric("App Opens", kfmt(total_opens))

    st.markdown("---")

    left, center, right = st.columns([1.2, 2.2, 1.2])

    # LEFT: by transaction type + top states
    with left:
        section_title("🇮🇳 All-India Overview", "By Transaction Type")
        tx_type_sql = "SELECT transaction_type, SUM(transaction_amount) AS total_amount, SUM(transaction_count) AS total_count FROM aggregated_transaction_data"
        sql_ttt, p_ttt = add_where_filters(tx_type_sql, year_opt, q_opt)
        sql_ttt += " GROUP BY transaction_type ORDER BY total_amount DESC"
        ttd = run_sql(sql_ttt, p_ttt)
        if not warn_if_empty(ttd):
            st.dataframe(
                ttd.rename(columns={"transaction_type": "Type", "total_amount": "Amount", "total_count": "Count"}),
                use_container_width=True, height=260
            )

        st.markdown("—")
        st.caption("Top states by amount")
        top_states_sql = "SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction_data"
        sql_ts, p_ts = add_where_filters(top_states_sql, year_opt, q_opt)
        sql_ts += " GROUP BY state ORDER BY total_amount DESC LIMIT 5"
        ts = run_sql(sql_ts, p_ts)
        if not warn_if_empty(ts, "No states data."):
            st.table(ts)

    # CENTER: India Map
    with center:
        section_title("🗺️ India Map", "Transaction Amount by State")
        map_sql = "SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction_data"
        sql_map, p_map = add_where_filters(map_sql, year_opt, q_opt)
        sql_map += " GROUP BY state ORDER BY state"
        map_df = run_sql(sql_map, p_map)

        if not warn_if_empty(map_df, "No map data."):
            state_name_map = {
                "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
                "Dadra & Nagar Haveli & Daman & Diu": "Dadra And Nagar Haveli And Daman And Diu",
                "Nct Of Delhi": "Nct Of Delhi",
                "Pondicherry": "Pondicherry",
                "Telangana": "Telangana",
                "Uttarakhand": "Uttarakhand"
            }
            map_df["state_norm"] = (
                map_df["state"]
                .str.strip()
                .str.title()
                .replace(state_name_map)
            )
            geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            fig = go.Figure(
                data=go.Choropleth(
                    geojson=geojson_url,
                    featureidkey="properties.ST_NM",
                    locationmode="geojson-id",
                    locations=map_df["state_norm"],
                    z=map_df["total_amount"].astype(float),
                    autocolorscale=False,
                    colorscale="Reds",
                    marker_line_color="peachpuff",
                    colorbar=dict(
                        title={'text': "Txn Amount (₹)"},
                        thickness=15, len=0.35, bgcolor='rgba(255,255,255,0.6)', tick0=0
                    )
                )
            )
            fig.update_geos(
                visible=False,
                projection=dict(type='conic conformal',
                                parallels=[12.472944444, 35.172805555556],
                                rotation={'lat': 24, 'lon': 80}),
                lonaxis={'range': [68, 98]},
                lataxis={'range': [6, 38]}
            )
            fig.update_layout(margin={'r': 0, 't': 10, 'l': 0, 'b': 0}, height=550)
            st.plotly_chart(fig, use_container_width=True)

    # RIGHT: pie + lists
    with right:
        section_title("📂 Categories & Top Lists")
        if not warn_if_empty(ttd):
            pie = px.pie(ttd, names="transaction_type", values="total_amount", title="Share by Txn Amount")
            st.plotly_chart(pie, use_container_width=True)

