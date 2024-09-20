./google-cloud-sdk/bin/gcloud config set project gemini-435701
export GOOGLE_CLOUD_PROJECT=gemini-435701
./google-cloud-sdk/bin/gcloud auth login
streamlit run app.py