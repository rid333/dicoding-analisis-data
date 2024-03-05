import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
day_df = pd.read_csv('day.csv')
# Hapus kolom yang tidak diperlukan
day_df = day_df.drop(['instant', 'atemp', 'windspeed', 'holiday', 'weekday'], axis=1)

# Rename data
season_labels = {
        1:"springer", 
        2:"summer", 
        3:"fall", 
        4:"winter"
        }
yr_labels = {
        0: 2011,
        1: 2012
        }
weather_labels = {
        1: 'Clear/Few clouds',
        2: 'Mist/Cloudy',
        3: 'Light Snow/Rain',
        4: 'Heavy Rain/Snow/Fog'
        }
month_labels = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
        }
# Rename kolom
day_df['season'] = day_df['season'].map(season_labels)
day_df['yr'] = day_df['yr'].map(yr_labels)
day_df['weathersit'] = day_df['weathersit'].map(weather_labels)
day_df['mnth'] = day_df['mnth'].map(month_labels)

# Ubah tipe data dteday jari datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Ubah tipe data season, yr, weathersit, mnth jadi kategorikal
day_df['season'] = day_df['season'].astype('category')
day_df['yr'] = day_df['yr'].astype('category')
day_df['weathersit'] = day_df['weathersit'].astype('category')
day_df['mnth'] = day_df['mnth'].astype('category')
day_df['workingday'] = day_df['workingday'].astype('category')

# Menyiapkan daily_rentals_df
def daily_rentals_df(df):
    return df.groupby('dteday', observed=True).agg({'cnt':'sum'}).reset_index()

# Menyiapkan daily_rentals_casual_df
def daily_rentals_casual_df(df):
    return df.groupby('dteday', observed=True).agg({'casual':'sum'}).reset_index()

# Menyiapkan daily_rentals_registered_df
def daily_rentals_registered_df(df):
    return df.groupby('dteday', observed=True).agg({'registered':'sum'}).reset_index()

# Menyiapkan monthly_rentals_df
def monthly_rentals_df(df):
    df['month_year'] = df['dteday'].dt.strftime('%B %Y')
    return df.groupby('month_year', observed=True)['cnt'].sum().reset_index().assign(month_year=lambda x: pd.to_datetime(x['month_year'], format='%B %Y')).sort_values('month_year').set_index('month_year')


# Menyiapkan seaon_rentals_df
def season_rentals_df(df):
    return df.groupby('season', observed=True).agg({'cnt':'sum'}).reset_index()

# Menyiapkan year_rentals_df
def year_rentals_df(df):
    return df.groupby('yr', observed=True).agg({'cnt':'sum'}).reset_index()

# Menyiapkan weekday and workingday rentals
def weekly_rentals_df(df):
    return df.groupby('workingday', observed=True).agg({'cnt':'sum'}).rename(index={1: 'Not Holiday/Weekend', 0: 'Holiday/Weekend'})

# Menyiapkan weather_rentals_df
def weather_rentals_df(df):
    return df.groupby('weathersit', observed=True).agg({'cnt':'sum'}).reset_index()

min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    # Menambahkan Logo 
    st.image('https://storage.googleapis.com/kampusmerdeka_kemdikbud_go_id/mitra/mitra_e7e4d54b-6688-45e9-96a6-1a2e04be63a0.png')

    # Mengambil start date dan end date dari user input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]

# Menyiapkan data untuk plot
daily_rentals = daily_rentals_df(main_df)
daily_rentals_casual = daily_rentals_casual_df(main_df)
daily_rentals_registered = daily_rentals_registered_df(main_df)
monthly_rentals = monthly_rentals_df(main_df)
season_rentals = season_rentals_df(main_df)
weekly_rentals = weekly_rentals_df(main_df)
weather_rentals = weather_rentals_df(main_df)

st.header('Bike Sharing Rentals Dashboard')
st.subheader('Daily Rentals')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Rentals", value=daily_rentals['cnt'].sum())

with col2:
    st.metric(label="Total Casual Rentals", value=daily_rentals_casual['casual'].sum())

with col3:
    st.metric(label="Total Registered Rentals", value=daily_rentals_registered['registered'].sum())

# Plot Daily Rentals

st.subheader('Daily Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
        daily_rentals['dteday'], 
        daily_rentals['cnt'], 
        marker='o',
        linewidth=2,
        )
ax.tick_params(labelsize=15)
st.pyplot(fig)

# Plot Monthly Rentals

st.subheader('Monthly Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
        monthly_rentals.index, 
        monthly_rentals['cnt'], 
        marker='o',
        linewidth=4,
        )
ax.tick_params(labelsize=15)
st.pyplot(fig)

# Plot Seasonly and Weatherly Rentals
st.subheader('Seasonly and Weatherly Rentals')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
sns.barplot(x='season', y='cnt', data=season_rentals, ax=ax[0])
ax[0].set_title('Seasonly Rentals', fontsize=35)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
# Menampilkan jumlah di atas bar
for p in ax[0].patches:
    ax[0].annotate(format(p.get_height(), '.0f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 10), 
                   textcoords = 'offset points',
                   fontsize=20)

sns.barplot(x='weathersit', y='cnt', data=weather_rentals, ax=ax[1])
ax[1].set_title('Weatherly Rentals', fontsize=35)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
# Menampilkan jumlah di atas bar
for p in ax[1].patches:
    ax[1].annotate(format(p.get_height(), '.0f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 10), 
                   textcoords = 'offset points',
                   fontsize=20)
st.pyplot(fig)

# Plot Weekly Rentals
st.subheader('Weekdays and Weekend Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x=weekly_rentals.index, y='cnt', data=weekly_rentals, ax=ax)
ax.set_title('Weekdays and Weekend Rentals', fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
# Menampilkan jumlah di atas bar
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.0f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 10), 
                   textcoords = 'offset points',
                   fontsize=10)
st.pyplot(fig)

# Copyright
st.caption('Copyright © 2024 Alridho')
