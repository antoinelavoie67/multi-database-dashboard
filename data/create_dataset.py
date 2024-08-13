import json
from pandas import json_normalize
from tqdm import tqdm
import sys


def create_dataset(input_file_name: str, output_file_name: str, input_column_name: list, output_column_name: list = None, index: bool = False) -> None:
    """
    input_file_name (str): Input JSON file name
    output_file_name (str): Output CSV file name
    input_column_name (str): Filter input file based on the columns
    output_column_name (list): Rename input columns. None by default. Note: Passing 'None' will keep the same column names
    index (bool): Toggle index in output file. False (turned off) by default
    """

    with open(input_file_name) as f:
        input_file_data: list = json.load(f)
        output_file_data: list = []

        if output_column_name is not None:
            if len(input_column_name) != len(output_column_name):
                print("Input-Output columns need to have same length and input columns must be not null!")
                return
        else: output_column_name = input_column_name

        valid_columns: list = list(input_file_data[0].keys()) + ["keywords.id", "keywords.name", "keywords.score"]
        valid_columns.remove("keywords")

        if "affiliation" in valid_columns:
            valid_columns.remove("affiliation")
            valid_columns += ["affiliation.id", "affiliation.name", "affiliation.photoUrl"]

        if "keywords" in input_column_name:
            input_column_name.remove("keywords")
            input_column_name += ["keywords.id", "keywords.name", "keywords.score"]

        if "affiliation" in input_column_name:
            input_column_name.remove("affiliation")
            input_column_name += ["affiliation.id", "affiliation.name", "affiliation.photoUrl"]

        for col in input_column_name:
            if col not in valid_columns:
                print(f"Input column [{col}] not found!")
                print("Available columns are: [" + ", ".join(valid_columns) + "]")
                return

        has_publications: bool = ("publications" in input_column_name)
        has_keywords: list = ["keywords.id" in input_column_name , "keywords.name" in input_column_name, "keywords.score" in input_column_name]
        has_affiliation: list = ["affiliation.id" in input_column_name , "affiliation.name" in input_column_name, "affiliation.photoUrl" in input_column_name]


        def get_data_from_record(record: dict) -> dict:
            data: dict = {}

            for c in input_column_name:
                try: data[c] = record[c]
                except KeyError: continue

            if has_affiliation[0]: data["affiliation.id"] = record["affiliation"]["id"]
            if has_affiliation[1]: data["affiliation.name"] = record["affiliation"]["name"]
            if has_affiliation[2]: data["affiliation.photoUrl"] = record["affiliation"]["photoUrl"]

            return data


        if has_publications and any(has_keywords):
            for record in tqdm(input_file_data, desc="Records Processed: "):
                data: dict = get_data_from_record(record)

                for pid in record["publications"]:
                    for keyword in record["keywords"]:
                        temp_data: dict = data.copy()

                        if has_keywords[0]: temp_data["keywords.id"] = keyword["id"]
                        if has_keywords[1]: temp_data["keywords.name"] = keyword["name"]
                        if has_keywords[2]: temp_data["keywords.score"] = keyword["score"]
                        temp_data["publications"] = pid

                        output_file_data.append(temp_data)


        elif has_publications:
            for record in tqdm(input_file_data, desc="Records Processed: "):
                data: dict = get_data_from_record(record)

                for pid in record["publications"]:
                    temp_data: dict = data.copy()
                    temp_data["publications"] = pid
                    output_file_data.append(temp_data)


        elif any(has_keywords):
            for record in tqdm(input_file_data, desc="Records Processed: "):
                data: dict = get_data_from_record(record)

                for keyword in record["keywords"]:
                    temp_data: dict = data.copy()

                    if has_keywords[0]: temp_data["keywords.id"] = keyword["id"]
                    if has_keywords[1]: temp_data["keywords.name"] = keyword["name"]
                    if has_keywords[2]: temp_data["keywords.score"] = keyword["score"]

                    output_file_data.append(temp_data)


        else:
            for record in tqdm(input_file_data, desc="Records Processed: "):
                output_file_data.append(get_data_from_record(record))

    print(f"Creating [{output_file_name}]... Note: This may take some time depending on the amount of data being extracted and computing power!")
    json_normalize(output_file_data).drop_duplicates().rename(columns={c:cp for (c, cp) in zip(input_column_name, output_column_name)}).to_csv(output_file_name, index=index)
    print("Done!")


def print_usage() -> None:
    print("USAGE 1: python ./create_dataset.py input_file output_file")
    print('EXAMPLE 1: python ./create_dataset.py faculty.json faculty_all_atributes.csv"\n')
    print("USAGE 1: python ./create_dataset.py input_file output_file extract_columns")
    print('EXAMPLE 1: python ./create_dataset.py faculty.json test1.csv "id, researchInterest"\n')
    print("USAGE 2: python ./create_dataset.py input_file output_file extract_columns rename_extracted_columns")
    print('EXAMPLE 2: python ./create_dataset.py faculty.json test2.csv "id, researchInterest" "faculty_id, research_interest"\n')
    print("USAGE 3: python ./create_dataset.py input_file output_file extract_columns rename_extracted_columns indexing")
    print('EXAMPLE 3: python ./create_dataset.py faculty.json test3.csv "id, researchInterest" "faculty_id, research_interest" True')


def create_full_dataset(filepath,output_file):
    with open(filepath) as f:
     data = json.load(f)
     df = json_normalize(data)
     df.replace(r'[^\w\s]|_', ' ', regex=True)
     df.to_csv(output_file, index=True)

if __name__ == "__main__":
    num_args = len(sys.argv)

    try:
        if num_args == 3:
            create_full_dataset(sys.argv[1],sys.argv[2])
        elif num_args == 4:
            create_dataset(sys.argv[1], sys.argv[2], sys.argv[3].replace(" ", "").split(","))
        elif num_args == 5:
            create_dataset(sys.argv[1], sys.argv[2], sys.argv[3].replace(" ", "").split(","), sys.argv[4].replace(" ", "").split(","))
        elif num_args == 6:
            create_dataset(sys.argv[1], sys.argv[2], sys.argv[3].replace(" ", "").split(","), sys.argv[4].replace(" ", "").split(","), bool(sys.argv[5]))
        else:
            print("Please specify the correct number of args.\n")
            print_usage()
    except:
        print_usage()
