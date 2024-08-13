mkdir neo4j_data
python3 create_dataset.py faculty.json neo4j_data/faculty.csv "id, name, position, researchInterest, email, phone, photoUrl"
python3 create_dataset.py faculty.json neo4j_data/institute.csv "affiliation.id, affiliation.name, affiliation.photoUrl" "id, name, photoUrl"
python3 create_dataset.py publications.json neo4j_data/keyword.csv "keywords.id, keywords.name" "id, name"
python3 create_dataset.py publications.json neo4j_data/publication.csv "id, title, venue, year, numCitations"
python3 create_dataset.py faculty.json neo4j_data/faculty_affiliation.csv "id, affiliation.id"
python3 create_dataset.py faculty.json neo4j_data/faculty_keyword.csv "id, keywords.id, keywords.score"
python3 create_dataset.py faculty.json neo4j_data/faculty_publication.csv "id, publications"
python3 create_dataset.py publications.json neo4j_data/publication_keyword.csv "id, keywords.id, keywords.score"
python3 GenerateNeo4jCSV_postprocess.py