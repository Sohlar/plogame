# PLO Project

This is a Django project for a Poker game. The project uses Django Channels for handling WebSockets and real-time communication.

## Features

- Django 5.0.7
- Django Channels for WebSocket support
- Poker game implementation

## Quick Start

### Prerequisites

- Python 3.x
- Django 5.0.7

### Installation

1. Clone the repository:

    `git clone https://github.com/yourusername/plo_project.git`
    
    `cd plo_project`

2. Create a virtual environment and activate it:

    `python3 -m venv venv`
    
    `source venv/bin/activate`  (On Windows use `venv\Scripts\activate`)

3. Install the required packages:

    `pip install -r requirements.txt`

4. Apply migrations:

    `python manage.py migrate`

5. Run the development server:

    `daphne plo_project.asgi:application`

### Running the Poker Game

You can sample the game from the command line interface using the following command:

`python3 ./poker/cli_game`

## Project Structure

- `plo_project/settings.py`: Main settings file for the Django project.
- `poker/cli_game`: Command line interface for sampling the Poker game.

## Settings

Key settings in `plo_project/settings.py`:

- `INSTALLED_APPS`: Includes Django apps and the `channels` app for WebSocket support.
- `ASGI_APPLICATION`: Points to the ASGI application for Channels.
- `CHANNEL_LAYERS`: Configuration for Channels layers.
- `DATABASES`: Configured to use SQLite by default.

For more details, refer to the [Django documentation](https://docs.djangoproject.com/en/5.0/).

## TODO

- **Finish Communication Protocol**: Finalize the communication protocol for real-time game updates and player interactions.
- **Dynamic HTML Generation from WebSocket**: Implement dynamic HTML updates based on WebSocket messages to enhance the user experience.
- **Model Training**: Develop and train machine learning models to improve game strategies and player experience.
- **Automated Testing**: Implement comprehensive unit and integration tests to ensure code quality and reliability.
- **Continuous Integration/Continuous Deployment (CI/CD)**: Set up CI/CD pipelines for automated testing and deployment.
- **Scalability Improvements**: Optimize the application for scalability to handle a large number of concurrent users.
- **Security Enhancements**: Conduct security audits and implement best practices to secure the application.
- **Documentation**: Improve and expand project documentation for developers and users.


## License

This project is licensed under the MIT License.
