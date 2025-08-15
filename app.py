
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
# =========================================================
# USE CASE 1: Decoding Transaction Dynamics on PhonePe
# =========================================================
elif section == "Use Case 1: Decoding Transaction Dynamics on PhonePe":
    st.title("Use Case 1: Decoding Transaction Dynamics on PhonePe")

    # 1.01
    section_title("1.01 Total Amount & Count by State & Year")
    q101 = """
        SELECT state, year,
               SUM(transaction_amount) AS total_amount,
               SUM(transaction_count)  AS total_count
        FROM aggregated_transaction_data
        GROUP BY state, year
        ORDER BY year, state;
    """
    d101 = run_sql(q101)
    if not warn_if_empty(d101):
        st.plotly_chart(px.bar(d101, x="state", y="total_amount", color="year",
                               barmode="group", title="Total Transaction Amount by State & Year"),
                        use_container_width=True)
        st.plotly_chart(px.bar(d101, x="state", y="total_count", color="year",
                               barmode="group", title="Total Transaction Count by State & Year"),
                        use_container_width=True)

    # 1.02
    section_title("1.02 Top 5 States by Insurance Amount")
    q102 = """
        SELECT state, SUM(transaction_amount) AS total_amount
        FROM aggregated_insurance_data
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 5;
    """
    d102 = run_sql(q102)
    if not warn_if_empty(d102):
        st.plotly_chart(px.bar(d102, x="state", y="total_amount",
                               title="Top 5 States (Insurance Amount)"),
                        use_container_width=True)

    # 1.03
    section_title("1.03 Top 10 Districts by Transaction Count (Map Transactions)")
    q103 = """
        SELECT state, district_state_name,
               SUM(transaction_count) AS total_count
        FROM map_transaction_data
        GROUP BY state, district_state_name
        ORDER BY total_count DESC
        LIMIT 10;
    """
    d103 = run_sql(q103)
    if not warn_if_empty(d103):
        st.plotly_chart(px.bar(d103, x="district_state_name", y="total_count", color="state",
                               title="Top 10 Districts by Txn Count"),
                        use_container_width=True)

    # 1.04
    section_title("1.04 Registered Users vs App Opens by State")
    q104 = """
        SELECT state,
               SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_opens
        FROM map_user_data
        GROUP BY state
        ORDER BY total_users DESC;
    """
    d104 = run_sql(q104)
    if not warn_if_empty(d104):
        st.plotly_chart(px.scatter(d104, x="total_users", y="total_opens", text="state",
                                   title="Users vs App Opens (State)"),
                        use_container_width=True)

    # 1.05
    section_title("1.05 Top 10 Pincodes by Transaction Amount")
    q105 = """
        SELECT entity_name AS pincode, SUM(transaction_amount) AS total_amount
        FROM top_transaction_data
        WHERE entity_level = 'pincode'
        GROUP BY entity_name
        ORDER BY total_amount DESC
        LIMIT 10;
    """
    d105 = run_sql(q105)
    if not warn_if_empty(d105):
        st.plotly_chart(px.bar(d105, x="pincode", y="total_amount",
                               title="Top 10 Pincodes by Txn Amount"),
                        use_container_width=True)

# =========================================================
# USE CASE 2: Device Dominance & User Engagement
# =========================================================
elif section == "Use Case 2: Device Dominance & User Engagement":
    st.title("Use Case 2: Device Dominance & User Engagement")

    # 2.01
    section_title("2.01 Top 5 States by Total Transaction Amount (All Time)")
    q201 = """
        SELECT state, SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction_data
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 5;
    """
    d201 = run_sql(q201)
    if not warn_if_empty(d201):
        st.plotly_chart(px.bar(d201, x="state", y="total_amount",
                               title="Top 5 States by Amount"),
                        use_container_width=True)

    # 2.02
    section_title("2.02 Yearly Growth in Transactions by State (Top 8 States)")
    top_states_sql = """
        WITH sums AS (
            SELECT state, SUM(transaction_amount) AS total_amount
            FROM aggregated_transaction_data
            GROUP BY state
        )
        SELECT state FROM sums ORDER BY total_amount DESC LIMIT 8;
    """
    topS = run_sql(top_states_sql)["state"].tolist()
    if topS:
        q202 = f"""
            SELECT state, year, SUM(transaction_count) AS total_transactions
            FROM aggregated_transaction_data
            WHERE state IN ({','.join(["'" + s.replace("'", "''") + "'" for s in topS])})
            GROUP BY state, year
            ORDER BY state, year;
        """
        d202 = run_sql(q202)
        if not warn_if_empty(d202):
            st.plotly_chart(px.line(d202, x="year", y="total_transactions", color="state",
                                    markers=True, title="Yearly Txn Count (Top States)"),
                            use_container_width=True)
    else:
        st.info("No states found for Top 8 selection.")

    # 2.03
    section_title("2.03 Engagement Rate by District (App Opens per 100 Users)")
    q203 = """
        SELECT district_state_name,
               SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_app_opens,
               CASE WHEN SUM(registered_users)=0 THEN 0
                    ELSE ROUND( (SUM(app_opens) * 100.0) / SUM(registered_users), 2) END AS engagement_rate_per_100
        FROM map_user_data
        GROUP BY district_state_name
        ORDER BY engagement_rate_per_100 DESC;
    """
    d203 = run_sql(q203)
    if not warn_if_empty(d203):
        st.plotly_chart(px.bar(d203.head(30), x="district_state_name", y="engagement_rate_per_100",
                               title="Top Districts by Engagement Rate"),
                        use_container_width=True)

    # 2.04
    section_title("2.04 Insurance Transaction Trends by Quarter")
    q204 = """
        SELECT year, quarter,
               SUM(transaction_count) AS total_insurance_tx,
               SUM(transaction_amount) AS total_insurance_amount
        FROM aggregated_insurance_data
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    d204 = run_sql(q204)
    if not warn_if_empty(d204):
        st.plotly_chart(px.line(d204, x="quarter", y="total_insurance_tx", color="year",
                                markers=True, title="Insurance Transactions (Count) by Quarter"),
                        use_container_width=True)
        st.plotly_chart(px.line(d204, x="quarter", y="total_insurance_amount", color="year",
                                markers=True, title="Insurance Amount by Quarter"),
                        use_container_width=True)

    # 2.05
    section_title("2.05 Top 10 Pincodes by Registered Users")
    q205 = """
        SELECT pincode, SUM(registeredusers) AS total_users
        FROM top_user_data
        GROUP BY pincode
        ORDER BY total_users DESC
        LIMIT 10;
    """
    d205 = run_sql(q205)
    if not warn_if_empty(d205):
        st.plotly_chart(px.bar(d205, x="pincode", y="total_users",
                               title="Top 10 Pincodes by Registered Users"),
                        use_container_width=True)

# =========================================================
# USE CASE 3: Insurance Penetration & Growth Potential
# =========================================================
elif section == "Use Case 3: Insurance Penetration & Growth Potential":
    st.title("Use Case 3: Insurance Penetration & Growth Potential")

    # 3.01
    section_title("3.01 Total Insurance Amount by State")
    q301 = """
        SELECT state, SUM(transaction_amount) AS total_insurance_amount
        FROM aggregated_insurance_data
        GROUP BY state
        ORDER BY total_insurance_amount DESC;
    """
    d301 = run_sql(q301)
    if not warn_if_empty(d301):
        st.plotly_chart(px.bar(d301, x="state", y="total_insurance_amount",
                               title="Insurance Amount by State"),
                        use_container_width=True)

    # 3.02
    section_title("3.02 Yearly Growth in Insurance Amount")
    q302 = """
        SELECT year, SUM(transaction_amount) AS total_amount
        FROM aggregated_insurance_data
        GROUP BY year
        ORDER BY year;
    """
    d302 = run_sql(q302)
    if not warn_if_empty(d302):
        st.plotly_chart(px.line(d302, x="year", y="total_amount", markers=True,
                                title="Insurance Amount by Year"),
                        use_container_width=True)

    # 3.03
    section_title("3.03 Insurance Penetration (Policies Sold) — Top 10 States")
    q303 = """
        SELECT state, SUM(transaction_count) AS total_policies_sold
        FROM aggregated_insurance_data
        GROUP BY state
        ORDER BY total_policies_sold DESC
        LIMIT 10;
    """
    d303 = run_sql(q303)
    if not warn_if_empty(d303):
        st.plotly_chart(px.bar(d303, x="state", y="total_policies_sold",
                               title="Top 10 States by Insurance Policies Sold"),
                        use_container_width=True)

    # 3.04
    section_title("3.04 Quarterly Growth Trend in Insurance Amount")
    q304 = """
        SELECT year, quarter, SUM(transaction_amount) AS total_amount
        FROM aggregated_insurance_data
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    d304 = run_sql(q304)
    if not warn_if_empty(d304):
        st.plotly_chart(px.line(d304, x="quarter", y="total_amount", color="year",
                                markers=True, title="Insurance Amount by Quarter"),
                        use_container_width=True)

    # 3.05
    section_title("3.05 Latest vs Previous Year Growth (Insurance)")
    q305 = """
        WITH yearly_amounts AS (
        SELECT year, SUM(transaction_amount) AS total_amount
        FROM aggregated_insurance_data
        GROUP BY year
    )
    SELECT a.year AS current_year,
           b.year AS previous_year,
           a.total_amount AS current_total_amount,
           b.total_amount AS previous_total_amount,
           (a.total_amount - b.total_amount) AS growth_amount,
           CASE WHEN b.total_amount=0 THEN NULL
                ELSE ROUND(((a.total_amount - b.total_amount) / b.total_amount) * 100, 2)
           END AS growth_percentage
    FROM yearly_amounts a
    JOIN yearly_amounts b ON a.year = b.year + 1
    ORDER BY current_year DESC;
    """
    d305 = run_sql(q305)
    if not warn_if_empty(d305):
        st.plotly_chart(px.bar(d305, x="current_year", y="growth_amount",
                               title="Year-over-Year Growth (Amount)", text="growth_percentage"),
                        use_container_width=True)

# =========================================================
# USE CASE 4: Transaction Analysis for Market Expansion
# =========================================================
elif section == "Use Case 4: Transaction Analysis for Market Expansion":
    st.title("Use Case 4: Transaction Analysis for Market Expansion")

    # 4.01
    section_title("4.01 Total Transaction Amount by State")
    q401 = """
        SELECT state, SUM(transaction_amount) AS total_transaction_amount
        FROM aggregated_transaction_data
        GROUP BY state
        ORDER BY total_transaction_amount DESC;
    """
    d401 = run_sql(q401)
    if not warn_if_empty(d401):
        st.plotly_chart(px.bar(d401, x="state", y="total_transaction_amount",
                               title="Total Txn Amount by State"),
                        use_container_width=True)

    # 4.02
    section_title("4.02 Top 10 States by Number of Transactions")
    q402 = """
        SELECT state, SUM(transaction_count) AS total_transactions
        FROM aggregated_transaction_data
        GROUP BY state
        ORDER BY total_transactions DESC
        LIMIT 10;
    """
    d402 = run_sql(q402)
    if not warn_if_empty(d402):
        st.plotly_chart(px.bar(d402, x="state", y="total_transactions",
                               title="Top 10 States by Transaction Count"),
                        use_container_width=True)

    # 4.03
    section_title("4.03 Yearly Growth in Transactions (Amount & Count)")
    q403 = """
        SELECT year,
               SUM(transaction_amount) AS total_amount,
               SUM(transaction_count)  AS total_transactions
        FROM aggregated_transaction_data
        GROUP BY year
        ORDER BY year;
    """
    d403 = run_sql(q403)
    if not warn_if_empty(d403):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.line(d403, x="year", y="total_amount", markers=True,
                                    title="Txn Amount by Year"),
                            use_container_width=True)
        with c2:
            st.plotly_chart(px.line(d403, x="year", y="total_transactions", markers=True,
                                    title="Txn Count by Year"),
                            use_container_width=True)

    # 4.04
    section_title("4.04 Quarterly Transaction Trends (Amount)")
    q404 = """
        SELECT year, quarter, SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction_data
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
    d404 = run_sql(q404)
    if not warn_if_empty(d404):
        st.plotly_chart(px.line(d404, x="quarter", y="total_amount", color="year",
                                markers=True, title="Txn Amount by Quarter"),
                        use_container_width=True)

    # 4.05
    section_title("4.05 States with Highest Growth (Latest vs Previous Year)")
    q405 = """
        WITH yearly_amounts AS (
        SELECT state, year, SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction_data
        GROUP BY state, year
    )
    SELECT a.state,
           a.year AS current_year,
           b.year AS previous_year,
           a.total_amount AS current_total_amount,
           b.total_amount AS previous_total_amount,
           (a.total_amount - b.total_amount) AS growth_amount,
           CASE WHEN b.total_amount=0 THEN NULL
                ELSE ROUND(((a.total_amount - b.total_amount) / b.total_amount) * 100, 2)
           END AS growth_percentage
    FROM yearly_amounts a
    JOIN yearly_amounts b ON a.state = b.state AND a.year = b.year + 1
    ORDER BY growth_percentage DESC NULLS LAST
    LIMIT 20;
    """
    d405 = run_sql(q405)
    if not warn_if_empty(d405):
        st.plotly_chart(px.bar(d405, x="state", y="growth_percentage",
                               title="Top States by YoY Growth (%)"),
                        use_container_width=True)

# =========================================================
# USE CASE 5: User Engagement & Growth Strategy
# =========================================================
elif section == "Use Case 5: User Engagement & Growth Strategy":
    st.title("Use Case 5: User Engagement & Growth Strategy")

    # 5.01
    section_title("5.01 Registered Users & App Opens by State (Scatter)")
    q501 = """
        SELECT state,
               SUM(registered_users) AS total_registered_users,
               SUM(app_opens) AS total_app_opens
        FROM map_user_data
        GROUP BY state
        ORDER BY total_registered_users DESC;
    """
    d501 = run_sql(q501)
    if not warn_if_empty(d501):
        st.plotly_chart(px.scatter(d501, x="total_registered_users", y="total_app_opens",
                                   text="state", title="App Opens vs Registered Users (State)"),
                        use_container_width=True)

    # 5.02
    section_title("5.02 Top 5 Districts — App Opens (2024)")
    q502 = """
        SELECT district_state_name, SUM(app_opens) AS total_app_opens
        FROM map_user_data
        WHERE year = 2024
        GROUP BY district_state_name
        ORDER BY total_app_opens DESC
        LIMIT 5;
    """
    d502 = run_sql(q502)
    if not warn_if_empty(d502):
        st.plotly_chart(px.bar(d502, x="district_state_name", y="total_app_opens",
                               title="Top 5 Districts by App Opens (2024)"),
                        use_container_width=True)

    # 5.03
    section_title("5.03 Top 5 Districts — Registered Users (2024 Q1)")
    q503 = """
        SELECT district_state_name, state, registered_users
        FROM map_user_data
        WHERE year = 2024 AND quarter = 1
        ORDER BY registered_users DESC
        LIMIT 5;
    """
    d503 = run_sql(q503)
    if not warn_if_empty(d503):
        st.plotly_chart(px.bar(d503, x="district_state_name", y="registered_users", color="state",
                               title="Top 5 Districts by Registered Users (2024 Q1)"),
                        use_container_width=True)

    # 5.04
    section_title("5.04 QoQ Change in Registered Users (Top States)")
    q504 = """
        WITH quarterly_data AS (
            SELECT state, year, quarter, SUM(registered_users) AS total_users
            FROM map_user_data
            GROUP BY state, year, quarter
        )
        SELECT a.state, a.year, a.quarter AS current_quarter,
               a.total_users AS current_users,
               b.total_users AS previous_users,
               (a.total_users - b.total_users) AS user_growth
        FROM quarterly_data a
        JOIN quarterly_data b
          ON a.state = b.state AND a.year = b.year AND a.quarter = b.quarter + 1
        ORDER BY user_growth DESC
        LIMIT 20;
    """
    d504 = run_sql(q504)
    if not warn_if_empty(d504):
        st.plotly_chart(px.bar(d504, x="state", y="user_growth",
                               title="QoQ Growth in Registered Users (Top States)"),
                        use_container_width=True)

    # 5.05
    section_title("5.05 States with Highest User Engagement (Opens per User)")
    q505 = """
        SELECT state,
               CASE WHEN SUM(registered_users)=0 THEN NULL
                    ELSE (SUM(app_opens) * 1.0 / SUM(registered_users)) END AS engagement_ratio
        FROM map_user_data
        GROUP BY state
        ORDER BY engagement_ratio DESC NULLS LAST
        LIMIT 10;
    """
    d505 = run_sql(q505)
    if not warn_if_empty(d505):
        st.plotly_chart(px.bar(d505, x="state", y="engagement_ratio",
                               title="Top 10 States by Engagement Ratio"),
                        use_container_width=True)

