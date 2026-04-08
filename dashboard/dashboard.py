import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set konfigurasi halaman Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Fungsi untuk memuat dan membersihkan data (menggunakan cache agar lebih cepat)
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/day.csv")
    
    # Mengubah format tanggal
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Mapping Data (Sama seperti di Notebook)
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    df['season_name'] = df['season'].map(season_mapping)
    
    workingday_mapping = {0: 'Holiday/Weekend', 1: 'Working Day'}
    df['workingday_name'] = df['workingday'].map(workingday_mapping)
    
    month_mapping = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                     7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    df['month_name'] = df['mnth'].map(month_mapping)
    
    # Clustering/Binning untuk Suhu (Analisis Lanjutan)
    bins = [0, 0.33, 0.66, 1.0]
    labels = ['Rendah (Dingin)', 'Sedang (Sejuk)', 'Tinggi (Panas)']
    df['temp_group'] = pd.cut(df['temp'], bins=bins, labels=labels, include_lowest=True)
    
    return df

df = load_data()

# ==============================
# SIDEBAR (Filter Rentang Waktu)
# ==============================
min_date = df["dteday"].min()
max_date = df["dteday"].max()

with st.sidebar:
    st.header("🚲 Bike Sharing Data Dashboard")
    st.header("Filter Data")
    
    # Widget date_input untuk memfilter tanggal
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memfilter DataFrame utama berdasarkan input di sidebar
main_df = df[(df["dteday"] >= str(start_date)) & (df["dteday"] <= str(end_date))]


# ==============================
# MAIN PAGE (Konten Dashboard)
# ==============================
st.title("🚲 Bike Sharing Data Dashboard")

# Menampilkan metrik utama (KPI)
st.subheader("Daily Sharing Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rides", value=f"{main_df['cnt'].sum():,}")
with col2:
    st.metric("Total Casual Users", value=f"{main_df['casual'].sum():,}")
with col3:
    st.metric("Total Registered Users", value=f"{main_df['registered'].sum():,}")

st.divider()

# Visualisasi 1: Musim & Bulan
st.subheader("1. Performa Penyewaan: Musim dan Tren Bulanan")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

custom_colors = {'Spring': '#D3D3D3', 'Summer': '#D3D3D3', 'Fall': '#1f77b4', 'Winter': '#D3D3D3'}
sns.barplot(x='season_name', y='cnt', data=main_df, estimator=sum, errorbar=None, ax=ax[0], palette=custom_colors)
ax[0].set_title('Total Penyewaan Berdasarkan Musim', fontsize=15)
ax[0].set_xlabel('Musim', fontsize=12)
ax[0].set_ylabel('Total Penyewaan', fontsize=12)
ax[0].ticklabel_format(style='plain', axis='y')

sns.lineplot(x='month_name', y='cnt', data=main_df, estimator=sum, errorbar=None, marker='o', ax=ax[1], color='b')
ax[1].set_title('Tren Penyewaan per Bulan', fontsize=15)
ax[1].set_xlabel('Bulan', fontsize=12)
ax[1].set_ylabel('Total Penyewaan', fontsize=12)
ax[1].ticklabel_format(style='plain', axis='y')

st.pyplot(fig) # Menampilkan plot ke Streamlit


# Visualisasi 2: Casual vs Registered
st.subheader("2. Pola Penyewaan: Hari Kerja vs Hari Libur")
melted_df = pd.melt(main_df, id_vars=['workingday_name'], value_vars=['casual', 'registered'], 
                    var_name='User_Type', value_name='Average_Rentals')

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x='workingday_name', y='Average_Rentals', hue='User_Type', data=melted_df, errorbar=None, palette='Set2', ax=ax2)
ax2.set_title('Rata-rata Penyewaan: Casual vs Registered', fontsize=15)
ax2.set_xlabel('Tipe Hari', fontsize=12)
ax2.set_ylabel('Rata-rata Penyewaan', fontsize=12)
st.pyplot(fig2)


# Visualisasi 3: Clustering (Analisis Lanjutan)
st.subheader("3. Dampak Suhu terhadap Penyewaan (Clustering)")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(x='temp_group', y='cnt', data=main_df, palette='coolwarm', errorbar=None, ax=ax3)
ax3.set_title('Rata-rata Penyewaan Berdasarkan Kelompok Suhu', fontsize=15)
ax3.set_xlabel('Kelompok Suhu', fontsize=12)
ax3.set_ylabel('Rata-rata Total Penyewaan', fontsize=12)
st.pyplot(fig3)

st.caption("Copyright © Adriano Deshon 2026")