import json
import pandas as pd


def create_mapping(csv_path):
    # Load the dataset to inspect its contents
    data = pd.read_csv(csv_path)

    # Define the grade-to-cohort mapping
    cohort_mapping = {
        6: "Cohort_2031",
        7: "Cohort_2030",
        8: "Cohort_2029",
        9: "Cohort_2028",
        10: "Cohort_2027",
        11: "Cohort_2026",
        12: "Cohort_2025"
    }

    # Creating the dictionary with renamed grades
    student_mapping = {
        f"{row['Last Name']}_{row['First Name']}": cohort_mapping.get(row['Grade'], row['Grade'])
        for _, row in data.iterrows()
    }

    # Specify the output file path
    output_json_file = 'student_mapping.json'

    # Write the formatted mapping to the JSON file
    with open(output_json_file, 'w') as file:
        json.dump(student_mapping, file)
