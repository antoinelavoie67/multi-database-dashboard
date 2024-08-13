from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb://localhost:27017/')
db = client['academicworld']
faculty_collection = db['faculty']

### WIDGET: Faculty Research and Filter By University Watchlist
def get_top_faculty(research_interest, keyword, watchlist_schools):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.academicworld
    
    if watchlist_schools:
        pipeline = [
            {"$unwind": "$keywords"},
            {"$match": {"affiliation.name": {"$in": watchlist_schools}}},
            {"$match": {"keywords.name": {"$regex": keyword, "$options": "i"}}},
            {"$match": {"researchInterest": {"$regex": research_interest, "$options": "i"}}},
            {"$group": {
                "_id": "$id",
                "faculty_name": {"$first": "$name"},
                "faculty_position": {"$first": "$position"},
                "faculty_email": {"$first": "$email"},
                "faculty_phone": {"$first": "$phone"},
                "affiliation_name": {"$first": "$affiliation.name"},
                "faculty_photoUrl": {"$first": "$photoUrl"},
                "total_keyword_score": {"$sum": "$keywords.score"}
            }},
            {"$sort": {"total_keyword_score": -1}},
            {"$limit": 15}
        ]
        result = db.faculty.aggregate(pipeline)
    else:
        pipeline = [
            {"$unwind": "$keywords"},
            {"$match": {"keywords.name": {"$regex": keyword, "$options": "i"}}},
            {"$match": {"researchInterest": {"$regex": research_interest, "$options": "i"}}},
            {"$group": {
                "_id": "$id",
                "faculty_name": {"$first": "$name"},
                "faculty_position": {"$first": "$position"},
                "faculty_email": {"$first": "$email"},
                "faculty_phone": {"$first": "$phone"},
                "affiliation_name": {"$first": "$affiliation.name"},
                "faculty_photoUrl": {"$first": "$photoUrl"},
                "total_keyword_score": {"$sum": "$keywords.score"}
            }},
            {"$sort": {"total_keyword_score": -1}},
            {"$limit": 15}
        ]
        result = db.faculty.aggregate(pipeline)

    result_df = pd.DataFrame(list(result)).rename(
        columns={
            "_id": "faculty_id",
            "faculty_name": "faculty_name",
            "faculty_position": "faculty_position",
            "faculty_email": "faculty_email",
            "faculty_phone": "faculty_phone",
            "affiliation_name": "affiliation_name",
            "faculty_photoUrl": "faculty_photoUrl",
            "total_keyword_score": "total_keyword_score",
        }
    )
    return result_df