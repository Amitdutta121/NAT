import pandas as pd
import numpy as np
import random
from collections import Counter
import matplotlib.pyplot as plt

random.seed(42)

# Load the data
one_hot_df = pd.read_csv('one_hot_df.csv')
one_hot_df.columns = one_hot_df.columns.str.strip()
# Learning rate


for i in range(22):

    learning_rate = i * 0.1  # Learning rate 0.8 is good with 20 iterations

    mean_score = np.mean(one_hot_df['Score'])


    # Function to initialize values for each parameter option dynamically
    def initialize_values(df):
        values = {}
        parameter_options = {}
        for col in df.columns:
            col = col.strip()
            if col != 'Score':
                parameter, option = col.rsplit('_', 1)
                if parameter not in values:
                    values[parameter] = []
                    parameter_options[parameter] = []
                values[parameter].append(100.0)  # Initialize with equal weights
                parameter_options[parameter].append(option)
        return values, parameter_options


    values, parameter_options = initialize_values(one_hot_df)


    def select_param(param_values, random_number):
        current_sum = 0
        for i in range(len(param_values)):
            current_sum += param_values[i]
            if random_number <= current_sum:
                return i

        return -1


    def param_values_to_actual(all_params_indexes):
        all_params = []
        param_ind = 0
        for parameter in all_params_indexes:
            all_params.append(list(parameter_options.values())[param_ind][parameter])
            param_ind += 1

        return all_params


    # Initialize values

    def rank_based_selection():
        all_params = []
        for parameter in values:
            # Rank the options based on their current values (descending order)
            ranked_indexes = np.argsort(values[parameter])[::-1]
            ranked_values = [values[parameter][i] for i in ranked_indexes]

            # Assign selection probabilities based on rank
            total_rank = sum(range(1, len(ranked_values) + 1))
            selection_probabilities = [(len(ranked_values) - i) / total_rank for i in range(len(ranked_values))]

            # Select a parameter option based on these probabilities
            selected_index = np.random.choice(ranked_indexes, p=selection_probabilities)

            all_params.append(selected_index)
        return param_values_to_actual(all_params)


    def update_wheel(previous_params, new_score_in):
        # Iterate through each parameter in the selected parameters
        for i, param in enumerate(previous_params):
            # Get the corresponding parameter key (e.g., 'MainRuleType', 'RangeCategory')
            parameter_key = list(parameter_options.keys())[i]

            # Find the index of the selected option within its parameter's options
            option_index = parameter_options[parameter_key].index(param.strip())

            # Update the value using the learning rate and the difference between new_score_in and mean_score
            update_value = learning_rate * (new_score_in - mean_score)
            values[parameter_key][option_index] -= update_value

        return values


    # Initialize a global dictionary to store scores for each MainRuleType
    main_rule_type_scores = {
        'crossing-giveway': 50,
        'crossing-standon': 50,
        'headon-giveway': 50,
        'overtaking-giveway': 50,
        'overtaking-standon': 50
    }


    def update_main_rule_type_score(params):
        global main_rule_type_scores  # Access the global scores

        current_score = 0

        # Define the main rule types and corresponding score increments
        rule_score_map = {
            'crossing-giveway': 25,
            'crossing-standon': 20,
            'headon-giveway': 15,
            'overtaking-giveway': 10,
            'overtaking-standon': 5
        }

        # Check each parameter to see if it's in the rule_score_map
        for param in params:
            if param.strip() in rule_score_map:
                # Calculate the updated score
                updated_score = main_rule_type_scores[param.strip()] + rule_score_map[param.strip()]
                # Ensure the score does not exceed 100
                main_rule_type_scores[param.strip()] = min(updated_score, 100)
                # Return the updated score
                current_score = min(updated_score, 100)
                return main_rule_type_scores[param.strip()]

        # If no matching rule is found, return the current score
        return current_score


    ratio_of_situations = []

    for i in range(20):
        print("-" * 50)
        params = rank_based_selection()
        print(params)
        ratio_of_situations.append(params[1])
        # Update the values based on the new score
        new_score = update_main_rule_type_score(params)
        values = update_wheel(params, new_score)
        print(params, new_score)
        print(values)
        print("Crossing Giveway : ", values['MainRuleType'][0])
        print("Crossing Standon : ", values['MainRuleType'][1])
        print("Headon Giveway : ", values['MainRuleType'][2])
        print("Overtaking Giveway : ", values['MainRuleType'][3])
        print("Overtaking Standon : ", values['MainRuleType'][4])
        print("-" * 50)

    # Desired order of rule types
    desired_order = ['crossing-giveway', 'crossing-standon', 'headon-giveway', 'overtaking-giveway',
                     'overtaking-standon']

    # Count the occurrences of each unique value
    counts = Counter(ratio_of_situations)

    # Reorder the counts according to the desired order
    ordered_counts = {rule: counts[rule] for rule in desired_order if rule in counts}

    # Generate the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(ordered_counts.keys(), ordered_counts.values())
    plt.xlabel('Rule Types')
    plt.ylabel('Count')
    plt.title('Count of Each Unique Rule Type' + str(learning_rate))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
