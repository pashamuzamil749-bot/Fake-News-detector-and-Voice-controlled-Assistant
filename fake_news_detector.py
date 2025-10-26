import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import eli5

# Step 1: Load and clean dataset
@st.cache_data
def load_data():
    # Use absolute path to avoid FileNotFoundError
    csv_path = r"C:\Users\LENOVO\Desktop\Python programs\Python Developer Projects\fake_news_detector\news.csv"
    df = pd.read_csv(csv_path)
    df.dropna(inplace=True)
    df['label'] = df['label'].map({'REAL': 0, 'FAKE': 1})
    return df

df = load_data()

# Step 2: Vectorize text
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X = vectorizer.fit_transform(df['title'])
y = df['label']

# Step 3: Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

# Step 4: Evaluate model
accuracy = accuracy_score(y_test, model.predict(X_test))

# Step 5: Streamlit UI
st.title("📰 Fake News Detector")
st.write(f"Model Accuracy: *{accuracy:.2f}*")

# Show classification report
st.subheader("📊 Model Performance")
report = classification_report(y_test, model.predict(X_test), target_names=["Real", "Fake"], output_dict=True)
st.dataframe(pd.DataFrame(report).transpose())

# Show top influential words
st.subheader("🧠 Top Influential Words")
html_explanation = eli5.format_as_html(eli5.explain_weights(model, vec=vectorizer, top=20))
st.components.v1.html(html_explanation, height=400, scrolling=True)

# Single headline prediction
st.subheader("🔎 Single Headline Check")
user_input = st.text_input("Enter a news headline")

if user_input:
    input_vector = vectorizer.transform([user_input])
    prediction = model.predict(input_vector)[0]
    confidence = model.predict_proba(input_vector)[0][prediction]

    label = "Fake" if prediction == 1 else "Real"
    st.markdown(f"### Prediction: *{label}*")
    st.markdown(f"### Confidence: *{confidence:.2f}*")

# Batch CSV upload
st.subheader("📁 Batch Check (CSV Upload)")
batch_file = st.file_uploader("Upload CSV with 'title' column", type=["csv"])
if batch_file:
    try:
        batch_df = pd.read_csv(batch_file)
        if 'title' not in batch_df.columns:
            st.error("Uploaded CSV must contain a 'title' column.")
        else:
            batch_titles = batch_df['title'].dropna()
            batch_vectors = vectorizer.transform(batch_titles)
            batch_preds = model.predict(batch_vectors)
            batch_probs = model.predict_proba(batch_vectors)
            batch_confidences = [probs[pred] for probs, pred in zip(batch_probs, batch_preds)]

            batch_df['prediction'] = ["Fake" if p == 1 else "Real" for p in batch_preds]
            batch_df['confidence'] = [f"{c:.2f}" for c in batch_confidences]

            st.dataframe(batch_df)
            st.download_button("Download Results", batch_df.to_csv(index=False), "batch_predictions.csv", "text/csv")
    except Exception as e:
        st.error(f"Error processing file: {e}")