import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


@st.cache_data
def load_data():
    df = pd.read_csv("air_quality.csv", parse_dates=["time"])
    df.set_index("time", inplace=True)  # Pastikan indeks adalah datetime
    return df

df = load_data()

# Sidebar untuk filter
with st.sidebar:
    st.sidebar.header("Filter")

    st.sidebar.subheader("Rentang Waktu")
    start_time = pd.Timestamp(st.sidebar.date_input("Tanggal Mulai", df.index.min().date()))
    end_time = pd.Timestamp(st.sidebar.date_input("Tanggal Akhir", df.index.max().date()))

    st.sidebar.subheader("Stasiun Pengukuran")
    all_stations = df['station'].unique().tolist()
    selected_stations = st.multiselect("Pilih Stasiun", options=all_stations, default=all_stations)

    st.caption('Copyright © nf.muzakki 2025')


# Filter dataset berdasarkan rentang waktu
df_filtered = df[(df.index >= start_time) & (df.index <= end_time)].copy()

# Dashboard Title
st.title("Dashboard Analisis Kualitas Udara")

st.subheader("Rata-rata PM2.5 berdasarkan Stasiun Pengukuran")
if not df_filtered.empty:
    # Hitung rata-rata PM2.5 untuk setiap stasiun dan urutkan dari yang tertinggi
    df_avg_pm25 = df_filtered.groupby('station', as_index=False)['PM2.5'].mean()
    df_avg_pm25 = df_avg_pm25.sort_values(by='PM2.5', ascending=True)  # Urut dari terendah ke tertinggi (karena barh)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Buat horizontal bar chart
    bars = ax.barh(df_avg_pm25['station'], df_avg_pm25['PM2.5'], color='skyblue')

    # Menambahkan label angka di ujung setiap bar
    for bar in bars:
        xval = bar.get_width() + 0.5  # Beri sedikit jarak
        ax.text(xval, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.1f}', ha='left', va='center', fontsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.set_ylabel("")
    ax.set_title("")

    st.pyplot(fig)
    
    # Menampilkan stasiun dengan PM2.5 tertinggi
    highest_station = df_avg_pm25.iloc[11]
    st.write(f"Stasiun dengan PM2.5 tertinggi selama periode terpilih adalah **{highest_station['station']}** dengan rata-rata **{highest_station['PM2.5']:.1f} µg/m³**.")
else:
    st.write("Tidak ada data dalam rentang waktu yang dipilih.")


st.subheader("Rata-rata Harian PM2.5 berdasarkan Stasiun Pengukuran")
if not df_filtered.empty:
    # Buat kolom hanya untuk tanggal (tanpa jam)
    df_filtered.index = pd.to_datetime(df_filtered.index)  # Pastikan indeks datetime
    df_filtered['date_only'] = df_filtered.index.date  

    # Filter data berdasarkan stasiun yang dipilih
    df_filtered_station = df_filtered[df_filtered['station'].isin(selected_stations)]

    if not df_filtered_station.empty:
        # Hitung rata-rata harian
        df_daily = df_filtered_station.groupby(['station', 'date_only'], as_index=False)['PM2.5'].mean()

        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=df_daily, x='date_only', y='PM2.5', hue='station', alpha=0.2, marker='', linestyle='-')

        ax.set_xlabel("")
        ax.set_ylabel("Rata-rata Harian PM2.5 (µg/m³)")
        ax.set_title("")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Tampilkan legend hanya jika lebih dari satu stasiun dipilih
        if len(selected_stations) > 1:
            ax.legend(title="Stasiun", bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            ax.legend_.remove()  # Hapus legend jika hanya satu stasiun

        # Format sumbu X agar lebih terbaca
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))  
        ax.tick_params(axis='x', rotation=20)  

        st.pyplot(fig)
    else:
        st.write("Tidak ada data untuk stasiun yang dipilih.")
else:
    st.write("Tidak ada data dalam rentang waktu yang dipilih.")

st.subheader("Korelasi Faktor Cuaca dengan PM2.5")
if not df_filtered.empty:
    corr_matrix = df_filtered[['PM2.5', "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    st.write(f"Faktor cuaca yang paling berkorelasi dengan PM2.5 adalah {corr_matrix['PM2.5'].drop('PM2.5').idxmax()}")
else:
    st.write("Tidak ada data dalam rentang waktu yang dipilih.")

