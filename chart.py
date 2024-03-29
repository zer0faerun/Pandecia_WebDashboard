from streamlit_echarts import st_echarts
import streamlit as st

def ytd_bar_chart(df):
    options = {
        "xAxis": {
            "type": "category",
            "data": df['month_year'].tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [{"data": df['total_net_sales'].tolist(), "type": "bar"}],
    }

    events = {
        "click": "function(params) { console.log(params.name); return params.name }",
        "dblclick": "function(params) { return [params.type, params.name, params.value] }",
    }

    st.subheader("YTD Sales")


    st_echarts(
        options=options, events=events, height="500px", key="render_basic_bar_events"
    )
    return
