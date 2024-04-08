from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase app
cred = credentials.Certificate("chandu_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection("Object Detection and Distance Estimation")


# Route to fetch data from Firestore and render template
@app.route("/")
def index():
    print("ashwani hii")
    objects = []
    docs = collection_ref.stream()
    for index, doc in enumerate(docs, start=1):
        obj_data = doc.to_dict()
        obj_data['index'] = index
        objects.append(obj_data)

    # Sort objects based on timestamp
    objects.sort(key=lambda x: x['timestamp'])

    return render_template("index.html", objects=objects)


if __name__ == "__main__":
    app.run(debug=True)
