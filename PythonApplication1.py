import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import datetime
import pymysql

# Pass the connection details directly into st.connection
conn = st.connection(
    "sql",
    type="sql",
    url="mysql+pymysql://root:sql1234@localhost/test"
)

st.markdown(
    """
    <h1 style='text-align: center; color: #FF7F7F; font-size: 60px;'>
        Cross Market Analysis
    </h1>
    """, 
    unsafe_allow_html=True
)
# 1. Inject Global CSS for Lavender Theme
st.markdown("""
    <style>
    /* Style all Titles (h1) */
    .stApp h1 {
        text-align: left;
        color: #B19CD9; /* Medium Lavender */
        font-size: 35px !important;
        font-weight: 700;
    }
    
    /* Style the Subtext (The st.write lines) */
    .stApp p {
        text-align: left;
        color: #000000; /* Slightly darker lavender for readability */
        font-size: 12;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation menu
menu = st.sidebar.radio(
    "Navigation",
    ["Market Overview", "SQL Query Runner", "Top 3 Crypto Analysis"]
)

# Display content based on selection
if menu == "Market Overview":
    st.title("Cross-Market Overview")
    st.write("Crypto.Oil.Stock Market | SQL Powered Analytics")

    #1. Create 3 columns: Left, Middle (spacer), and Right
    # The [2, 3, 2] ratio makes the side columns wide enough for the date picker
    col_left, col_space, col_right = st.columns([2, 3, 2])

    with col_left:
        start_date = st.date_input("Start Date", value=datetime.date(2025, 1, 1), key="start_date")

    with col_right:
        end_date = st.date_input("End Date", value=datetime.date.today(), key="end_date")

    # 2. Run Queries based on Dates
    # Note: Use :start and :end to prevent SQL injection
    #BITCOIN AVG
    btc_query = "SELECT avg(price_inr) FROM crypto_prices WHERE timestamp BETWEEN :start AND :end"
    btc_data = conn.query(btc_query, params={"start": start_date, "end": end_date})
    
    # Extract the value from the dataframe
    btc_price = btc_data.iloc[0, 0] if not btc_data.empty else "N/A"

    #OIL AVG
    oil_query = "SELECT avg(price) FROM oil_prices WHERE date BETWEEN :start AND :end"
    oil_data = conn.query(oil_query, params={"start": start_date, "end": end_date})
    
    oil_price = oil_data.iloc[0, 0] if not oil_data.empty else "N/A"

    #S&P 500 AVG
    sp500_query = "SELECT avg(close) FROM stock_prices WHERE ticker = '^GSPC' and date BETWEEN :start AND :end"
    sp500_data = conn.query(sp500_query, params={"start": start_date, "end": end_date})
    
    sp500_price = sp500_data.iloc[0, 0] if not sp500_data.empty else "N/A"

    #NIFTY AVG
    nifty_query = "SELECT avg(close) FROM stock_prices WHERE ticker = '^NSEI' and date BETWEEN :start AND :end"
    nifty_data = conn.query(nifty_query, params={"start": start_date, "end": end_date})
    
    nifty_price = nifty_data.iloc[0, 0] if not nifty_data.empty else "N/A"

    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px !important; /* Makes the number smaller so it doesn't wrap */
    }
    </style>
    """, unsafe_allow_html=True)

    # 3. Display in Blocks
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(label="Bitcoin Avg(INR)", value=f"₹{btc_price:,.2f}")
    
    with m2:
        st.metric(label="Oil Avg(INR)", value=f"₹{oil_price:,.2f}")
    
    with m3:
        st.metric(label="S&P 500 Avg", value=f"₹{sp500_price:,.2f}")
    
    with m4:
        st.metric(label="In Nifty Avg", value=f"₹{nifty_price:,.2f}")

    st.divider()

    # 4. Detailed Daily Results Query
    detailed_query = """
    SELECT 
        c.timestamp AS date, 
        c.price_inr AS bitcoin_price, 
        o.price AS oil_price, 
        MAX(CASE WHEN s.ticker = '^GSPC' THEN s.close END) AS sp500, 
        MAX(CASE WHEN s.ticker = '^NSEI' THEN s.close END) AS nifty
    FROM crypto_prices c 
    INNER JOIN oil_prices o ON c.timestamp = o.date
    INNER JOIN stock_prices s ON o.date = s.date
    WHERE c.coin_id = 'bitcoin' 
        AND c.timestamp BETWEEN :start AND :end
    GROUP BY c.timestamp, c.price_inr, o.price
    ORDER BY c.timestamp DESC
    """
    
    # Run the query
    df_details = conn.query(detailed_query, params={"start": start_date, "end": end_date})

    # 5. Display the Dataframe
    st.subheader("Daily Market Snapshot")
    
    if not df_details.empty:
        st.dataframe(
            df_details, 
            width='stretch', 
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("date", format="YYYY-MM-DD"),
                "bitcoin_price": st.column_config.NumberColumn("bitcoin_price", format="₹%.2f"),
                "oil_price": st.column_config.NumberColumn("oil_price", format="₹%.2f"),
                "sp500": st.column_config.NumberColumn("sp500", format="%.2f"),
                "nifty": st.column_config.NumberColumn("nifty", format="%.2f"),
            }
        )
    else:
        st.warning("No overlapping data found for the selected date range.")


elif menu == "SQL Query Runner":
    st.title("SQL Query Runner")
    st.write("Predefined SQL Queries...")

    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px !important; /* Makes the number smaller so it doesn't wrap */
    }
    </style>
    """, unsafe_allow_html=True)

    #1. Dropdown
    option = st.selectbox(
    "Select a Query",
    ["Top 3 cryptocurrencies by market cap", 
     "List all coins where circulating supply exceeds 90% of total supply" ,
     "Get coins that are within 10% of their all-time-high (ATH)",
     "Find the average market cap rank of coins with volume above $1B",
     "Get the most recently updated coin",
     "Find the highest daily price of Bitcoin in the last 365 days",
    "Calculate the average daily price of Ethereum in the past 1 year",
    "Show the daily price trend of Bitcoin in January 2026",
    "Find the coin with the highest average price over 1 year",
    "Get the % change in Bitcoin’s price between May 2025 and Mar 2026",
    "Find the highest oil price in the last 5 years",
    "Get the average oil price per year",
    "Show oil prices during COVID crash (March–April 2020)",
    "Find the lowest price of oil in the last 10 years",
    "Calculate the volatility of oil prices",
    "Get all stock prices for a given ticker",
    "Find the highest closing price for NASDAQ (^IXIC)",
    "List top 5 days with highest price difference for S&P 500 (^GSPC)",
    "Get monthly average closing price for each ticker",
    "Get average trading volume of NSEI in 2024",
    "Compare Bitcoin vs Oil average price in 2025",
    "Check if Bitcoin moves with S&P 500",
    "Compare Ethereum and NASDAQ daily prices for 2025",
    "Find days when oil price spiked and compare with Bitcoin price change",
    "Compare top 3 coins daily price trend vs Nifty (^NSEI)",
    "Compare stock prices (^GSPC) with crude oil prices on the same dates",
    "Correlate Bitcoin closing price with crude oil closing price (same date)",
    "Compare NASDAQ (^IXIC) with Ethereum price trends",
    "Join top 3 crypto coins with stock indices for 2025",
    "Compare stock prices, oil prices, and Bitcoin prices for daily comparison"
    ],
    index=0  # Default selection
    )

    # 2. The Run Button
    run_pressed = st.button("Run Query")

    # 3. Map dropdown options to actual SQL queries
    queries = {
    #1
        "Top 3 cryptocurrencies by market cap": 
            "SELECT id, market_cap FROM cryptocurrencies ORDER BY market_cap DESC LIMIT 3",
    #2
        "List all coins where circulating supply exceeds 90% of total supply":
        "SELECT id FROM cryptocurrencies WHERE circulating_supply > (total_supply * 0.90)",
    #3
        "Get coins that are within 10% of their all-time-high (ATH)":
        "select * from cryptocurrencies where ath <= (select max(ath)*0.10 from cryptocurrencies)",
    #4
        "Find the average market cap rank of coins with volume above $1B":
        "SELECT AVG(market_cap_rank) AS average_rank FROM cryptocurrencies WHERE total_volume > 1000000000",
    #5
        "Get the most recently updated coin":
        "SELECT id, date FROM cryptocurrencies order by date desc limit 1",
    #6
        "Find the highest daily price of Bitcoin in the last 365 days":
        "select timestamp, max(price_inr) max_price from crypto_prices where coin_id = 'bitcoin' group by timestamp order by timestamp desc",
    #7
        "Calculate the average daily price of Ethereum in the past 1 year":
        "select timestamp, avg(price_inr) avg_price from crypto_prices where coin_id = 'Ethereum' group by timestamp order by timestamp desc",
    #8
        "Show the daily price trend of Bitcoin in January 2026":
        "select * from crypto_prices where coin_id = 'bitcoin' and timestamp between '2026-01-01' and '2026-01-31' order by timestamp",
    #9
        "Find the coin with the highest average price over 1 year":
        "select coin_id, avg(price_inr) from crypto_prices group by coin_id order by 2 desc limit 1",
    #10
        "Get the % change in Bitcoin’s price between May 2025 and Mar 2026":
        '''WITH StartPrice AS (
                SELECT price_inr 
                FROM crypto_prices 
                WHERE coin_id = 'bitcoin' AND timestamp = '2025-05-01'
            ),
            EndPrice AS (
                SELECT price_inr 
                FROM crypto_prices 
                WHERE coin_id = 'bitcoin' AND timestamp = '2026-03-31'
            )
            SELECT 
                ((e.price_inr - s.price_inr) / s.price_inr) * 100 AS percentage_change
            FROM StartPrice s, EndPrice e''',
    #11
        "Find the highest oil price in the last 5 years":
        '''SELECT MAX(price) AS highest_price
            FROM oil_prices
            WHERE date BETWEEN (SELECT DATE_SUB(MAX(date), INTERVAL 5 YEAR) FROM oil_prices) 
                           AND (SELECT MAX(date) FROM oil_prices)''',
    #12
        "Get the average oil price per year":
        "select year(date), avg(price) avg_oil_price  from oil_prices group by year(date) order by 1 desc",
    #13
        "Show oil prices during COVID crash (March–April 2020)":
        "select * from oil_prices where date >= '2020-03-01' and date <= '2020-04-30' order by date",
    #14
        "Find the lowest price of oil in the last 10 years":
        '''SELECT MIN(price) AS highest_price
                FROM oil_prices
                WHERE date BETWEEN (SELECT Min(date) FROM oil_prices) 
                               AND (SELECT MAX(date) FROM oil_prices)''',
    #15
        "Calculate the volatility of oil prices":
        "select year(date), max(price) - min(price) price_volatility  from oil_prices group by year(date) order by 1 desc",
    #16
        "Get all stock prices for a given ticker":
        "select * from stock_prices",
    #17
        "Find the highest closing price for NASDAQ (^IXIC)":
        "select max(close) max_close_price from stock_prices where ticker = '^IXIC'",
    #18
        "List top 5 days with highest price difference for S&P 500 (^GSPC)":
        "SELECT date, high, low, (high - low) AS price_difference FROM stock_prices WHERE ticker = '^GSPC' ORDER BY price_difference DESC LIMIT 5",
    #19
        "Get monthly average closing price for each ticker":
        "select ticker, month(date), avg(close) avg_close_price from stock_prices group by ticker, month(date) order by 1 asc, 2 desc",
    #20
        "Get average trading volume of NSEI in 2024":
        "select avg(volume) avg_trading_volume from stock_prices where ticker = '^NSEI' and year(date) = '2024'",
    #21
        "Compare Bitcoin vs Oil average price in 2025":
        '''select '2025' year
		    , (select avg(price_inr) from crypto_prices where coin_id = 'bitcoin' and year(timestamp) = '2025') bitocoin_avg_price
		    , (select avg(price) from oil_prices where year(date) = '2025') oil_avg_price ''',
    #22
        "Check if Bitcoin moves with S&P 500":
         '''select s.ticker, cast(s.date as date) date, s.open sp500_price, c.coin_id, c.price_inr bitcoint_price
                from stock_prices s inner join crypto_prices c on s.date = c.timestamp
                where ticker = '^GSPC' and coin_id = 'bitcoin'
                order by s.date desc''',
    #23
        "Compare Ethereum and NASDAQ daily prices for 2025":
        '''SELECT 
                c.coin_id, 
                c.timestamp, 
                c.price_inr ethereum_price, 
                s.ticker, 
                s.close nasdaq_price
            FROM crypto_prices c
            INNER JOIN stock_prices s 
                ON DATE(c.timestamp) = s.date
            WHERE c.coin_id = 'Ethereum' 
              AND s.ticker = '^IXIC'
              AND YEAR(s.date) = 2025
            ORDER BY s.date''',
    #24
        "Find days when oil price spiked and compare with Bitcoin price change":
        '''select c.coin_id, c.timestamp, c.price_inr bitcoin_price, o.price oil_price
            from crypto_prices c inner join oil_prices o on (c.timestamp = o.date and o.price > c.price_inr)
            where coin_id = 'bitcoin' order by c.timestamp desc''',
    #25
        "Compare top 3 coins daily price trend vs Nifty (^NSEI)":
        '''select s.ticker, cast(s.date as date) date, s.open, c.coin_id, c.price_inr
            from stock_prices s inner join crypto_prices c on s.date = c.timestamp
            where ticker = '^NSEI'
            order by s.date desc''',
    #26
        "Compare stock prices (^GSPC) with crude oil prices on the same dates":
        '''select s.ticker, cast(s.date as date) date, s.open ticker_price,  o.price oil_price
            from stock_prices s inner join oil_prices o on s.date = o.date
            where ticker = '^GSPC'
            order by s.date desc''',
    #27
        "Correlate Bitcoin closing price with crude oil closing price (same date)":
        '''select c.coin_id, c.timestamp, c.price_inr bitcoin_price, o.price oil_price
            from crypto_prices c inner join oil_prices o on c.timestamp = o.date
            where coin_id = 'bitcoin' order by c.timestamp desc''',
    #28
        "Compare NASDAQ (^IXIC) with Ethereum price trends":
        '''SELECT c.coin_id, c.timestamp date, c.price_inr ethereum_price, s.ticker, s.close nasdaq_price
                FROM crypto_prices c INNER JOIN stock_prices s ON DATE(c.timestamp) = s.date
                WHERE c.coin_id = 'Ethereum' AND s.ticker = '^IXIC'
                ORDER BY s.date desc''',
    #29
        "Join top 3 crypto coins with stock indices for 2025":
        '''SELECT c.coin_id, c.timestamp date, c.price_inr crypto_price, s.ticker, s.close stock_price
                FROM crypto_prices c INNER JOIN stock_prices s ON DATE(c.timestamp) = s.date
                ORDER BY s.date desc''',
    #30
        "Compare stock prices, oil prices, and Bitcoin prices for daily comparison":
        '''select c.coin_id, c.timestamp, c.price_inr bitcoin_price, o.price oil_price, s.ticker, s.close stock_price
                from crypto_prices c inner join oil_prices o on c.timestamp = o.date
	                inner join stock_prices s on o.date = s.date
                where coin_id = 'bitcoin' order by c.timestamp desc'''
    }

    # 4. Logic to run ONLY when button is clicked
    if run_pressed:
        if option in queries:
            with st.spinner("Executing query..."):
                try:
                    query_to_run = queries[option]
                    df_results = conn.query(query_to_run)

                    if not df_results.empty:
                        st.subheader("Query executed successfully")
                        st.dataframe(df_results, width='stretch', hide_index=True)
                        
                    else:
                        st.warning("No data found for this selection.")
                except Exception as e:
                    st.error(f"SQL Error: {e}")
        else:
            st.info(f"SQL logic for '{option}' hasn't been added to the dictionary yet.")

elif menu == "Top 3 Crypto Analysis":
    st.title("Top 3 Crypto Analysis")
    st.write("Daily price analysis for top cryptocurrencies.")

    # 1. Fetch dynamic options for the dropdown
    crypto_list_query = "SELECT id FROM cryptocurrencies ORDER BY market_cap DESC LIMIT 3"
    df_crypto = conn.query(crypto_list_query)
    crypto_options = df_crypto.iloc[:, 0].tolist() if not df_crypto.empty else ["No coins found"]

    # 2. Input Widgets (Interacting here triggers a script re-run)
    selected_coin = st.selectbox("Select a Cryptocurrency", options=crypto_options)

    col_left1, _, col_right1 = st.columns([2, 3, 2])
    with col_left1:
        start_date = st.date_input("Start Date", value=datetime.date(2025, 1, 1), key="start_date")
    with col_right1:
        end_date = st.date_input("End Date", value=datetime.date.today(), key="end_date")

    # 3. Automatic Query Execution
    # Because there is no 'if button', this runs every time a selection changes
    crypto_query = """
        SELECT date, current_price AS price_inr 
        FROM cryptocurrencies 
        WHERE date BETWEEN :start AND :end 
        AND id = :coin
        ORDER BY date DESC
    """
    
    # Run query with mapped parameters
    crypto_data = conn.query(
        crypto_query, 
        params={"start": start_date, "end": end_date, "coin": selected_coin}
    )

    # 4. Immediate Display
    if not crypto_data.empty:
        st.subheader(f"{selected_coin.upper()} Price Trend")
        
        # Then display the raw data table
        st.dataframe(crypto_data, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No data available for {selected_coin} in this date range.")

