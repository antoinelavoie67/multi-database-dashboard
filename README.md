**Title:** Faculty Research Funding Board

**Purpose:** This dashboard aims to provide public and private companies with valuable insights into university, faculty, and student-related statistics and relationships. It is designed for employees at companies interested in sponsoring academic research and the means to partner with faculty on research projects. These research opportunities, which I found extremely rewarding during my undergraduate experience, offer students hands-on, meaningful experiences while delivering significant value to companies. The objective of this dashboard is to foster and encourage these mutually beneficial collaborations.

**Demo:** [https://drive.google.com/file/d/11rDsmdN-6hnZs5sy_p_nMga618MOrvox/view?usp=sharing](https://drive.google.com/file/d/11rDsmdN-6hnZs5sy_p_nMga618MOrvox/view?usp=sharing)

**Installation:** The databases (MySQL, MongoDB, and Neo4J) used in this project followed where we left off with MP5. The program should handle the creation, maintenance, and manipulation of any data within these settings. Additional data extensions were implemented for extra-credit tasks, including:
- University-related statistics: Pulled from: [US News](https://www.kaggle.com/datasets/theriley106/university-statistics?resource=download)
- City-wide latitude and longitude data: Pulled from SimpleMaps [SimpleMaps](https://www.kaggle.com/datasets/sergejnuss/united-states-cities-database?resource=download)
These datasets are included in the codebase but will require path adjustments in “university_add_data.ipynb”. Furthermore, ensure that configurations and connections to the databases are correctly set up by replacing placeholders for usernames, passwords, etc.

**Usage:** After downloading all the code and adjusting configurations (usernames, passwords, paths, etc.) the user can run “python3 app.py” which will generate a browser link to populate the dashboard. The rest of the process should be easily figured out by trial and error but would be used most efficiently if the user already has a timeframe(s), keyword(s), and faculty research interest(s) in mind. By following a left-to-right, top-to-bottom process, and exploring all the widgets, a user will be left with a table that they can present including relevant university, faculty, and fund data. 

**Design:** This application is designed using Plotly for visualizations and more specifically Dash, which is a framework to help build apps centered around data. Through the row column structure in Dash I was able to build a rectangular dashboard with headers, inputs that interact with the user (selection dropdowns, buttons, and sliders), and change stylistic elements such as the font, colors, and border width. Each row (also indicated with comments in the code) in the dashboard focuses on a different aspect of the use case with:
- Row 1: Title and time selection
- Row 2: University exploration and watchlist creation
- Row 3: Faculty exploration and watchlist creation
- Row 4: Fund distribution and final table including elements from the previous rows

**Implementation:** The overall codebase (Python) follows what is suggested in the instructions document including “app.py”, “mysql_utils.py”, “neo4j_utils.py”, “mongodb_utils.py”, and “style.css” files. The “app.py” interacts with these database-specific files through a series of callbacks and these files each connect with their respective databases. Using Plotly for the US Map and Neo4j visualizations, pandas for data frames, regex for string comparisons, and Python notebooks for further data exploration and concatenation I was able to functionalize the program into a working dashboard. 

**Database Techniques:** All of the database techniques were implemented in the MySQL database and can be found within the “mysql_utls.py’ (also denoted with comments):
- **Constraint:** For the "university_watchlist" table in the "academicworld" database, I added a unique constraint to ensure that each university name is unique. 
- **Trigger:** This was added to the "faculty_watchlist" table to automatically update the timestamp whenever a record is modified. This ensures that the "updated_at" column reflects the most recent update time so that a user can see how their watchlist changes over time as more research is conducted.
- **View:** In order to join data from the "faculty_watchlist" and "university_watchlist" tables a view was created. This helped provide a consolidated view of all the important information from the previous widgets with the inclusion of a funding column based on a total budget. This view was beneficial because it reflected changes from any of the other watchlists and also allowed the user to flexibly update their funding.  

**Extra Credit 1:**
- I felt that the university table was lacking important information that potential sponsors might be interested in. To address this, I aimed to include a map of the universities, but obtaining the latitude and longitude coordinates proved challenging. I found two datasets that provided more information I wanted to add:
  - University-related statistics: Pulled from: [US News](https://www.kaggle.com/datasets/theriley106/university-statistics?resource=download)
  - City-wide latitude and longitude data: Pulled from SimpleMaps [SimpleMaps](https://www.kaggle.com/datasets/sergejnuss/united-states-cities-database?resource=download)
- I combined these datasets in my “university_add_data.ipynb” using pandas and mapped the information to the SQL database's university table so that when the university watchlist is created, it includes this additional information such as rank, enrollment numbers, average ACT and SAT scores, etc.
- Challenges faced and steps taken:
  - Naming Issues: Addressed inconsistencies between datasets
  - SQL Null Values vs. pd.NA: Handled differences between SQL null values and pandas NA.
  - Missing Data: Manually imputed latitude and longitude data for about 18/19 universities.
  - Debugging Plotly Graphs: Spent half a day debugging a bug with Plotly graphs failing to update on Dash callbacks more than once as the university_watchlist is updated. This is a common issue with limited solutions, so I chose to create a button instead to update the map.

**Extra Credit 2:**
- Given the use of three different databases, I wanted to explore the objective of multi-database querying to ensure information remains consistent across the dashboard for my use case. Using the “university_watchlist” table in MySQL, I was able to query all unique universities and use this output to then query MongoDB when the “Filter By University Watchlist” button is clicked. This process required extra data exploration, which I performed directly through the database platforms on my terminal. I also created tests in the “mono_sql_univ_comparison.ipynb” notebook to confirm my assumptions about data quality and consistency for the university variable. This whole process included Multi-Database Integration to ensure seamless querying across MySQL and MongoDB, data explorations to understand deeper structure and data consistency, and further testing/validation.  

**Contributions:** I worked completely solo on this project and completed all tasks individually.
