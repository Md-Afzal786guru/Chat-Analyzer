import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# Function to display rules and regulations
def show_popup():
    st.markdown("## 📝 Rules & Regulations ⚖️")
    st.markdown("""
    1️⃣ This tool is for **personal chat analysis** only.  
    2️⃣ We **do not store** any uploaded data. 🔒  
    3️⃣ Ensure the uploaded file is in the **.txt** format. 📎  
    4️⃣ The analysis is based **only on the provided chat data**. 📊  
    5️⃣ By proceeding, you **agree to these terms**. ✅  
    """)
    if st.button("✅ Accept & Proceed"):
        st.session_state.accepted_terms = True
        st.rerun()

# Apply theme
def apply_theme():
    if st.session_state.theme == "Dark":
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

# Show popup if terms not accepted
if not st.session_state.accepted_terms:
    show_popup()
else:
    st.sidebar.title("🚀 WhatsApp Chat Analyzer")
    st.sidebar.markdown("---")

    # Theme selection
    st.session_state.theme = st.sidebar.radio("🎨 Choose Theme", ["Light", "Dark"], index=0)
    apply_theme()

    # File upload validation
    uploaded_file = st.sidebar.file_uploader("📂 Upload a WhatsApp chat file", type=["txt"])
    
    if uploaded_file is not None:
        if not uploaded_file.name.endswith(".txt"):
            st.sidebar.warning("⚠️ Please upload a valid **.txt** file! 🚫")
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

                st.title("📊 Chat Analysis Summary 📝")
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

                # Daily timeline
                st.title("📆 Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#003f88', linewidth=2)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # Activity map
                st.title("🗺️ Activity Map")
                col1, col2 = st.columns(2)

                with col1:
                    st.header("📌 Most Active Days")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='#ff006e')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.header("📆 Most Active Months")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='#8338ec')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                # Weekly activity heatmap
                st.title("🔥 Weekly Activity Heatmap")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, cmap="magma", ax=ax)
                st.pyplot(fig)

                # Busiest users (Group level)
                if selected_user == "Overall":
                    st.title("🏆 Most Active Users")
                    x, new_df = helper.most_busy_users(df)
                    col1, col2 = st.columns(2)
                    with col1:
                        fig, ax = plt.subplots()
                        ax.bar(x.index, x.values, color='#d90429')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)

                    # Display the most active user
                    most_active_user = x.idxmax()
                    st.markdown(f"### 🏆 Most Active User: **{most_active_user}**")
                    st.markdown(f"**{most_active_user}** sent the most messages in the group, with a total of **{x.max()}** messages.")

                # WordCloud
                st.title("☁️ WordCloud")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig)

                # Most common words
                most_common_df = helper.most_common_words(selected_user, df)
                st.title("🔤 Most Common Words")
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1], color='#4361ee')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # Emoji analysis
                emoji_df = helper.emoji_list(selected_user, df)
                st.title("😂 Emoji Analysis")
                col1, col2 = st.columns(2)

                if emoji_df.empty:  # Check if the DataFrame is empty
                    st.warning("This person did not send any emojis.")
                else:
                    with col1:
                        st.dataframe(emoji_df)
                    with col2:
                        fig, ax = plt.subplots()
                        ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f",
                               colors=['#ffbe0b', '#fb5607', '#ff006e', '#8338ec', '#3a86ff'])
                        st.pyplot(fig)

                # Most Active Hours of the Day
                st.title("🕑 Most Active Hours")
                active_hours = helper.most_active_hours(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(active_hours.index, active_hours.values, color='#ff5733')
                ax.set_xlabel("Hour of the Day")
                ax.set_ylabel("Number of Messages")
                ax.set_title("Messages by Hour of the Day")
                plt.xticks(range(24))
                st.pyplot(fig)

                # Download analyzed data
                st.sidebar.markdown("---")
                st.sidebar.header("📅 Export Data")
                csv = df.to_csv(index=False)
                st.sidebar.download_button(
                    label="⬇️ Download Analyzed Data",
                    data=csv,
                    file_name="analyzed_data.csv",
                    mime="text/csv"
                )

                # Add timestamp for analysis completion
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.sidebar.markdown(f"🕚 **Last Analysis:** `{current_time}`")

                st.markdown("---")
                st.write("👨‍💻 Developed by: **Md Afzal** 💡")