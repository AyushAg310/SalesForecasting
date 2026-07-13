import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(page_title='Sales Forecasting & Demand Intelligence', layout='wide', page_icon='📊')

DATA = 'data'

# ============================================================
# THEME — professional navy / teal / gold palette
# ============================================================
NAVY = '#0B2545'
SLATE = '#13315C'
TEAL = '#1B998B'
GOLD = '#C9A227'
MAROON = '#8C3B3B'
STEEL = '#6C8EBF'
BG = '#F7F8FA'
CARD_BG = '#FFFFFF'
TEXT = '#1B2431'
MUTED = '#5B6472'

DISCRETE_SEQUENCE = [NAVY, TEAL, GOLD, MAROON, STEEL, '#4C6A92', '#A85751']

pio.templates['superstore'] = go.layout.Template(
    layout=go.Layout(
        colorway=DISCRETE_SEQUENCE,
        font=dict(family='Segoe UI, Helvetica, Arial, sans-serif', color=TEXT, size=13),
        title_font=dict(size=18, color=NAVY),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#E4E7EB', zerolinecolor='#E4E7EB'),
        yaxis=dict(gridcolor='#E4E7EB', zerolinecolor='#E4E7EB'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(bgcolor=NAVY, font_color='white', font_size=13),
    )
)
pio.templates.default = 'superstore'

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; }}
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{ color: #E8ECF1 !important; }}
    section[data-testid="stSidebar"] .stRadio label:hover {{ color: {GOLD} !important; }}
    div[data-testid="stMetric"] {{
        background-color: {CARD_BG};
        border: 1px solid #E4E7EB;
        border-left: 4px solid {TEAL};
        border-radius: 8px;
        padding: 14px 16px 8px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    div[data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-weight: 600; }}
    div[data-testid="stMetricValue"] {{ color: {NAVY} !important; }}
    h1, h2, h3 {{ color: {NAVY} !important; }}
    .app-header {{
        background: linear-gradient(90deg, {NAVY} 0%, {SLATE} 100%);
        padding: 22px 28px; border-radius: 10px; margin-bottom: 18px;
    }}
    .app-header h1 {{ color: white !important; margin: 0; font-size: 26px; }}
    .app-header p {{ color: #C9D4E3; margin: 4px 0 0 0; font-size: 14px; }}
    .section-tag {{
        display: inline-block; background-color: {TEAL}; color: white;
        padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
        margin-bottom: 6px;
    }}
</style>
""", unsafe_allow_html=True)


def page_header(title, tag, subtitle):
    st.markdown(f"""
    <div class="app-header">
        <span class="section-tag">{tag}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data
def load_csv(name, parse_dates=None):
    return pd.read_csv(f'{DATA}/{name}', parse_dates=parse_dates)


st.sidebar.markdown('## 📊 Navigation')
page = st.sidebar.radio(
    'Go to',
    ['Sales Overview', 'Forecast Explorer', 'Anomaly Report', 'Product Demand Segments'],
    label_visibility='collapsed',
)
st.sidebar.markdown('---')
st.sidebar.caption('Sales Forecasting & Demand Intelligence System')
st.sidebar.caption('Superstore dataset · 2015–2018')

# ============================================================
# PAGE 1 — SALES OVERVIEW
# ============================================================
if page == 'Sales Overview':
    page_header('Sales Overview', 'OVERVIEW', 'Company-wide performance across 4 years of order data')

    yearly = load_csv('yearly_sales.csv')
    monthly = load_csv('monthly_trend.csv', parse_dates=['Date'])
    region_cat = load_csv('region_category_monthly.csv', parse_dates=['Order Date'])

    year_choice = st.select_slider('Filter by year range', options=sorted(yearly['Year'].unique()),
                                    value=(int(yearly['Year'].min()), int(yearly['Year'].max())))
    yearly_f = yearly[(yearly['Year'] >= year_choice[0]) & (yearly['Year'] <= year_choice[1])]
    monthly_f = monthly[(monthly['Date'].dt.year >= year_choice[0]) & (monthly['Date'].dt.year <= year_choice[1])]

    total_sales = yearly_f['Sales'].sum()
    avg_monthly = monthly_f['Sales'].mean()
    peak_month = monthly_f.loc[monthly_f['Sales'].idxmax()]
    yoy = ((yearly_f['Sales'].iloc[-1] - yearly_f['Sales'].iloc[0]) / yearly_f['Sales'].iloc[0] * 100) if len(yearly_f) > 1 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Total Sales (selected years)', f'${total_sales:,.0f}')
    k2.metric('Average Monthly Sales', f'${avg_monthly:,.0f}')
    k3.metric('Peak Month', peak_month['Date'].strftime('%b %Y'), f"${peak_month['Sales']:,.0f}")
    k4.metric('Growth (first → last year)', f'{yoy:+.1f}%')

    st.write('')
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Total Sales by Year')
        fig = px.bar(yearly_f, x='Year', y='Sales', text_auto='.2s', color_discrete_sequence=[NAVY])
        fig.update_traces(marker_line_width=0, hovertemplate='%{x}<br>$%{y:,.0f}<extra></extra>')
        fig.update_layout(yaxis_title='Sales ($)', height=380)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader('Monthly Sales Trend')
        show_avg = st.toggle('Show 3-month rolling average', value=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_f['Date'], y=monthly_f['Sales'], mode='lines+markers',
                                  name='Monthly Sales', line=dict(color=TEAL, width=2)))
        if show_avg:
            fig.add_trace(go.Scatter(x=monthly_f['Date'], y=monthly_f['Sales'].rolling(3).mean(),
                                      mode='lines', name='3-mo rolling avg', line=dict(color=GOLD, width=2, dash='dash')))
        fig.update_layout(yaxis_title='Sales ($)', height=380, legend=dict(orientation='h', y=1.15))
        st.plotly_chart(fig, width='stretch')

    st.subheader('Sales by Region and Category')
    filt1, filt2 = st.columns(2)
    with filt1:
        regions = st.multiselect('Region', sorted(region_cat['Region'].unique()),
                                  default=sorted(region_cat['Region'].unique()))
    with filt2:
        categories = st.multiselect('Category', sorted(region_cat['Category'].unique()),
                                     default=sorted(region_cat['Category'].unique()))

    filtered = region_cat[
        region_cat['Region'].isin(regions) & region_cat['Category'].isin(categories) &
        (region_cat['Order Date'].dt.year >= year_choice[0]) & (region_cat['Order Date'].dt.year <= year_choice[1])
    ]
    fig = px.line(filtered, x='Order Date', y='Sales', color='Category', line_dash='Region',
                  title=None, color_discrete_sequence=DISCRETE_SEQUENCE)
    fig.update_layout(yaxis_title='Sales ($)', height=420, legend=dict(orientation='h', y=1.1))
    st.plotly_chart(fig, width='stretch')

    with st.expander('View underlying data'):
        display_filtered = filtered.copy()
        display_filtered['Sales'] = display_filtered['Sales'].round(1)
        st.dataframe(display_filtered, width='stretch', hide_index=True)
        st.download_button('Download filtered data (CSV)', filtered.to_csv(index=False), 'sales_filtered.csv')

# ============================================================
# PAGE 2 — FORECAST EXPLORER
# ============================================================
elif page == 'Forecast Explorer':
    page_header('Forecast Explorer', 'FORECASTING', 'SARIMA (2,1,2)(1,1,1,12) — selected in Task 3 by lowest MAE/RMSE/MAPE against held-out actuals')

    forecasts = load_csv('forecasts.csv', parse_dates=['Date'])
    metrics = load_csv('model_metrics.csv')
    segment_options = [s for s in forecasts['Segment'].unique() if s != 'Overall']

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        segments = st.multiselect('Compare category / region', segment_options, default=[segment_options[0]])
    with c2:
        horizon = st.slider('Forecast horizon (months ahead)', min_value=1, max_value=3, value=3)
    with c3:
        show_ci = st.toggle('Show confidence band', value=True)

    if not segments:
        st.info('Select at least one category or region above to see its forecast.')
    else:
        fig = go.Figure()
        for i, segment in enumerate(segments):
            color = DISCRETE_SEQUENCE[i % len(DISCRETE_SEQUENCE)]
            hist = load_csv(f'history_{segment.replace(" ", "_")}.csv', parse_dates=['Date'])
            seg_forecast = forecasts[(forecasts['Segment'] == segment) & (forecasts['MonthAhead'] <= horizon)]

            fig.add_trace(go.Scatter(x=hist['Date'][-18:], y=hist['Sales'][-18:], mode='lines',
                                      name=f'{segment} — actual', line=dict(color=color, width=2)))
            fig.add_trace(go.Scatter(x=seg_forecast['Date'], y=seg_forecast['Forecast'], mode='lines+markers',
                                      name=f'{segment} — forecast', line=dict(color=color, width=2, dash='dash')))
            if show_ci:
                fig.add_trace(go.Scatter(
                    x=pd.concat([seg_forecast['Date'], seg_forecast['Date'][::-1]]),
                    y=pd.concat([seg_forecast['UpperCI'], seg_forecast['LowerCI'][::-1]]),
                    fill='toself', fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)',
                    line=dict(color='rgba(255,255,255,0)'), name=f'{segment} — 95% CI', showlegend=True,
                ))

        fig.update_layout(title=f'{horizon}-Month Forecast', yaxis_title='Sales ($)', height=460,
                           legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig, width='stretch')

        st.subheader('Forecast values & accuracy')
        cols = st.columns(len(segments))
        for i, segment in enumerate(segments):
            seg_forecast = forecasts[(forecasts['Segment'] == segment) & (forecasts['MonthAhead'] <= horizon)]
            seg_metrics = metrics[metrics['Segment'] == segment].iloc[0]
            with cols[i]:
                st.markdown(f'**{segment}**')
                st.dataframe(
                    seg_forecast[['Date', 'Forecast']].assign(Forecast=lambda d: d['Forecast'].round(0)).set_index('Date'),
                    width='stretch',
                )
                m1, m2 = st.columns(2)
                m1.metric('MAE', f"${seg_metrics['MAE']:,.0f}")
                m2.metric('RMSE', f"${seg_metrics['RMSE']:,.0f}")

        st.caption('MAE/RMSE computed by holding out the last 3 known months as a test set and comparing SARIMA\'s prediction against real sales for those months — the same evaluation approach used in Task 3.')

        all_forecasts = forecasts[forecasts['Segment'].isin(segments) & (forecasts['MonthAhead'] <= horizon)]
        st.download_button('Download forecast data (CSV)', all_forecasts.to_csv(index=False), 'forecasts.csv')

# ============================================================
# PAGE 3 — ANOMALY REPORT
# ============================================================
elif page == 'Anomaly Report':
    page_header('Anomaly Report', 'MONITORING', 'Weekly sales, 2015–2018 — flagged by two independent detection methods')

    anomalies = load_csv('anomalies.csv', parse_dates=['Week'])

    z_thresh = st.slider('Z-score sensitivity (lower = more anomalies flagged)', 1.0, 3.0, 2.0, 0.1)
    anomalies['zscore_anomaly_live'] = anomalies['z_score'].abs() > z_thresh

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anomalies['Week'], y=anomalies['Sales'], mode='lines', name='Weekly Sales',
                              line=dict(color=STEEL, width=1.8)))

    iso_pts = anomalies[anomalies['iso_anomaly']]
    fig.add_trace(go.Scatter(x=iso_pts['Week'], y=iso_pts['Sales'], mode='markers', name='Isolation Forest anomaly',
                              marker=dict(color=MAROON, size=11, symbol='circle', line=dict(width=1, color='white'))))

    z_pts = anomalies[anomalies['zscore_anomaly_live']]
    fig.add_trace(go.Scatter(x=z_pts['Week'], y=z_pts['Sales'], mode='markers', name=f'Z-score anomaly (|z| > {z_thresh})',
                              marker=dict(color=GOLD, size=11, symbol='triangle-up', line=dict(width=1, color='white'))))

    fig.update_layout(title='Weekly Sales — Detected Anomalies', yaxis_title='Sales ($)', height=460,
                       legend=dict(orientation='h', y=1.12))
    st.plotly_chart(fig, width='stretch')

    k1, k2, k3 = st.columns(3)
    k1.metric('Isolation Forest flags', int(anomalies['iso_anomaly'].sum()))
    k2.metric(f'Z-score flags (|z| > {z_thresh})', int(anomalies['zscore_anomaly_live'].sum()))
    k3.metric('Agreement (both methods)', int((anomalies['iso_anomaly'] & anomalies['zscore_anomaly_live']).sum()))

    st.subheader('Detected anomaly weeks')
    method = st.radio('Method', ['Isolation Forest', 'Z-score', 'Both (agreement only)'], horizontal=True)

    if method == 'Isolation Forest':
        table = anomalies[anomalies['iso_anomaly']][['Week', 'Sales']]
    elif method == 'Z-score':
        table = anomalies[anomalies['zscore_anomaly_live']][['Week', 'Sales', 'z_score']]
    else:
        table = anomalies[anomalies['iso_anomaly'] & anomalies['zscore_anomaly_live']][['Week', 'Sales']]

    numeric_cols = table.select_dtypes(include='number').columns
    table[numeric_cols] = table[numeric_cols].round(2)
    st.dataframe(table.sort_values('Sales', ascending=False), width='stretch', hide_index=True)
    st.download_button('Download anomaly data (CSV)', table.to_csv(index=False), 'anomalies.csv')

# ============================================================
# PAGE 4 — PRODUCT DEMAND SEGMENTS
# ============================================================
elif page == 'Product Demand Segments':
    page_header('Product Demand Segments', 'SEGMENTATION', 'K-Means clustering (k=4) on total sales, growth rate, volatility, and average order value')

    clusters = load_csv('clusters.csv')

    cluster_choice = st.multiselect('Filter by segment', sorted(clusters['ClusterLabel'].unique()),
                                     default=sorted(clusters['ClusterLabel'].unique()))
    clusters_f = clusters[clusters['ClusterLabel'].isin(cluster_choice)]

    fig = px.scatter(clusters_f, x='PC1', y='PC2', color='ClusterLabel', text='Sub-Category',
                      size='TotalSales', size_max=42, color_discrete_sequence=DISCRETE_SEQUENCE,
                      hover_data={'GrowthRate': ':.1f', 'Volatility': ':,.0f', 'AvgOrderValue': ':,.0f'})
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
    fig.update_layout(title='Demand Clusters (PCA projection)', height=480, legend=dict(orientation='h', y=-0.15))
    st.plotly_chart(fig, width='stretch')

    st.subheader('Sub-categories by segment')
    display_cols = ['Sub-Category', 'ClusterLabel', 'TotalSales', 'GrowthRate', 'Volatility', 'AvgOrderValue']
    st.dataframe(
        clusters_f[display_cols].sort_values('ClusterLabel').round(1),
        width='stretch', hide_index=True,
    )
    st.download_button('Download cluster data (CSV)', clusters_f.to_csv(index=False), 'clusters.csv')

    st.subheader('Recommended stocking strategy')
    strategy = {
        'High Volume, Stable Demand': ('🟦', 'Standard reorder-point replenishment with steady safety stock — the revenue backbone; don\'t stock out, but no need for constant re-forecasting.'),
        'Growing Demand, Niche/High-Ticket': ('🟨', 'Track closely month-to-month and lean toward pre-ordering ahead of demand, given the strong growth trend — but verify order volume isn\'t too thin before over-committing inventory.'),
        'Low Volume, Stable Demand': ('🟩', 'Lean, infrequent restocking — low volatility means low risk of stockouts even with minimal safety stock.'),
        'Declining Demand, High Volatility': ('🟥', 'Reduce standing inventory and shift to just-in-time ordering — high volatility combined with a negative trend is the highest-risk profile for overstock.'),
    }
    for label, (icon, advice) in strategy.items():
        if label in cluster_choice:
            st.markdown(f'{icon} **{label}** — {advice}')
