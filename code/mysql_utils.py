import mysql.connector
import logging
import pandas as pd

config = {
    'user': 'root',
    'password': '...', #removed for privacy
    'host': 'localhost',
    'database': 'academicworld',
    'raise_on_warnings': True
}


class MySQLDatabase:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.exception("Exception occurred")
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logging.exception(f"Failed to execute query: {error}")
            self.connection.rollback()
            return False

    def fetch_data(self, query, values=None):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()


#Extra Credit: 
def add_university_data():
    university_df_merged = pd.read_csv('/Users/antoine/Desktop/411Project/code/ec_data/university_df_merged.csv')
    university_df_merged = university_df_merged.where(pd.notnull(university_df_merged), None)
    
    with MySQLDatabase(config) as db:
        columns_to_add = {
            'univ_rank': 'FLOAT',
            'enrollment': 'FLOAT',
            'avg_sat': 'FLOAT',
            'avg_act': 'FLOAT',
            'city': 'VARCHAR(255)',
            'state': 'VARCHAR(255)',
            'latitude': 'FLOAT',
            'longitude': 'FLOAT'
        }
        for column, data_type in columns_to_add.items():
            check_column_query = f"""
            SELECT COUNT(*)
            FROM information_schema.columns 
            WHERE table_name='university' AND column_name='{column}';
            """
            db.execute_query(check_column_query)
            column_exists = db.cursor.fetchone()[0]

            if column_exists == 0:
                alter_table_query = f"""
                ALTER TABLE university
                ADD COLUMN {column} {data_type};
                """
                db.execute_query(alter_table_query)
            else:
                return
        
        for index, row in university_df_merged.iterrows():
            update_query = """
            UPDATE university
            SET univ_rank = %s, 
                enrollment = %s, 
                avg_sat = %s, 
                avg_act = %s, 
                city = %s, 
                state = %s, 
                latitude = %s, 
                longitude = %s
            WHERE name = %s;
            """
            values = (
                row['Univ_Rank'], 
                row['Enrollment'], 
                row['Avg_SAT'], 
                row['Avg_ACT'], 
                row['city'], 
                row['state'], 
                row['Latitude'], 
                row['Longitude'],
                row['University']
            )
            values = tuple(None if pd.isna(v) else v for v in values)
            db.execute_query(update_query, values)
    
    print("Latitude and longitude data added to the university table.")
add_university_data()


#Helper Function
def get_all_university_data():
    with MySQLDatabase(config) as db:
        query = """
            SELECT
                *
            FROM
                university 
        """
        result = db.fetch_data(query)
        return pd.DataFrame(result, columns=['id', 'name', 'photo_url', 'univ_rank', 'enrollment', 'avg_sat', 'avg_act', 'city', 'state', 'latitude', 'longitude'])

#Helper Function
def get_all_faculty_info():
    with MySQLDatabase(config) as db:
        query = """
            SELECT
                f.name AS faculty_name,
                f.photo_url AS faculty_photo_url,
                f.position AS faculty_position,
                f.email AS faculty_email,
                f.phone AS faculty_phone,
                u.name AS university_name,
                u.photo_url AS university_photo_url
            FROM
                faculty f
            JOIN
                university u ON f.university_id = u.id;
        """
        result = db.fetch_data(query)
        return pd.DataFrame(result, columns=['faculty_name', 'faculty_photo_url', 'faculty_position', 'faculty_email', 'faculty_phone', 'university_name', 'university_photo_url'])
#global value
faculty_info_df = get_all_faculty_info()

### CONSTRAINT (1st Database Technique)
def add_constraint():
    with MySQLDatabase(config) as db:
        query = """
            ALTER TABLE university_watchlist
            ADD CONSTRAINT unique_name UNIQUE (name)
        """
        if db.execute_query(query):
            logging.info("Unique constraint on 'name' added successfully")
        else:
            logging.error("Failed to add unique constraint on 'name'")

### WIDGET: Add To/Remove From Watchlist
def manage_watchlist(action, schools=None):
    with MySQLDatabase(config) as db:
        query = "SHOW TABLES LIKE 'university_watchlist'"
        if not bool(db.fetch_data(query)):
            query = (
                "CREATE TABLE `university_watchlist` ("
                "`name` varchar(512) NOT NULL,"
                "`photo_url` varchar(512) NOT NULL,"
                "`univ_rank` float,"
                "`enrollment` float,"
                "`avg_sat` float,"
                "`avg_act` float,"
                "`city` varchar(255),"
                "`state` varchar(255),"
                "`latitude` float,"
                "`longitude` float,"
                "PRIMARY KEY (`name`))"
            )
            db.execute_query(query)
            add_constraint()

        school_details = []
        if schools:
            query = """
                SELECT name, photo_url, univ_rank, enrollment, avg_sat, avg_act, city, state, latitude, longitude 
                FROM university 
                WHERE name IN (%s)
            """ % ', '.join(['%s'] * len(schools))
            result = db.fetch_data(query, tuple(schools))
            school_details = [
                {
                    'name': row[0],
                    'photo_url': row[1],
                    'univ_rank': row[2],
                    'enrollment': row[3],
                    'avg_sat': row[4],
                    'avg_act': row[5],
                    'city': row[6],
                    'state': row[7],
                    'latitude': row[8],
                    'longitude': row[9]
                }
                for row in result
            ]

        if action == 'add' and schools and school_details:
            for details in school_details:
                query = "SELECT COUNT(*) FROM university_watchlist WHERE name = %s"
                result = db.fetch_data(query, (details['name'],))
                if result and result[0][0] == 0:
                    query = """
                        INSERT INTO university_watchlist 
                        (name, photo_url, univ_rank, enrollment, avg_sat, avg_act, city, state, latitude, longitude) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    db.execute_query(query, (
                        details['name'], details['photo_url'], details['univ_rank'], details['enrollment'],
                        details['avg_sat'], details['avg_act'], details['city'], details['state'],
                        details['latitude'], details['longitude']
                    ))

        elif action == 'remove' and schools:
            for school in schools:
                query = "DELETE FROM university_watchlist WHERE name = %s"
                db.execute_query(query, (school,))

        query = "SELECT * FROM university_watchlist"
        result = db.fetch_data(query)
        df = pd.DataFrame(result, columns=['name', 'photo_url', 'univ_rank', 'enrollment', 'avg_sat', 'avg_act', 'city', 'state', 'latitude', 'longitude'])
        return df
    
### WIDGET: Add To Faculty Reach Out Remove From Reach Out
### TRIGGER (2nd Database Technique) 
def manage_faculty_watchlist(action, faculty_name):
    with MySQLDatabase(config) as db:
        if db.fetch_data("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'academicworld' AND table_name = 'faculty_watchlist';")[0][0] == 0:
            db.execute_query("""
                CREATE TABLE faculty_watchlist (
                    faculty_name VARCHAR(512) PRIMARY KEY,
                    university_name VARCHAR(512),
                    faculty_photo_url VARCHAR(512),
                    faculty_position VARCHAR(512),
                    faculty_email VARCHAR(512),
                    faculty_phone VARCHAR(512),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP        
                );
            """)

            db.execute_query("""
                CREATE TRIGGER update_timestamp
                BEFORE UPDATE ON faculty_watchlist
                FOR EACH ROW
                BEGIN
                    SET NEW.updated_at = NOW();
                END;
            """)

        if faculty_name in faculty_info_df['faculty_name'].values:
            specific_info = faculty_info_df[faculty_info_df['faculty_name'] == faculty_name].iloc[0]
            if action == "add":
                query = """
                INSERT INTO faculty_watchlist (faculty_name, university_name, faculty_photo_url, faculty_position, faculty_email, faculty_phone)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
                values = (specific_info['faculty_name'], specific_info['university_name'], specific_info['faculty_photo_url'], specific_info['faculty_position'], specific_info['faculty_email'], specific_info['faculty_phone'])
            elif action == "remove":
                query = "DELETE FROM faculty_watchlist WHERE faculty_name = %s;"
                values = (faculty_name,)
            else:
                return []

            if db.execute_query(query, values):
                query = "SELECT * FROM faculty_watchlist;"
                result = db.fetch_data(query)
                df = pd.DataFrame(result, columns=['faculty_name', 'university_name', 'faculty_photo_url', 'faculty_position', 'faculty_email', 'faculty_phone', 'updated_at'])
                return df
            else:
                return []
        else:
            print("Faculty name not found in DataFrame")
            return []

### WIDGET: Faculty Funding
### VIEW (3rd Database Technique)
def manage_faculty_fund_watchlist(total_budget):
    with MySQLDatabase(config) as db:
        create_view_query = """
        CREATE OR REPLACE VIEW faculty_fund_view AS
        SELECT
            u.photo_url,
            u.name AS university_name,
            u.univ_rank,
            u.enrollment,
            u.state,
            f.faculty_photo_url,
            f.faculty_name,
            f.faculty_position,
            f.faculty_email,
            f.faculty_phone,
            ({} / faculty_count.total_faculty) AS fund
        FROM
            faculty_watchlist f
        INNER JOIN
            university_watchlist u ON f.university_name = u.name
        INNER JOIN (
            SELECT university_name, COUNT(*) AS total_faculty
            FROM faculty_watchlist
            GROUP BY university_name
        ) faculty_count ON f.university_name = faculty_count.university_name;
        """.format(total_budget)

        if db.execute_query(create_view_query):
            logging.info("View created successfully")
        else:
            logging.error("Failed to create view")
        fetch_view_query = "SELECT * FROM faculty_fund_view;"
        result = db.fetch_data(fetch_view_query)
        return pd.DataFrame(result, columns=['photo_url', 'name', 'univ_rank', 'enrollment', 'state', 'faculty_photo_url', 'faculty_name', 'faculty_position', 'faculty_email', 'faculty_phone', 'fund'])

