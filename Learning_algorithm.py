import pandas as pd
import numpy as np

# Load the data
one_hot_df = pd.read_csv('one_hot_df.csv')



# Define softmax function
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

# Define epsilon and learning rate as global variables
epsilon = 0.1  # Exploration rate
learning_rate = 0.5  # Learning rate

# Function to initialize probabilities for each parameter option dynamically
def initialize_probabilities(df):
    probabilities = {}
    parameter_options = {}
    for col in df.columns:
        col = col.strip()
        if col != 'Score':
            parameter, option = col.rsplit('_', 1)
            if parameter not in probabilities:
                probabilities[parameter] = []
                parameter_options[parameter] = []
            probabilities[parameter].append(1 / df.filter(like=parameter).shape[1])
            parameter_options[parameter].append(option)
    for parameter in probabilities:
        probabilities[parameter] = softmax(probabilities[parameter])
    return probabilities, parameter_options

# Function to select parameter using Epsilon-Greedy strategy
def select_parameter(probabilities, parameter_options, epsilon):
    if np.random.rand() < epsilon:
        # Exploration: select a random parameter and option
        parameter = np.random.choice(list(probabilities.keys()))
        option_idx = np.random.choice(len(probabilities[parameter]))
    else:
        # Exploitation: select the best parameter and option based on probabilities
        parameter = np.random.choice(list(probabilities.keys()))
        option_idx = np.random.choice(len(probabilities[parameter]), p=probabilities[parameter])
    option = parameter_options[parameter][option_idx]
    return parameter, option

# Function to update the probability values based on the score
def update_probabilities(probabilities, parameter, option_idx, new_score):
    scores = np.array(probabilities[parameter])

    # Apply a stronger penalty to highly scored options
    if new_score >= 90:  # You can adjust this threshold
        scores[option_idx] *= 0.1  # Strongly reduce probability

    # Otherwise, apply the regular update
    else:
        scores[option_idx] -= learning_rate * (new_score - np.mean(scores))

    # Normalize probabilities using softmax
    probabilities[parameter] = softmax(scores)
    return probabilities

# Function to generate the next question
def generate_next_question(df, probabilities, parameter_options, epsilon=0.1):
    parameter, option = select_parameter(probabilities, parameter_options, epsilon)

    option_col = f"{parameter}_{option}"
    if option_col not in df.columns:
        # Handle the case where the selected column doesn't exist
        print(f"Column {option_col} does not exist. Re-selecting parameter and option.")
        return generate_next_question(df, probabilities, parameter_options, epsilon)

    selected_questions = df[df[option_col] == 1]
    if selected_questions.empty:
        # Handle the case where no questions are found for the selected parameter and option
        print(f"No questions found for {option_col}. Re-selecting parameter and option.")
        return generate_next_question(df, probabilities, parameter_options, epsilon)

    selected_question = selected_questions.iloc[0]
    selected_question_params = selected_question[selected_question == 1].index.tolist()

    student_score = np.random.uniform(60, 100)

    option_idx = parameter_options[parameter].index(option)
    probabilities = update_probabilities(probabilities, parameter, option_idx, student_score)

    return selected_question_params, student_score, probabilities

def generate_next_question_from_score(df, probabilities, parameter_options, epsilon=0.1, student_score=None):
    parameter, option = select_parameter(probabilities, parameter_options, epsilon)

    option_col = f"{parameter}_{option}"
    if option_col not in df.columns:
        # Handle the case where the selected column doesn't exist
        print(f"Column {option_col} does not exist. Re-selecting parameter and option.")
        return generate_next_question_from_score(df, probabilities, parameter_options, epsilon, student_score)

    selected_questions = df[df[option_col] == 1]
    if selected_questions.empty:
        # Handle the case where no questions are found for the selected parameter and option
        print(f"No questions found for {option_col}. Re-selecting parameter and option.")
        return generate_next_question_from_score(df, probabilities, parameter_options, epsilon, student_score)

    selected_question = selected_questions.iloc[0]
    selected_question_params = selected_question[selected_question == 1].index.tolist()

    if student_score is None:
        student_score = np.random.uniform(60, 100)

    option_idx = parameter_options[parameter].index(option)
    probabilities = update_probabilities(probabilities, parameter, option_idx, student_score)

    return selected_question_params, student_score, probabilities

one_hot_df.columns = one_hot_df.columns.str.strip()  # Strip spaces from column names

# Initialize probabilities
parameters, parameter_options = initialize_probabilities(one_hot_df)
#
# # Generate 10 questions
# for i in range(10):
#     next_question_params, next_student_score, probabilities = generate_next_question(one_hot_df_copy, parameters, parameter_options, epsilon)
#     print(f"Question {i+1}:")
#     print("Selected Question Parameters:", next_question_params)
#     print("Student Score:", next_student_score)
#     print("Updated Probabilities:", probabilities)
#     print("-" * 30)

# Initialize a global dictionary to store scores for each MainRuleType
main_rule_type_scores = {
    'MainRuleType_crossing-giveway': 50,
    'MainRuleType_crossing-standon': 50,
    'MainRuleType_headon-giveway': 50,
    'MainRuleType_overtaking-giveway': 50,
    'MainRuleType_overtaking-standon': 50
}

def update_main_rule_type_score(params):
    global main_rule_type_scores  # Access the global scores

    # Define the main rule types and corresponding score increments
    rule_score_map = {
        'MainRuleType_crossing-giveway': 25,
        'MainRuleType_crossing-standon': 15,
        'MainRuleType_headon-giveway': 15,
        'MainRuleType_overtaking-giveway': 20,
        'MainRuleType_overtaking-standon': 5
    }

    # Check each parameter to see if it's in the rule_score_map
    for param in params:
        if param in rule_score_map:
            # Calculate the updated score
            updated_score = main_rule_type_scores[param] + rule_score_map[param]
            # Ensure the score does not exceed 100
            main_rule_type_scores[param] = min(updated_score, 100)
            # Return the updated score
            return main_rule_type_scores[param]

    # If no matching rule is found, return None
    return None


# Initialize probabilities
parameters, parameter_options = initialize_probabilities(one_hot_df)

# Loop to generate questions and update scores
for i in range(10):
    student_score = 50  # Initial student score

    # Generate the next question based on current student score
    next_question_params, next_student_score, updated_probabilities = generate_next_question_from_score(
        one_hot_df,
        parameters,
        parameter_options,
        epsilon,
        student_score
    )

    # Update the student score based on the selected question parameters
    student_score = update_main_rule_type_score(next_question_params)

    # Print results for each iteration
    print(f"Question {i+1}:")
    print("Selected Question Parameters:", next_question_params)
    print("Student Score:", student_score)
    print("Updated Probabilities:", updated_probabilities)
    print("-" * 30)
