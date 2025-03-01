import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- 🌟 Streamlit Page Configurations ---
st.set_page_config(page_title="🚀 Data Sweeper", layout="wide")

# --- 🌟 Custom CSS for Enhanced UI ---
st.markdown("""
    <style>
        /* Dark mode with a sleek gradient background */
        body { background: linear-gradient(135deg, #1f1f1f, #121212); color: white; }

        /* Custom Card Styling */
        .block-container { 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            background: rgba(97, 212, 228, 0.85);
            backdrop-filter: blur(10px);
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 { color: #f8f9fa; text-transform: uppercase; letter-spacing: 1px; }

        /* Buttons */
        .stButton>button { 
            border: none; 
            border-radius: 8px; 
            background: linear-gradient(135deg, #0078D7, #005a9e); 
            color: white; 
            padding: 10px 20px; 
            font-size: 16px; 
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4); 
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover { background: linear-gradient(135deg, #005a9e, #003a6e); transform: scale(1.05); }

        /* DataFrame Table */
        .stDataFrame, .stTable { 
            border-radius: 10px; 
            overflow: hidden; 
            background-color: #1a1a1a;
        }

        /* Checkbox and Radio Button Colors */
        .stCheckbox>label, .stRadio>label { color: white; font-weight: bold; }

        /* Download Button */
        .stDownloadButton>button { 
            background: linear-gradient(135deg, #28a745, #218838);
            color: white; 
            transition: all 0.3s ease-in-out;
        }
        .stDownloadButton>button:hover { background: linear-gradient(135deg, #218838, #166b29); transform: scale(1.05); }

    </style>
""", unsafe_allow_html=True)

# --- 🚀 App Title & Description ---
st.title("🚀 Data Sweeper")
st.write("📊 **Transform and clean your CSV/Excel files effortlessly with built-in data visualization.**")

# --- 📁 File Uploader ---
uploaded_files = st.file_uploader("📁 **Upload CSV or Excel files:**", type=["csv", "xlsx"], accept_multiple_files=True)


# --- 🔄 File Processing Function ---
def process_file(file):
    file_extension = os.path.splitext(file.name)[-1].lower()
    
    try:
        # 📥 Load the File
        if file_extension == ".csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine="openpyxl")  

        # 🔄 Fix potential errors related to mixed data types
        df = df.convert_dtypes()
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str)

    except Exception as e:
        st.error(f"❌ Error processing {file.name}: {e}")
        return None

    # --- 📝 File Metadata ---
    with st.container():
        st.subheader(f"📄 File: {file.name}")
        col1, col2 = st.columns([2, 3])
        with col1:
            st.write(f"📏 **Size:** {file.size / 1024:.2f} KB")
        with col2:
            st.write(f"🔢 **Rows & Columns:** {df.shape[0]} rows × {df.shape[1]} columns")

    # 🏗 Preview Uploaded File
    with st.expander("🔍 **Preview Data**"):
        st.dataframe(df.head())

    # 📊 Data Summary
    if st.checkbox(f"📈 Show Data Summary for {file.name}"):
        st.write(df.describe())

    # 🛠 **Data Cleaning Options**
    st.subheader("🛠 Data Cleaning Options")
    if st.checkbox(f"Enable Cleaning for {file.name}"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🗑 Remove Duplicates ({file.name})"):
                initial_count = df.shape[0]
                df.drop_duplicates(inplace=True)
                st.success(f"✅ Removed {initial_count - df.shape[0]} duplicate rows.")
        with col2:
            if st.button(f"🛠 Fill Missing Values ({file.name})"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✅ Missing values filled with column means.")

    # 🎯 **Column Selection**
    st.subheader("🎯 Select Columns to Display")
    selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
    df = df[selected_columns]

    # 📊 **Visualization**
    st.subheader("📊 Data Visualization")
    if st.checkbox(f"📈 Show Visualization for {file.name}"):
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.shape[1] >= 1:
            st.bar_chart(numeric_df)
        else:
            st.warning("⚠ No numeric columns available for visualization.")

    # 🔄 **Conversion & Download**
    st.subheader("🔄 Convert & Download")
    conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
    
    if st.button(f"💾 Convert {file.name}"):
        buffer = BytesIO()
        file_name = file.name.replace(file_extension, f".{conversion_type.lower()}")
        mime_type = "text/csv" if conversion_type == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
        else:
            df.to_excel(buffer, index=False, engine="openpyxl")

        buffer.seek(0)

        st.download_button(
            label=f"⬇ Download {file.name} as {conversion_type}",
            data=buffer,
            file_name=file_name,
            mime=mime_type
        )

# --- 🏗 Process Each Uploaded File ---
if uploaded_files:
    for file in uploaded_files:
        process_file(file)

st.success("🎉 All files processed successfully!")
