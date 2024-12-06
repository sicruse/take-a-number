# TakeANumber

A lightweight REST API service that generates sequential numbers, perfect for distributed systems that need unique, incremental identifiers. TakeANumber maintains multiple independent sequences, each identified by a unique name.

## Project Overview

TakeANumber provides a simple way to generate sequential numbers across different sequences. Each sequence is identified by a unique name and maintains its own counter. When requested, the service returns and increments the next value in the specified sequence.

## Features

- Simple REST API endpoint for retrieving next value in a sequence
- Supports multiple independent sequences
- Persistent storage of sequence values
- Thread-safe operations
- Docker support for easy deployment
- Lightweight and fast

## Prerequisites

- Docker (recommended)
- Alternative: Python 3.11+ with Flask

## Installation

### Using Docker (Recommended)

1. Clone this repository:

```
git clone <repository-url>
cd TakeANumber
```

2. Ensure you have the required files:

```
# Create empty sequences.json if it doesn't exist
echo '{}' > sequences.json
```

3. Build the Docker image:

```
docker build -t take-a-number:latest .
```

4. Run the container:

```bash
# Clean up any existing container
docker stop take-a-number 2>/dev/null || true
docker rm take-a-number 2>/dev/null || true

# Run the container
docker run -d -p 5000:5000 --name take-a-number \
    -v $(pwd)/sequences.json:/app/sequences.json \
    take-a-number:latest

# If port 5000 is already in use, use a different port:
docker run -d -p 5001:5000 --name take-a-number \
    -v $(pwd)/sequences.json:/app/sequences.json \
    take-a-number:latest
```

Note: When using a different port, remember to update your curl commands accordingly:
```
curl http://localhost:5001/next/foo
```

### Manual Installation

1. Clone the repository
2. Install dependencies:

```
pip install flask
```

3. Run the application:

```
python app.py
```

## Usage

### API Endpoint

GET `/next/<sequence_id>`

- `sequence_id`: String identifier for your sequence

### Example Usage

```
# Get next value for sequence "foo"
curl http://localhost:5000/next/foo

# Response:
# {"sequence_id": "foo", "next_value": 1}

# Get next value again
curl http://localhost:5000/next/foo

# Response:
# {"sequence_id": "foo", "next_value": 2}
```

### Different Sequences

You can maintain multiple sequences simultaneously:

```
curl http://localhost:5000/next/sequence1
curl http://localhost:5000/next/sequence2
```

Each sequence maintains its own counter independently.

## Configuration

The service uses these default settings:

- Port: 5000
- Host: 0.0.0.0
- Storage file: sequences.json

You can configure the storage location by setting the SEQUENCE_FILE configuration value:

```python
# Store in current directory
app.config['SEQUENCE_FILE'] = 'sequences.json'

# Store in specific directory (directory will be created if it doesn't exist)
app.config['SEQUENCE_FILE'] = '/path/to/your/sequences.json'
```

## Data Persistence

- Sequence values are stored in a JSON file (default: `sequences.json` in current directory)
- If a path is specified, directories will be automatically created
- The file is automatically created if it doesn't exist
- Each sequence maintains its own independent counter
- First request for a sequence starts at 1
- Thread-safe file operations prevent data corruption
- For Docker deployments, consider mounting a volume for persistence:

```bash
docker run -d -p 5000:5000 --name take-a-number \
    -v $(pwd)/sequences.json:/app/sequences.json \
    take-a-number:latest
```

## Docker Management

### Start Container

Before starting a new container, ensure no existing container has the same name:
```bash
# Clean up existing container
docker stop take-a-number 2>/dev/null || true
docker rm take-a-number 2>/dev/null || true
```

### Start Container
```
docker start take-a-number
```

### Stop Container
```
docker stop take-a-number
```

### View Logs
```
docker logs take-a-number
```

### Remove Container
```
docker rm take-a-number
```

## Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install flask pytest  # Added pytest as it's supported
```

3. Run in development mode:

```bash
python app.py
```

## Testing

### Setup Testing Environment

Before running tests, set up your development environment:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

From the project root directory:

```bash
# Using unittest
python -m unittest tests/test_take_a_number.py

# Using pytest (if installed)
pytest tests/test_take_a_number.py
```

### Test Coverage

The test suite verifies:
- Sequence initialization (always starts at 1)
- Multiple independent sequences
- Thread-safe operations
- File persistence and corruption recovery
- Large number handling
- Invalid input handling
- Automatic directory creation for storage file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for any new functionality
4. Ensure all tests pass:
   ```bash
   python -m unittest tests/test_take_a_number.py
   ```
5. Commit your changes
6. Push to the branch
7. Create a Pull Request

**Note**: All pull requests must include appropriate test coverage and pass the existing test suite to be considered for merge.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the GitHub repository.

## Security Considerations

This service is designed for internal use in a trusted network environment. If exposed to the public internet, consider adding:

- Authentication
- Rate limiting
- HTTPS
- Input validation