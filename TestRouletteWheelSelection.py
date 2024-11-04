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

learning_rate = 0.8 # Learning rate 0.8 is good with 20 iterations

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
            values[parameter].append(random.randint(150,200))  # Initialize with equal weights
            parameter_options[parameter].append(option)
    return values, parameter_options


values, parameter_options = initialize_values(one_hot_df)

print(parameter_options)
print(values)
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

def roulette_wheel_selection():
    all_params = []
    for parameter in values:
        # print(values[parameter])
        sum_values = sum(values[parameter])
        random_number = sum_values * random.random()

        all_params.append(select_param(values[parameter], random_number))
    # convert all_params to actual values

    return param_values_to_actual(all_params)

def random_selection():
    all_params = []
    for parameter in values:
        all_params.append(random.randint(0, len(values[parameter]) - 1))
    return param_values_to_actual(all_params)


def update_wheel(previous_params, new_score_in):
    print("===========================")
    print(previous_params)
    print("===========================")
    # Iterate through each parameter in the selected parameters
    for i, param in enumerate(previous_params):
        # Get the corresponding parameter key (e.g., 'MainRuleType', 'RangeCategory')
        parameter_key = list(parameter_options.keys())[i]

        # Find the index of the selected option within its parameter's options
        option_index = parameter_options[parameter_key].index(param.strip())

        # Update the value using the learning rate and the difference between new_score_in and mean_score
        update_value = learning_rate * (new_score_in - mean_score)
        values[parameter_key][option_index] -= update_value

        # # Check if the updated value is negative
        # if values[parameter_key][option_index] < 0:
        #     # Normalize all values for this parameter to ensure they remain positive and proportional
        #     min_value = min(values[parameter_key])
        #     for j in range(len(values[parameter_key])):
        #         values[parameter_key][j] -= min_value
        #         # Apply a small positive floor to avoid exact zeros after normalization
        #         values[parameter_key][j] = max(values[parameter_key][j], 0.01)
        #
        #     # Renormalize to keep the sum of probabilities consistent if needed
        #     total = sum(values[parameter_key])
        #     values[parameter_key] = [val / total for val in values[parameter_key]]

    return values


# Initialize a global dictionary to store scores for each MainRuleType
main_rule_type_scores = {
    'crossing-giveway': 50,
    'crossing-standon': 50,
    'headon-giveway': 50,
    'overtaking-giveway': 50,
    'overtaking-standon': 50
}


def update_main_rule_type_score(params, learner_type="random"):
    global main_rule_type_scores

    # Define the learning rates for different learner types
    if learner_type == "fast":
        rule_score_map = {
            'crossing-giveway': 25,
            'crossing-standon': 35,
            'headon-giveway': 25,
            'overtaking-giveway': 25,
            'overtaking-standon': 25
        }
    elif learner_type == "slow":
        rule_score_map = {
            'crossing-giveway': 10,
            'crossing-standon': 8,
            'headon-giveway': 6,
            'overtaking-giveway': 4,
            'overtaking-standon': 2
        }
    elif learner_type == "inconsistent":
        rule_score_map = {
            'crossing-giveway': 30,
            'crossing-standon': 15,
            'headon-giveway': 25,
            'overtaking-giveway': 5,
            'overtaking-standon': 20
        }
    elif learner_type == "focused":
        rule_score_map = {
            'crossing-giveway': 50,
            'crossing-standon': 5,
            'headon-giveway': 5,
            'overtaking-giveway': 5,
            'overtaking-standon': 5
        }
    elif learner_type == "random":
        rule_score_map = {
            'crossing-giveway': random.randint(5, 30),
            'crossing-standon': random.randint(5, 30),
            'headon-giveway': random.randint(5, 30),
            'overtaking-giveway': random.randint(5, 30),
            'overtaking-standon': random.randint(5, 30)
        }
    else:  # default learner
        rule_score_map = {
            'crossing-giveway': 25,
            'crossing-standon': 20,
            'headon-giveway': 15,
            'overtaking-giveway': 10,
            'overtaking-standon': 5
        }

    # Update scores based on the selected parameters
    for param in params:
        if param.strip() in rule_score_map:
            updated_score = main_rule_type_scores[param.strip()] + rule_score_map[param.strip()]
            main_rule_type_scores[param.strip()] = min(updated_score, 100)
            return main_rule_type_scores[param.strip()]
    return 0

ratio_of_situations = []
main_rule_type_values = {
    'crossing-giveway': [],
    'crossing-standon': [],
    'headon-giveway': [],
    'overtaking-giveway': [],
    'overtaking-standon': []
}

correct_parameters = []
scores = []

for i in range(10):
    print("-" * 50)
    params = roulette_wheel_selection()
    # params = random_selection()
    print(params)
    ratio_of_situations.append(params[1])
    # Update the values based on the new score
    new_score = update_main_rule_type_score(params, learner_type="inconsistent")
    values = update_wheel(params, new_score)
    print(params, new_score)
    print(values)
    print("Crossing Giveway : ", values['MainRuleType'][0])
    print("Crossing Standon : ", values['MainRuleType'][1])
    print("Headon Giveway : ", values['MainRuleType'][2])
    print("Overtaking Giveway : ", values['MainRuleType'][3])
    print("Overtaking Standon : ", values['MainRuleType'][4])
    main_rule_type_values['crossing-giveway'].append(values['MainRuleType'][0])
    main_rule_type_values['crossing-standon'].append(values['MainRuleType'][1])
    main_rule_type_values['headon-giveway'].append(values['MainRuleType'][2])
    main_rule_type_values['overtaking-giveway'].append(values['MainRuleType'][3])
    main_rule_type_values['overtaking-standon'].append(values['MainRuleType'][4])
    correct_parameters.append(params[1])
    scores.append(new_score)
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
plt.title('Count of Each Unique Rule Type'+str(learning_rate))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()



iterations = list(range(1, 11))

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create a y-axis to plot the parameter values
colors = ['red', 'green', 'orange', 'purple', 'brown']  # Example colors for different parameters
for i, (rule, values) in enumerate(main_rule_type_values.items()):
    ax.plot(iterations, values, marker='o', linestyle='--', label=rule, color=colors[i])

ax.set_xlabel('Iteration')
ax.set_ylabel('Parameter Values', color='black')
ax.tick_params(axis='y', labelcolor='black')

# Plot the correct parameter values
for i, correct_param in enumerate(correct_parameters):
    y_value = main_rule_type_values[correct_param][i]
    ax.scatter(iterations[i], y_value, color='black', s=100, edgecolor='yellow', zorder=5, label='Correct Param' if i == 0 else "")

# Add a legend positioned in the bottom left corner
fig.legend(loc="lower left", bbox_to_anchor=(0.1, 0.1), bbox_transform=ax.transAxes)

# Set the title
plt.title('Parameter Values and Correct Parameter Over Time')

plt.ylim(0, 220)
# Show the plot
plt.show()


#-------------------------------------------------------------------

# Calculate the linear regression line
slope, intercept = np.polyfit(iterations, scores, 1)
regression_line = np.poly1d([slope, intercept])

# Set up the figure and axis for the score plot
plt.figure(figsize=(10, 6))
plt.plot(iterations, scores, marker='o', linestyle='-', color='blue', label='Score')
plt.plot(iterations, regression_line(iterations), color='red', linestyle='--', label='Regression Line')

# Label the plot
plt.xlabel('Iteration')
plt.ylabel('Score')
plt.title('Score Over Time with Linear Regression Line')
plt.legend()

# Display the plot
plt.show()


print(scores)
print(slope)


