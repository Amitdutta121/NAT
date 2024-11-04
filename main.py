import os
import pandas as pd


folder_path = 'study2datasetNew'
std_column_names = [' Actioncorrect', ' StandOnGiveWaycorrect', ' RuleTypecorrect', ' TargetVesselTypecorrect']

def read_csv_with_adjustment(file_path):
    # Read the header and first data row
    header = pd.read_csv(file_path, nrows=0)
    data_sample = pd.read_csv(file_path, skiprows=1, nrows=1)

    # Count the number of columns in the header and data row
    header_count = len(header.columns)
    data_count = len(data_sample.columns)

    # If there's a mismatch, adjust the header
    if header_count != data_count:
        adjusted_columns = header.columns.tolist() + ['Unnamed'] * (data_count - header_count)
        df = pd.read_csv(file_path, names=adjusted_columns, header=0)
    else:
        df = pd.read_csv(file_path, header=0)

    return df

def standardize_column_names(df, columns):
  for column in columns:
    # Convert all values in the column to lowercase
    df[column] = df[column].str.lower()
    #remove space as well
    df[column] = df[column].str.replace(' ', '')
  return df


def read_csv_files(folder_path, start, end):
    """Reads CSV files from the specified range of student folders."""
    adaptive_dfs = []
    posttest_dfs = []
    pretest_dfs = []
    practice_dfs = []

    for student_folder in os.listdir(folder_path):
        if student_folder.startswith('Student'):
            student_number = int(student_folder.replace('Student', ''))
            if start <= student_number <= end:
                student_path = os.path.join(folder_path, student_folder)

                if os.path.isdir(student_path):
                    if student_number % 2 == 0:
                      ad_csv_df = read_csv_with_adjustment(os.path.join(student_path, 'adaptive.csv'))
                      ad_csv_df[" Methdology"] = "Adaptive"
                      adaptive_dfs.append(ad_csv_df)
                    post_df = pd.read_csv(os.path.join(student_path, 'posttest.csv'))

                    pre_df = pd.read_csv(os.path.join(student_path, 'pretest.csv'))


                    if student_number % 2 == 0:
                      post_df[" Methdology"] = "Adaptive"
                      pre_df[" Methdology"] = "Adaptive"
                    else:
                      post_df[" Methdology"] = "Practice"
                      pre_df[" Methdology"] = "Practice"

                    posttest_dfs.append(post_df)
                    pretest_dfs.append(pre_df)

                    practice_file = os.path.join(student_path, 'practice.csv')
                    if os.path.exists(practice_file):
                        practice_df = pd.read_csv(practice_file)
                        if student_number % 2 == 0:
                          practice_df[" Methdology"] = "Practice"
                        else:
                          practice_df[" Methdology"] = "Adaptive"
                        practice_dfs.append(practice_df)

    return adaptive_dfs, posttest_dfs, pretest_dfs, practice_dfs

def concatenate_dataframes(adaptive_dfs, posttest_dfs, pretest_dfs, practice_dfs):
    """Concatenates dataframes from lists."""
    adaptive_df = pd.concat(adaptive_dfs, ignore_index=True)
    posttest_df = pd.concat(posttest_dfs, ignore_index=True)
    pretest_df = pd.concat(pretest_dfs, ignore_index=True)
    practice_df = pd.concat(practice_dfs, ignore_index=True) if practice_dfs else pd.DataFrame()
    return adaptive_df, posttest_df, pretest_df, practice_df

def filter_columns(adaptive_df, posttest_df, pretest_df, practice_df, columns):
    """Filters the required columns from each dataframe."""
    adaptive_filtered = adaptive_df[columns]
    posttest_filtered = posttest_df[columns]
    pretest_filtered = pretest_df[columns]
    practice_filtered = practice_df[columns] if not practice_df.empty else pd.DataFrame(columns=columns)
    final_df = pd.concat([adaptive_filtered, posttest_filtered, pretest_filtered, practice_filtered], ignore_index=True)
    final_df = standardize_column_names(final_df, std_column_names)
    final_df[" MainRuleType"] = final_df[' RuleTypecorrect'] + ' - ' + final_df[' StandOnGiveWaycorrect']
    final_df = standardize_column_names(final_df, [" MainRuleType"])
    # Use pd.qcut to create 5 equal-sized categories
    # Define bins and labels
    bins = [0, 3000, 6000, 9000, 12000, float('inf')]  # Example bins
    labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

    # Create the 'RangeCategory' column using pd.cut
    final_df[' RangeCategory'] = pd.cut(final_df[' TargetRangecorrect'], bins=bins, labels=labels, right=False)
    return final_df

columns = [' TargetAnglecorrect', ' Score', ' TargetBearingcorrect', ' StandOnGiveWaycorrect', ' Actioncorrect', ' RuleTypecorrect', ' TargetRangecorrect', ' TargetVesselTypecorrect', ' Methdology']

adaptive_dfs, posttest_dfs, pretest_dfs, practice_dfs = read_csv_files(folder_path, 50, 80)
adaptive_df, posttest_df, pretest_df, practice_df = concatenate_dataframes(adaptive_dfs, posttest_dfs, pretest_dfs, practice_dfs)
final_df = filter_columns(adaptive_df, posttest_df, pretest_df, practice_df, columns)

# Define the angle to direction mapping function
def angle_to_direction(angle):
    if 0 <= angle < 11.25 or 348.75 <= angle < 360:
        return "Dead Ahead"
    elif 11.25 <= angle < 33.75:
        return "On the Port Bow"
    elif 33.75 <= angle < 56.25:
        return "Broad on the Port Bow"
    elif 56.25 <= angle < 78.75:
        return "Forward of the Port Beam"
    elif 78.75 <= angle < 101.25:
        return "Abeam (Port)"
    elif 101.25 <= angle < 123.75:
        return "Abaft the Port Beam"
    elif 123.75 <= angle < 146.25:
        return "Broad on the Port Quarter"
    elif 146.25 <= angle < 168.75:
        return "On the Port Quarter"
    elif 168.75 <= angle < 191.25:
        return "Dead Astern"
    elif 191.25 <= angle < 213.75:
        return "On the Starboard Quarter"
    elif 213.75 <= angle < 236.25:
        return "Broad on the Starboard Quarter"
    elif 236.25 <= angle < 258.75:
        return "Abaft the Starboard Beam"
    elif 258.75 <= angle < 281.25:
        return "Abeam (Starboard)"
    elif 281.25 <= angle < 303.75:
        return "Forward of the Starboard Beam"
    elif 303.75 <= angle < 326.25:
        return "Broad on the Starboard Bow"
    elif 326.25 <= angle < 348.75:
        return "On the Starboard Bow"
    else:
        return "Invalid angle"


vessel_mapping = {
    'tugwithtow':'tugwithtow',
    'merchant':'merchant',
    'cruiseship':'cruiseship',
    'tanker':'tanker',
    'mvseriusstar_51':'merchant',
    'turbocat_109':'merchant',
    'tractortug50_171':'tugwithtow',
    "grandprincess_237": "cruiseship",
    "tractortug50_273": "tugwithtow",
    "tractortug50_169": "tugwithtow",
    "aplb_231": "merchant",
    "sidecarsally_297": "fishingvessel",
    "turbocat_365": "merchant",
    "hosbrigadoon_65": "tugwithtow",
    "siriusstar_97": "tanker",
    "aplb_161": "merchant",
    "silvergate_197": "merchant",
    "grandprincess_63": "cruiseship",
    "smithouston_121": "tugwithtow",
    "grandprincess_57": "cruiseship",
    "pusherpup_115": "tugwithtow",
    "smithouston_177": "tugwithtow",
    "cmacgmnorsk_243": "merchant",
    "tractortug50_313": "tugwithtow",
    "smithouston_175": "tugwithtow",
    "hosbrigadoon_237": "tugwithtow",
    "yavuz_303": "warship",
    "yavuz_69": "warship",
    "orientexpress_127": "cruiseship",
    "cmacgmnorsk_189": "merchant",
    "yavuz_71": "warship",
    "smithouston_133": "tugwithtow",
    "aplb_81": "merchant",
    "grandprincess_235": "cruiseship"
}

# Define the function to categorize scores
def score_to_grade(score):
    if 90 <= score <= 100:
        return "A"
    elif 80 <= score < 90:
        return "B"
    elif 70 <= score < 80:
        return "C"
    elif 60 <= score < 70:
        return "D"
    elif 0 <= score < 60:
        return "F"
    else:
        return "Invalid score"

from sklearn.utils import resample

balanced_df = final_df[final_df[' MainRuleType'] != 'overtaking-inextermis']
# Separate majority and minority classes
df_crossing_giveway = balanced_df[balanced_df[' MainRuleType'] == 'crossing-giveway']
df_headon_giveway = balanced_df[balanced_df[' MainRuleType'] == 'headon-giveway']
df_crossing_standon = balanced_df[balanced_df[' MainRuleType'] == 'crossing-standon']
df_overtaking_giveway = balanced_df[balanced_df[' MainRuleType'] == 'overtaking-giveway']
df_overtaking_standon = balanced_df[balanced_df[' MainRuleType'] == 'overtaking-standon']

from sklearn.utils import resample

# Find the size of the largest class
max_size = max(len(df_crossing_giveway), len(df_headon_giveway), len(df_crossing_standon))

# Oversample the minority classes
df_overtaking_giveway_oversampled = resample(df_overtaking_giveway, replace=True, n_samples=max_size, random_state=42)
df_overtaking_standon_oversampled = resample(df_overtaking_standon, replace=True, n_samples=max_size, random_state=42)

# Combine oversampled classes with majority classes
balanced_df = pd.concat([df_crossing_giveway, df_headon_giveway, df_crossing_standon, df_overtaking_giveway_oversampled, df_overtaking_standon_oversampled])


sample_final_df = balanced_df.copy()
sample_final_df = sample_final_df[sample_final_df[' MainRuleType'] != 'overtaking-inextermis']

# Apply the function to create the new column
sample_final_df['TargetBearingNames'] = sample_final_df[' TargetBearingcorrect'].apply(angle_to_direction)
# Define the desired order of the categories
categories = ["Dead Ahead", "On the Port Bow", "Broad on the Port Bow", "Forward of the Port Beam", "Abeam (Port)",
              "Abaft the Port Beam", "Broad on the Port Quarter", "On the Port Quarter", "Dead Astern",
              "On the Starboard Quarter", "Broad on the Starboard Quarter", "Abaft the Starboard Beam",
              "Abeam (Starboard)", "Forward of the Starboard Beam", "Broad on the Starboard Bow", "On the Starboard Bow"]

# Convert the TargetBearingNames column to a categorical type with the specified order
sample_final_df['TargetBearingNames'] = pd.Categorical(sample_final_df['TargetBearingNames'], categories=categories, ordered=True)

# Apply the function to create the new column
sample_final_df['TargetAngleNames'] = sample_final_df[' TargetAnglecorrect'].apply(angle_to_direction)
# Convert the TargetAngleNames column to a categorical type with the specified order
sample_final_df['TargetAngleNames'] = pd.Categorical(sample_final_df['TargetAngleNames'], categories=categories, ordered=True)

sample_final_df['Grade'] = sample_final_df[' Score'].apply(score_to_grade)
grade_categories = ["A", "B", "C", "D", "F"]
sample_final_df['Grade'] = pd.Categorical(sample_final_df['Grade'], categories=grade_categories, ordered=True)

sample_final_df[' TargetVesselTypecorrect'] = sample_final_df[' TargetVesselTypecorrect'].map(vessel_mapping)

# feature_columns = [' StandOnGiveWaycorrect', ' Actioncorrect', ' RuleTypecorrect', ' TargetVesselTypecorrect', ' MainRuleType', ' RangeCategory','TargetBearingNames', 'TargetAngleNames']


feature_columns = [' TargetVesselTypecorrect', ' MainRuleType', ' RangeCategory','TargetBearingNames', 'TargetAngleNames']

# if isScoreCategorized:
#     target_column = 'Grade'
# else:
#     target_column = ' Score'

target_column = ' Score'
df_cleaned = sample_final_df[feature_columns + [target_column]]

# # Transform the specified columns into one-hot vectors
one_hot_df = pd.get_dummies(df_cleaned, columns=feature_columns)

# # Ensure the RangeCategory is one-hot encoded in the specified sequence
range_categories = ["Very Low", "Low", "Medium", "High", "Very High"]
one_hot_df = pd.get_dummies(df_cleaned, columns=[' TargetVesselTypecorrect', ' MainRuleType', ' RangeCategory','TargetBearingNames', 'TargetAngleNames'], dtype=int)
# one_hot_df = one_hot_df.reindex(columns=one_hot_df.columns.tolist() + [f'RangeCategory_{cat}' for cat in range_categories], fill_value=0)

print(one_hot_df.head())


# Save to CSV
one_hot_df.to_csv('one_hot_df.csv', index=False)

