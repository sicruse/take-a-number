from flask import Flask, jsonify
import os
import json
from threading import Lock

app = Flask(__name__)

# Make SEQUENCE_FILE configurable
app.config.setdefault('SEQUENCE_FILE', 'sequences.json')

# Lock for thread-safe file operations
lock = Lock()


def load_sequences():
    """Load the sequences from the JSON file. If it doesn't exist, return an empty dict."""
    sequence_file = app.config['SEQUENCE_FILE']
    if not os.path.exists(sequence_file):
        return {}
    with open(sequence_file, 'r') as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except json.JSONDecodeError:
            return {}


def save_sequences(sequences):
    """Save the sequences dictionary back to the JSON file."""
    sequence_file = app.config['SEQUENCE_FILE']

    # Get directory path
    directory = os.path.dirname(sequence_file)

    # Only try to create directory if there is a directory path
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Save the sequences
    with open(sequence_file, 'w') as f:
        json.dump(sequences, f)


@app.route('/next/<sequence_id>', methods=['GET'])
def get_next_value(sequence_id):
    with lock:
        sequences = load_sequences()

        # If sequence doesn't exist, initialize it to 0
        if sequence_id not in sequences:
            next_value = 1
        else:
            # Increment the existing value
            next_value = sequences[sequence_id] + 1

        # Save the new value
        sequences[sequence_id] = next_value

        # Save updated sequences
        save_sequences(sequences)

        return jsonify({
            "sequence_id": sequence_id,
            "next_value": next_value
        }), 200


if __name__ == '__main__':
    # Enable debug mode when running directly
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5000)
