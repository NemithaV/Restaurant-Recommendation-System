import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import plugins
from streamlit_folium import folium_static

# Load cleaned data
df = pd.read_csv('clean_data.csv')

# Load Similarity Matrix
sim_matrix = np.load('sim_matrix.npz')
sim_matrix = sim_matrix['a']


st.sidebar.markdown("<h2 style = 'text-align : center;'><em>Visual Analytics -- ITCS5122</em></h2>", unsafe_allow_html=True)

home_menu = st.sidebar.radio(
    'Select an option:',
    ('Home','Recommendation System')
)


names = list(df['Name'].unique())
default_ix = names.index('Maywood Pancake house')


def recommend(name, state, city):
    if name in df['Name'].values:
        # Get index
        index = df[(df['Name'] == name) & (df['state'] == state) & (df['city'] == city)].index[0]
        # Get recommendation scores
        scores = dict(enumerate(sim_matrix[index]))
        # Sort scores
        sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

        selected_index = [idx for idx, scores in sorted_scores.items()]
        selected_score = [scores for idx, scores in sorted_scores.items()]

        rec_res = df.iloc[selected_index]
        rec_res['similarity'] = selected_score

        recommendation = rec_res.reset_index(drop=True)
        return recommendation[:11]


####################################################################
# streamlit
##################################################################


if home_menu == "Home":
    st.markdown("<h1 style = 'text-align : center;'>RESTAURANT RECOMMENDATION SYSTEM<h1>", unsafe_allow_html=True)
    st.image("home_page_image.jpg")

    with st.expander("MEMBERS"):
        st.subheader("GROUP 11")
        col1, col2 = st.columns(2)
        with col1:
            """
                * Nemitha Vudaru             
                * Preethi Nallamothu        
                * Aalugupalli Abhiram Reddy
                * Jaswanth Tumati
            """
        with col2:
            """
                * 801255073
                * 801273372
                * 801268168
                * 801274978
            """
        

    st.markdown("<hr />" +
                "<h3>MOTIVES<h3>" +
                "<ul>" + 
                "<li>Planning a trip is most complicated these days and also expensive. It&#39;s not easy to find a new restaurant in a new place.</li>" +
                "<li>TripAdvisor aim is to decrease the stress by giving restaurant suggestions along with menu and user reviews.</li>" +
                "<li>Based on their unique needs, the dataset will let clients find a restaurant that satisfies those needs swiftly and effectively.</li>" +
                "</ul>", unsafe_allow_html=True)

    st.markdown("<hr />" +
                "<h3 >GOAL</h3>" +
                "<p>The primary goal of this information is to recommend restaurants to people visiting that location. The dataset will assist clients in quickly and effectively locating a restaurant that meets their demands based on their individual requirements. Time will be saved, and it will be simple to choose from several possibilities at once.</p>", unsafe_allow_html=True)






if home_menu == "Recommendation System":

    st.sidebar.header("Search")
    name_ = st.sidebar.selectbox(
        "Restaurant", names, index=default_ix
    )

    states = df[df['Name'] == name_]['state'].unique()
    state_ = st.sidebar.selectbox(
        "State", states
    )

    cities = df[(df['Name'] == name_) & (df['state'] == state_)]['city'].unique()
    city_ = st.sidebar.selectbox(
        "City ", cities
    )
    
    st.header('Restaurants Recommendation System ')

    st.image("https://images.unsplash.com/photo-1600891964599-f61ba0e24092?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80")
    

    about_df = df[(df['Name'] == name_) & (df['state'] == state_) & (df['city'] == city_)]
    about_name = about_df['Name'].values[0]
    about_location = about_df['Location'].values[0]
    about_type = about_df['Type'].values[0]
    about_review = str(about_df['Reviews'].values[0])
    about_comment = about_df['Comments'].values[0]
    about_contact = about_df['Contact Number'].values[0]
    about_Price_Range = about_df['Price_Range'].values[0]

    st.sidebar.markdown("<p>&nbsp;</p><hr />", unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style = 'text-align : center;'><strong>ABOUT THE RESTAURANT</strong></h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>NAME: </strong>" + about_name + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>LOCATION: </strong>" + about_location + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>REVIEW: </strong>" + about_review + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>CONTACT: </strong>" + about_contact + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>TYPE: </strong>" + about_type + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>COMMENT: </strong>" + str(about_comment) + '. </p>', unsafe_allow_html=True)
    st.sidebar.markdown("<p><strong>PRICE RANGE: </strong>" + str(about_Price_Range) + '. </p>', unsafe_allow_html=True)


    if st.button('Show Recommendations'):
        df_recommend = recommend(name_, state_, city_)
        final_df = df_recommend[1:]

        # Restaurant latitude and longitude values
        latitude = df_recommend['lat'][0]
        longitude = df_recommend['lon'][0]

        # create map and display it
        rest_map = folium.Map(location=[latitude, longitude], zoom_start=6)

        # display the map of restaurant
        rest_map.add_child(
            folium.features.CircleMarker(
                [latitude, longitude],
                radius=5,  # define how big you want the circle markers to be
                color='yellow',
                fill=True,
                fill_color='Red',
                fill_opacity=0.8
            )
        )
        label = df_recommend['Name'][0]
        folium.Marker([latitude, longitude], popup=label, icon=folium.Icon(color='red')).add_to(rest_map)

        # instantiate a mark cluster object for the incidents in the dataframe
        restaurants = plugins.MarkerCluster().add_to(rest_map)

        # loop through the dataframe and add each data point to the mark cluster
        for lat, lng, label in zip(final_df['lat'], final_df['lon'], final_df['Name']):
            folium.Marker(
                location=[lat, lng],
                icon=None,
                popup=label
            ).add_to(restaurants)


        # display table
        st.subheader("Top 10 Recommended Restaurants")
        st.dataframe(data=final_df[['Name', 'Street Address', 'Location', 'Type', 'Contact Number', 'Reviews', 'Comments', 'Price_Range']])

        # display map
        st.subheader('Map of Restaurants')
        st.markdown("Red Icon: Restaurant's location ")
        st.markdown("Blue Icon: Recommended Restaurants")
        folium_static(rest_map)



