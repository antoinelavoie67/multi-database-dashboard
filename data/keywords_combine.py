#python keywords_combine.py 'publication_keyword.csv' 'faculty_keyword.csv' 'keywords.id'
#Takes 3 inputs 1. publication_keyword.csv 2. faculty_keyword.csv 3. keyword.id column name as defined by student

import pandas as pd
import sys
print(sys.argv[0])
publication_keywords = pd.read_csv(sys.argv[1])
faculty_keywords = pd.read_csv(sys.argv[2])
# Using pd.concat to combine the data frames
keywords = pd.concat([publication_keywords, faculty_keywords]).drop_duplicates(keep="first").sort_values(by=[sys.argv[3]])
with open("keywords.csv", "w", encoding="utf-8") as keywords_file:
    keywords.to_csv(keywords_file, index=False)