from neo4j import GraphDatabase
import pandas as pd

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed", e)
    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

# Initialize the connection
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="...") #removed for privacy

#Helper Functions 
def all_keywords():
    query = '''
        MATCH (n:KEYWORD)
        RETURN n.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    keywords = [record['name'] for record in result]
    return keywords
keywords = [{'label': name, 'value': name} for name in all_keywords()]

def all_universities():
    query = '''
        MATCH (n:INSTITUTE)
        RETURN n.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    universities = [record['name'] for record in result]
    return universities
universities =  [{'label': name, 'value': name} for name in all_universities()]

def all_faculty():
    query = '''
        MATCH (f:FACULTY)
        RETURN f.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    faculties = [record['name'] for record in result]
    return faculties

faculties = [{'label': name, 'value': name} for name in all_faculty()]


### WIDGET: Displaying Top 10 Universities for Selected Keyword
def top_10_highest_avg_citations_keyword_year(keyword, start_year, end_year):
    query = '''
    MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) - [:PUBLISH] -> (p:PUBLICATION) - [:LABEL_BY] -> (k:KEYWORD)
    WHERE p.year >= {start_year} AND p.year <= {end_year} AND k.name CONTAINS "{keyword}"
    RETURN i1.photoUrl AS photoUrl, i1.name AS university, AVG(p.numCitations) AS average, COUNT(DISTINCT p) AS count
    ORDER BY average DESC
    LIMIT 10
    '''.format(start_year=start_year, end_year=end_year, keyword=keyword)
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'photoUrl': 'logo', 'name': 'university', 'average': 'average', 'count': 'count'}
    )
    return df

### WIDGET: Number Of Faculty Who Referenced [Keyword]
def num_fac_keyword(keyword, schools, start_year, end_year):
    schools_str = '", "'.join(schools)
    query = '''
        MATCH (f:FACULTY)-[:AFFILIATION_WITH]->(i:INSTITUTE),
            (f)-[:PUBLISH]->(p:PUBLICATION)-[:LABEL_BY]->(k:KEYWORD)
        WHERE k.name CONTAINS "{keyword}"
        AND p.year >= {start_year}
        AND p.year <= {end_year}
        AND i.name IN ["{schools}"]
        RETURN COUNT(DISTINCT f.id) AS num_faculty
    '''.format(keyword=keyword, start_year=start_year, end_year=end_year, schools=schools_str)
    result = conn.query(query, db='academicworld')
    num_fac = result[0]['num_faculty'] if result else 0
    return num_fac

### WIDGET: Number Of Publications Which Referenced [Keyword]
def num_pub_keyword(keyword, schools, start_year, end_year):
    schools_str = '", "'.join(schools)
    
    query = '''
        MATCH (f:FACULTY)-[:AFFILIATION_WITH]->(i:INSTITUTE),
              (f)-[:PUBLISH]->(p:PUBLICATION)-[:LABEL_BY]->(k:KEYWORD)
        WHERE k.name CONTAINS "{keyword}"
          AND p.year >= {start_year}
          AND p.year <= {end_year}
          AND i.name IN ["{schools}"]
        RETURN COUNT(DISTINCT p.id) AS num_publications
    '''.format(keyword=keyword, start_year=start_year, end_year=end_year, schools=schools_str)
    
    result = conn.query(query, db='academicworld')
    num_pub = result[0]['num_publications'] if result else 0
    return num_pub

def get_graph(faculty, keyword):
    query = '''
    MATCH (f:FACULTY {name: $faculty})-[:PUBLISH]->(p:PUBLICATION)<-[:PUBLISH]-(coauthor:FACULTY),
          (p)-[:LABEL_BY]->(k:KEYWORD),
          (coauthor)-[:AFFILIATION_WITH]->(coauthorInstitute:INSTITUTE)
    WHERE f <> coauthor AND k.name CONTAINS $keyword
    RETURN f.name AS FacultyName, coauthor.name AS CoauthorName, coauthorInstitute.name AS CoauthorInstituteName
    '''
    results = conn.query(query, parameters={'faculty': faculty, 'keyword': keyword}, db='academicworld')
    data = []
    for record in results:
        data.append(dict(record))

    return pd.DataFrame(data)