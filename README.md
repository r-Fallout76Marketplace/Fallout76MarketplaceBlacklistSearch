# Fallout76 Marketplace Blacklist Search

**Version:** 0.1.0

**Description:**

A Flask-based web application that allows users to search for blacklisted users in the r/Fallout76Marketplace community.

## Features

- Search functionality to identify blacklisted users.
- Integration with PlayStation Network (PSN) using `psnawp`.
- Management of blacklisted users via Trello using `py-trello`.

## Requirements

- Python 3.11 or higher
- Flask 3.1.0 or higher
- Gunicorn 23.0.0 or higher
- psnawp 2.1.0 or higher
- py-trello 0.20.1 or higher
- python-dotenv 1.0.1 or higher

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/fallout76marketplaceblacklistsearch.git
   cd fallout76marketplaceblacklistsearch
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows, use 'env\Scripts\activate'
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project root directory and add the following variables:

   ```env
    NPSSO_COOKIE=<placeholder>
    TRELLO_API_KEY=<placeholder>
    TRELLO_API_SECRET=<placeholder>
    TRELLO_TOKEN=<placeholder>
    TRELLO_TOKEN_SECRET=<placeholder>
    XAPI_KEY=<placeholder>
   ```

   Replace the placeholder values with your actual credentials.

## Usage

1. **Run the Flask application:**

   ```bash
   flask run
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.

2. **Deploying with Gunicorn:**

   For production environments, it's recommended to use Gunicorn:

   ```bash
   gunicorn -w 4 app:app
   ```

   This command will start the application with 4 worker processes.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - The web framework used.
- [psnawp](https://github.com/isFakeAccount/psnawp) - PlayStation Network API Wrapper.
- [py-trello](https://github.com/sarumont/py-trello) - Trello API Wrapper.

For more detailed information on setting up a Flask project, you can refer to this [Flask project template](https://github.com/xen/flask-project-template/blob/master/README.md). 