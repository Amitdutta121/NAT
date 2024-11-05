from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import random
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

parameters = {
    'rule_type': ['crossing_giveway', 'crossing_standon', 'headon_giveway', 'overtaking_giveway', 'overtaking_standon'],
    'tod': ['night', 'evening', 'afternoon', 'morning'],
    'cpa_time': ['critical', 'near', 'safe'],
    'tss': ['high', 'medium', 'low']
}

UPLOAD_FOLDER = "uploads"
db = TinyDB('mydatabase.json')

# Define the query
Student = Query()


# Function to check if a student exists
def student_exists(name):
    return db.contains(Student.name == name)


def insert_student_data(student_name, weakness, actual_params):
    student_data = {
        'name': student_name,
        'weakness': weakness,
        'actual_parameters': actual_params,
        'answers': []
    }
    db.insert(student_data)
    print(f"Student {student_name} has been added to the database.")


def update_student_by_name(name, updated_data):
    db.update(updated_data, Student.name == name)


def get_weakness_by_student_name(student_name):
    result = db.search(Student.name == student_name)
    if result:
        return result[0]
    else:
        return None


def initialize_values(parameters):
    values = {}
    parameter_options = {}
    for parameter, options in parameters.items():
        values[parameter] = []
        parameter_options[parameter] = options
        for option in options:
            values[parameter].append(random.randint(150, 200))  # Initialize with equal weights
    return values, parameter_options


def select_param(param_values, random_number):
    current_sum = 0
    for i in range(len(param_values)):
        current_sum += param_values[i]
        if random_number <= current_sum:
            return i

    return -1


def param_values_to_actual(all_params_indexes, parameter_options):
    all_params = []
    param_ind = 0
    for parameter in all_params_indexes:
        all_params.append(list(parameter_options.values())[param_ind][parameter])
        param_ind += 1

    return all_params


def roulette_wheel_selection(values, parameter_options):
    all_params = []
    for parameter in values:
        # print(values[parameter])
        sum_values = sum(values[parameter])
        random_number = sum_values * random.random()

        all_params.append(select_param(values[parameter], random_number))
    # convert all_params to actual values

    return param_values_to_actual(all_params, parameter_options)


def updated_wheel_parameter(previous_params, new_score_in, parameter_options, weakness_value):
    for i, param in enumerate(previous_params):
        # Get the corresponding parameter key (e.g., 'MainRuleType', 'RangeCategory')
        parameter_key = list(parameter_options.keys())[i]

        # Find the index of the selected option within its parameter's options
        option_index = parameter_options[parameter_key].index(param.strip())

        # Update the value using the learning rate and the difference between new_score_in and mean_score
        update_value = 0.8 * (new_score_in - 50)
        weakness_value[parameter_key][option_index] -= update_value
    return weakness_value


@app.route("/students/initialize/<string:student_id>", methods=['GET'])
def initialize_student(student_id):
    if not student_exists(student_id):
        values, parameter_options = initialize_values(parameters)
        insert_student_data(student_id, values, parameter_options)
        return jsonify({
            'message': "Student initialized"
        })
    else:
        return jsonify({
            'message': "Student already exists"
        })


@app.route("/students/<string:student_id>/weakness", methods=['GET'])
def get_weakness(student_id):
    if student_exists(student_id):
        student_data = get_weakness_by_student_name(student_id)
        return jsonify(student_data)
    else:
        return jsonify({
            'message': 'Student does not exists.'
        })


@app.route("/students/<string:student_id>/next_question", methods=['GET'])
def get_next_question_param(student_id):
    if student_exists(student_id):
        student_data = get_weakness_by_student_name(student_id)
        res = roulette_wheel_selection(student_data['weakness'], student_data['actual_parameters'])
        return jsonify(res)
    else:
        jsonify({
            'message': 'Student does not exists.'
        })


@app.route("/students/weakness", methods=['PATCH'])
def update_weakness_by_student():
    # Parse the JSON data from the request
    data = request.get_json()
    student_id = data.get('student_name')
    score = data.get('score')
    previous_question_param = data.get('previous_params')

    if student_exists(student_id):
        student_data = get_weakness_by_student_name(student_id)
        print(student_data)
        updated_wheel_parameter(previous_question_param, score, student_data['actual_parameters'],
                                student_data['weakness'])
        print(student_data)
        student_data['answers'].append({
            'question_params': previous_question_param,
            'score': score
        })
        update_student_by_name(student_id, student_data)
        return jsonify({
            "message": "Student weakness updated."
        })
    else:
        return jsonify({
            "message": "Student does not exists."
        })


@app.route("/upload/<string:upload_folder>", methods=['POST'])
def upload_file(upload_folder):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file:
        # Securely save the file to the server
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'File upload failed'}), 500

@app.route("/")
def hello_world():
    return "Hello, World!"

#
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=8800)
