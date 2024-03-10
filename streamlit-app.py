import pandas as pd
from datetime import datetime
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from configs.constants import Constants as c
import services.data_services as ds

# Config
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Header
st.title("Indiemart Dashboard")

# Main
# Connect to the SQLite database
conn = sqlite3.connect('./indiemart.db')
# Get item_latest_price_df
item_latest_price_df = ds.get_item_latest_price(conn)
# Get count_item_per_category 
count_item_per_category = ds.get_count_item_per_category(item_latest_price_df)
# Get count_item_per_source 
count_item_per_source = ds.get_count_item_per_source(item_latest_price_df)
# avg_latest_price_per_category
avg_latest_price_per_category = ds.get_avg_latest_price_per_category(item_latest_price_df)

# Create a container for main metrics summary
with st.container(border=True):
    st.markdown("### Items Availability")
    main_cols = st.columns(3)
    with main_cols[0]:
        # Metrics of total item available
        with st.container(border=True):
            st.metric(
                label="Item",
                value=f"""{count_item_per_category["count_product"].sum():,}"""
            )
    with main_cols[1]:
        # Metrics of total item category available
        with st.container(border=True):
            st.metric(
                label="Category",
                value=f"""{count_item_per_category.shape[0]}"""
            )
    with main_cols[2]:
        # Metrics of total source
        with st.container(border=True):
            st.metric(
                label="Source",
                value=f"""{count_item_per_source.shape[0]}"""
            )
    with st.expander("Items Details", expanded=False):
        # Create a container for other metrics
        with st.container():
            secondary_cols = st.columns([3,2,3])
            with secondary_cols[0]:
                # Item categories
                st.markdown("### Item Categories")
                # Create a pie chart figure
                item_category_pie_fig = px.pie(
                    count_item_per_category,
                    values="count_product",
                    names="category"
                )
                st.plotly_chart(item_category_pie_fig, use_container_width=True)
            with secondary_cols[1]:    
                # Item sources
                st.markdown("### Item Sources")
                # Create a pie chart figure
                item_source_pie_fig = px.pie(
                    count_item_per_source,
                    values="count_product",
                    names="source"
                )
                st.plotly_chart(item_source_pie_fig, use_container_width=True)
            with secondary_cols[2]:    
                # Average latest price
                st.markdown("### Average latest price")
                # Create a bar chart figure
                avg_latest_price_bar_fig = go.Figure(
                    data = [
                        go.Bar(
                            name="price",
                            x=avg_latest_price_per_category["category"],
                            y=avg_latest_price_per_category["price"],
                            orientation='v'
                        ),
                        go.Bar(
                            name="discount_price",
                            x=avg_latest_price_per_category["category"],
                            y=avg_latest_price_per_category["discount_price"],
                            orientation='v'
                        )
                    ]
                )
                st.plotly_chart(avg_latest_price_bar_fig, use_container_width=True)

# Get count_item_per_category 
count_item_per_category_indo = ds.get_count_item_per_category(item_latest_price_df, "klikindomaret")
count_item_per_category_alfa = ds.get_count_item_per_category(item_latest_price_df, "alfagift")
# Get compare items list
compare_items = ds.get_compare_items(item_latest_price_df)
# Get last price per category
avg_lp_per_category_alfagift, avg_lp_per_category_klikindomaret = ds.get_avg_latest_price_compare_source_per_category(item_latest_price_df, compare_items)

with st.container(border=True):
    st.markdown("### Source store comparison")
    third_cols = st.columns([1,5])
    with third_cols[1]:
        tabs = st.tabs[
            "Product Diversity",
            "Product Prices",
            "Discounts"
        ]
        with tabs[0]:
            # Create a bar chart figure
            product_diversity_bar_fig = go.Figure(
                data = [
                    go.Bar(
                        name="klikindomaret",
                        x=count_item_per_category_indo["category"],
                        y=count_item_per_category_indo["count_product"],
                        orientation='v'
                    ),
                    go.Bar(
                        name="alfagift",
                        x=count_item_per_category_alfa["category"],
                        y=count_item_per_category_alfa["count_product"],
                        orientation='v'
                    )
                ]
            )
            st.plotly_chart(product_diversity_bar_fig, use_container_width=True)
        with tabs[1]:
            # Create a bar chart figure
            product_price_bar_fig = go.Figure(
                data = [
                    go.Bar(
                        name="klikindomaret",
                        x=avg_lp_per_category_klikindomaret["category"],
                        y=avg_lp_per_category_klikindomaret["price"],
                        orientation='v'
                    ),
                    go.Bar(
                        name="alfagift",
                        x=avg_lp_per_category_alfagift["category"],
                        y=avg_lp_per_category_alfagift["price"],
                        orientation='v'
                    )
                ]
            )
            st.plotly_chart(product_diversity_bar_fig, use_container_width=True)
            st.markdown(f"""* _Only compare {len(compare_items)} items that's available in bith store._""")

    