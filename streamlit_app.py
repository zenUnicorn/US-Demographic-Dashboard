# Required libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Configure the page
st.set_page_config(
    page_title="USA Population Trends",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Custom CSS
st.markdown("""
<style>
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

# Data import
population_data = pd.read_csv('data/us-population-census-2010-2019.csv')

# Sidebar configuration
with st.sidebar:
    st.title('🇺🇸 USA Population Trends')
    
    available_years = list(population_data.year.unique())[::-1]
    
    chosen_year = st.selectbox('Choose a year', available_years)
    year_data = population_data[population_data.year == chosen_year]
    sorted_year_data = year_data.sort_values(by="population", ascending=False)

    palette_options = ['blues', 'greens', 'reds', 'purples', 'oranges', 'greys']
    chosen_palette = st.selectbox('Choose a color palette', palette_options)

# Visualization functions

# Heatmap
def create_heat_map(data, y_axis, x_axis, color_var, color_scheme):
    heat_map = alt.Chart(data).mark_rect().encode(
            y=alt.Y(f'{y_axis}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{x_axis}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({color_var}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=color_scheme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        )
    # height=300
    return heat_map

# Choropleth map
def create_choropleth(data, location_col, color_col, color_scheme):
    map_plot = px.choropleth(data, locations=location_col, color=color_col, locationmode="USA-states",
                               color_continuous_scale=color_scheme,
                               range_color=(0, max(year_data.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    map_plot.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return map_plot

# Donut chart
def create_donut(value, label, color):
    color_map = {
        'blue': ['#29b5e8', '#155F7A'],
        'green': ['#27AE60', '#12783D'],
        'red': ['#E74C3C', '#781F16'],
        'purple': ['#8E44AD', '#4A235A']
    }
    chart_colors = color_map.get(color, ['#F39C12', '#875A12'])
    
    data = pd.DataFrame({
        "Category": ['', label],
        "Percentage": [100-value, value]
    })
    background = pd.DataFrame({
        "Category": ['', label],
        "Percentage": [100, 0]
    })
    
    chart = alt.Chart(data).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="Percentage",
        color= alt.Color("Category:N",
                        scale=alt.Scale(domain=[label, ''], range=chart_colors),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = chart.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{value} %'))
    background_chart = alt.Chart(background).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="Percentage",
        color= alt.Color("Category:N",
                        scale=alt.Scale(domain=[label, ''], range=chart_colors),
                        legend=None),
    ).properties(width=130, height=130)
    return background_chart + chart + text

# Convert population to text 
def format_population(number):
    if number > 1000000:
        if not number % 1000000:
            return f'{number // 1000000} M'
        return f'{round(number / 1000000, 1)} M'
    return f'{number // 1000} K'

# Calculation year-over-year population migrations
def compute_population_change(data, target_year):
    current_year = data[data['year'] == target_year].reset_index()
    previous_year = data[data['year'] == target_year - 1].reset_index()
    current_year['population_change'] = current_year.population.sub(previous_year.population, fill_value=0)
    return pd.concat([current_year.states, current_year.id, current_year.population, current_year.population_change], axis=1).sort_values(by="population_change", ascending=False)

###############
# Main dashboard
columns = st.columns((1.5, 4.5, 2), gap='medium')

with columns[0]:
    st.markdown('#### Population Changes')

    population_change_data = compute_population_change(population_data, chosen_year)

    if chosen_year > 2010:
        top_state = population_change_data.states.iloc[0]
        top_state_pop = format_population(population_change_data.population.iloc[0])
        top_state_change = format_population(population_change_data.population_change.iloc[0])
        
        bottom_state = population_change_data.states.iloc[-1]
        bottom_state_pop = format_population(population_change_data.population.iloc[-1])   
        bottom_state_change = format_population(population_change_data.population_change.iloc[-1])   
    else:
        top_state = bottom_state = '-'
        top_state_pop = bottom_state_pop = '-'
        top_state_change = bottom_state_change = ''
    
    st.metric(label=top_state, value=top_state_pop, delta=top_state_change)
    st.metric(label=bottom_state, value=bottom_state_pop, delta=bottom_state_change)
    
    st.markdown('#### Migration Trends')

    if chosen_year > 2010:
        growing_states = population_change_data[population_change_data.population_change > 50000]
        shrinking_states = population_change_data[population_change_data.population_change < -50000]
        
        growth_percentage = round((len(growing_states)/population_change_data.states.nunique())*100)
        shrink_percentage = round((len(shrinking_states)/population_change_data.states.nunique())*100)
        growth_chart = create_donut(growth_percentage, 'Population Growth', 'green')
        shrink_chart = create_donut(shrink_percentage, 'Population Decline', 'red')
    else:
        growth_percentage = shrink_percentage = 0
        growth_chart = create_donut(growth_percentage, 'Population Growth', 'green')
        shrink_chart = create_donut(shrink_percentage, 'Population Decline', 'red')

    chart_columns = st.columns((0.2, 1, 0.2))
    with chart_columns[1]:
        st.write('Growth')
        st.altair_chart(growth_chart)
        st.write('Decline')
        st.altair_chart(shrink_chart)

with columns[1]:
    st.markdown('#### Total Population Distribution')
    
    choropleth = create_choropleth(year_data, 'states_code', 'population', chosen_palette)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heat_map = create_heat_map(population_data, 'year', 'states', 'population', chosen_palette)
    st.altair_chart(heat_map, use_container_width=True)

with columns[2]:
    st.markdown('#### State Rankings')

    st.dataframe(sorted_year_data,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "State",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(sorted_year_data.population),
                     )}
                 )
    
    with st.expander('Information', expanded=True):
        st.write('''
            - Data Source: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
            - :blue[**Population Changes**]: States with significant population increase/decrease for the selected year
            - :blue[**Migration Trends**]: Percentage of states with annual population change exceeding 50,000
            - Developed with Streamlit
            ''')
