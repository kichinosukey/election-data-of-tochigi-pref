import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk


def gen_data(lon, lat, length):
    return pd.DataFrame({
        'lon': np.ones(length)*lon,
        'lat': np.ones(length)*lat,
        })


if __name__ == '__main__':

    # Overview
    st.title("栃木県知事選挙結果 平成28年")
    
    # Load data
    result = pd.read_csv('result.csv', index_col=0)
    for col in result.columns[1:-1]:
        result[col] = result[col].astype(int)
    loc = pd.read_csv('lon-lat.csv', index_col=0)
    
    result = pd.merge(result, loc, left_index=True, right_index=True)
    result.reset_index(inplace=True)
    result = result.rename(columns={'index': '市町名'})

    # Set widget
    column = st.selectbox('列を選んでください。', list(result.columns[2:-1]), 0)

    # Arrange data    
    dat_list = []
    for city in result['市町名'].unique():
        tmp = result.query('市町名 == @city')
        length = list(tmp[column])[0]
        if length > 1000:
            length = int(length/1000)
        lon, lat = list(tmp['lon'])[0], list(tmp['lat'])[0]
        data = gen_data(lon, lat, length)
        dat_list.append(data)
    data = pd.concat(dat_list)

    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": list(data['lat'])[0],
            "longitude": list(data['lon'])[0],
            "zoom": 11,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=500,
                elevation_scale=10,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ],
    ))

    # Plot by Altair
    st.altair_chart(alt.Chart(result)
        .mark_bar().encode(
            x=alt.X("市町名:O"),
            y=alt.Y("%s:Q" % column),
            tooltip=['市町名', column]
        ), use_container_width=True)

    if st.checkbox("Show raw data", False):
        st.write(result)