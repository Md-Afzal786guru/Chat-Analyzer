import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize session state for popup
if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False

# Function to display rules and regulations
def show_popup():
    st.markdown("## 📜 Rules & Regulations")
    st.markdown("""
    1. This tool is for personal chat analysis only.
    2. We do not store any uploaded data.
    3. Ensure the uploaded file follows the correct format (.txt).
    4. The analysis results are based on the provided chat data.
    5. By proceeding, you agree to these terms.
    """)
    if st.button("✅ Accept & Proceed"):
        st.session_state.accepted_terms = True
        st.rerun()

# Show popup if terms not accepted
if not st.session_state.accepted_terms:
    show_popup()
else:
    def apply_theme(theme):
        if theme == "Dark":
            st.markdown(
                """
                <style>
                .main { background-color: #0a0a0a; color: #ffffff; }
                h1, h2, h3, h4, h5, h6, p, label { color: #ffd700; font-weight: bold; }
                .stButton>button, .stDownloadButton>button {
                    background-color: #1e1e1e; color: #ffd700; border-radius: 8px; 
                    padding: 12px 24px; font-weight: bold; border: 2px solid #ffd700;
                }
                .stTextInput>div>div>input, .stTextArea>div>div>textarea {
                    background-color: #1e1e1e; color: #ffffff; border: 1px solid #ffd700;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <style>
                .main { background-color: #f0f2f6; color: #000000; }
                h1, h2, h3, h4, h5, h6, p, label { color: #4b0082; font-weight: bold; }
                .stButton>button, .stDownloadButton>button {
                    background-color: #4b0082; color: #ffffff; border-radius: 8px;
                    padding: 12px 24px; font-weight: bold; border: 2px solid #4b0082;
                }
                .stTextInput>div>div>input, .stTextArea>div>div>textarea {
                    background-color: #ffffff; color: #0a0a0a; border: 1px solid #000000;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

    st.sidebar.title("🚀 WhatsApp Chat Analyzer")
    st.sidebar.markdown("---")

    theme = st.sidebar.radio("🎨 Choose Theme", ["Light", "Dark"])
    apply_theme(theme)

    # File upload validation
    uploaded_file = st.sidebar.file_uploader("📂 Upload a WhatsApp chat file", type=["txt"])
    
    if uploaded_file is not None:
        if not uploaded_file.name.endswith(".txt"):
            st.sidebar.warning("⚠️ Please upload a valid **.txt** file!")
        else:
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            df = preprocessor.preprocess(data)

            user_list = df['user'].unique().tolist()
            if 'group_notification' in user_list:
                user_list.remove('group_notification')
            user_list.sort()
            user_list.insert(0, "Overall")

            selected_user = st.sidebar.selectbox("📊 Show analysis for", user_list)

            if st.sidebar.button("🔍 Show Analysis"):
                num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

                st.title("📊 Chat Analysis Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💬 Total Messages", num_messages)
                col2.metric("📝 Total Words", words)
                col3.metric("📷 Media Shared", num_media_messages)
                col4.metric("🔗 Links Shared", num_links)

                st.title("📅 Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='#e63946', linewidth=2)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                st.title("🔥 Weekly Activity Heatmap")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, cmap="magma", ax=ax)
                st.pyplot(fig)

                st.title("☁️ WordCloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig)

                st.sidebar.markdown("---")
                st.sidebar.header("📥 Export Data")
                csv = df.to_csv(index=False)
                st.sidebar.download_button(
                    label="⬇️ Download Analyzed Data",
                    data=csv,
                    file_name="analyzed_data.csv",
                    mime="text/csv"
                )
                st.markdown("---")
                st.write("👨‍💻 Developed by: [Md Afzal]")
