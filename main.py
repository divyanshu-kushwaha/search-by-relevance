import os

import pymongo
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from nltk.tokenize import word_tokenize

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
app = Flask(__name__)

# Connect to MongoDB Atlas
client = pymongo.MongoClient(MONGO_URI)
db = client["SixtyFour"]
collection = db["items"]


# Calculate relevance score based on our logic
def calculate_weight(record, query_tokens):
    primary_weight = 0
    secondary_weight = 0

    current_tokens = record.get("Title", "").lower()
    for token in query_tokens:
        if token in current_tokens:
            primary_weight += 1

    if record.get("ParentExists") == "N":
        secondary_weight += 2
    elif record.get("ParentExists") == "Y" and record.get("Child") == "N":
        secondary_weight += 1

    return primary_weight, secondary_weight


@app.route('/search', methods=['GET'])
def search():
    user_query = request.args.get('query', '')
    user_query_tokens = word_tokenize(user_query.lower())

    # Fetch all records from MongoDB
    all_records = list(collection.find())

    # Calculate relevance score for each record and store the results
    matching_records = []
    for record in all_records:
        weight = calculate_weight(record, user_query_tokens)
        matching_records.append((record, weight))

    # Sort matching records by relevance score in descending order
    matching_records.sort(key=lambda x: x[1], reverse=True)

    relevant_results = []
    for record, weight in matching_records:
        result = {
            "Title": record.get("Title", ""),
            "Category": record.get("Category", ""),
            "SubCategory": record.get("SubCategory", ""),
            "Frequency": record.get("Frequency", ""),
            "ParentExists": record.get("ParentExists", ""),
            "Child": record.get("Child", ""),
            "Discontinued": record.get("Discontinued", ""),
            "Weight": weight[0] + weight[1]
        }
        relevant_results.append(result)

    # Return all relevant results as JSON
    return jsonify(relevant_results)


if __name__ == '__main__':
    app.run(debug=True)
