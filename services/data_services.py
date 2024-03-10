import pandas as pd
import streamlit as st
from datetime import datetime

# Untuk kembali ke directory utama
import sys
import os
sys.path.insert(
    0, 
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..'
        )
    )
)

from configs.constants import Constants as c

path = os.path.dirname(__file__)

@st.cache_data
def get_item_latest_price(_conn):
    sql_stmt = f"""
    WITH latest_prices AS (
        SELECT DISTINCT 
            items_id
            , MAX(price)
                OVER(
                    PARTITION BY items_id
                    ORDER BY created_at 
                    RANGE BETWEEN CURRENT ROW
                        AND UNBOUNDED FOLLOWING
                ) as price
        FROM prices
    ),
    latest_discount_prices AS (
        SELECT DISTINCT 
            items_id
            , MAX(discount_price)
                OVER(
                    PARTITION BY items_id
                    ORDER BY created_at 
                    RANGE BETWEEN CURRENT ROW
                        AND UNBOUNDED FOLLOWING
                ) as discount_price
        FROM discounts
    )
    SELECT 
        i.id
        , i.name
        , i.category 
        , i."source"
        , i.created_at as created_at_item
        , lp.price
        , ldp.discount_price
    FROM items i
    LEFT JOIN latest_prices lp
        ON i.id = lp.items_id 
    LEFT JOIN latest_discount_prices ldp
        ON i.id = ldp.items_id
    """
    latest_price_df = pd.read_sql(
        sql_stmt,
        _conn
    )
     ## Remap the item categories
    latest_price_df["category"] = latest_price_df["category"].replace(c.CATEGORY_VALUES_MAP)
    ## Remap the iten names
    latest_price_df["name"] = latest_price_df["name"].str.strip().replace(c.ITEM_NAME_VALUES_MAP)

    return latest_price_df

@st.cache_data
def get_count_item_per_category(item_df, source = 'All'):
    # Filter by source
    if source == 'All':
        source_df = item_df
    else:
        source_df = item_df[item_df["source"] == source]
    # Get result
    result_df = (
        source_df
        .groupby("category") # Group item by "category"
        [["name"]] # Select "name" column from the dataframe
        .nunique() # Count unique of each "category"
        .reset_index() # Reset index to put back "category" column
        .rename(columns={"name": "count_product"}) # Rename column
    )
    return result_df

@st.cache_data
def get_count_item_per_source(item_df):
    # Get result
    result_df = (
        item_df
        .groupby("source") # Group item by "source"
        [["name"]] # Select "name" column from the dataframe
        .nunique() # Count unique of each "source"
        .reset_index() # Reset index to put back "source" column
        .rename(columns={"name": "count_product"}) # Rename column
    )
    return result_df

@st.cache_data
def get_compare_items(item_df):
    # Get item_count data
    items_count_df = (
        item_df
        .groupby("name") # Group item by "name"
        [["id"]] # Select "id" column
        .count() # Count "id" based on "name"
        .sort_values(by="id", ascending=False) # Sort by descending order
        .reset_index() # Reset index to retake "name" column
        .rename(columns={"id":"count"}) # Rename column name
    )
    # Get compare_item list
    compare_items = (
        items_count_df
        [
            (items_count_df["count"] > 1) # Filter items count
        ]
        ["name"] # Select "name" series
        .to_list() # Convert to list
    )
    return compare_items

@st.cache_data
def get_avg_latest_price_per_category(latest_price_df):
    # Get avg latest price per category
    avg_lp_per_category = (
        latest_price_df
        .groupby("category")
        [["price", "discount_price"]]
        .mean()
        .apply(round)
        .reset_index()
    )
    return avg_lp_per_category

@st.cache_data
def get_avg_latest_price_compare_source_per_category(latest_price_df, compare_items):
    # Get avg latest price compare source per category
    ## Alfagift
    avg_lp_per_category_alfagift = (
        latest_price_df
        [
            (latest_price_df["source"] == "alfagift") &
            (latest_price_df["name"].isin(compare_items))
        ]
        .groupby("category")
        [["price"]]
        .mean()
        .apply(round)
        .reset_index()
    )
    ## Klik Indomarert
    avg_lp_per_category_klikindomaret = (
        latest_price_df
        [
            (latest_price_df["source"] == "klikindomaret") &
            (latest_price_df["name"].isin(compare_items))
        ]
        .groupby("category")
        [["price"]]
        .mean()
        .apply(round)
        .reset_index()
    )
    return avg_lp_per_category_alfagift, avg_lp_per_category_klikindomaret

@st.cache_data
def get_latest_price_per_category(latest_price_df, category):
    # Get latest price per category
    lp_per_category = (
        latest_price_df
        [
            (latest_price_df["category"] == category)
        ]
        [["price"]]
        .reset_index(drop=True)
        .rename(columns={"price":category})
    )
    return lp_per_category