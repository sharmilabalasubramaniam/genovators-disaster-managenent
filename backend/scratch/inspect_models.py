import joblib
import os

model_dir = r"c:\Users\sharm\OneDrive\Documents\Desktop\sahyat\backend\ml_models\disaster_models_unzipped"
models = ["cyclone_model.joblib", "earthquake_model.joblib", "flood_model.joblib", "landslide_model.joblib"]

for model_file in models:
    path = os.path.join(model_dir, model_file)
    print(f"--- {model_file} ---")
    try:
        model = joblib.load(path)
        print("Type:", type(model))
        if hasattr(model, "feature_names_in_"):
            print("Features:", model.feature_names_in_)
        elif hasattr(model, "n_features_in_"):
            print("Num Features:", model.n_features_in_)
        else:
            print("No feature information found directly.")
    except Exception as e:
        print("Error loading:", e)
