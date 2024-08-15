# PLO Project

This is a Django project for a Pot Limit Omaha Trainer. The project uses Django Channels for handling WebSockets and real-time communication.

## Features

- Django 5.0.7
- Django Channels for WebSocket support
- Poker game implementation
- @frontend: React-based frontend

## Quick Start

### Prerequisites

- Python 3.x
- Django 5.0.7
- Node.js and npm (for frontend)

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

### @frontend Setup

1. Navigate to the frontend directory:

    `cd frontend`

2. Install dependencies:

    `npm install`

3. Start the development server:

    `npm start`

### @build_react.sh

To build the React frontend and move the built files to the appropriate Django directories, run:

`./build_react.sh`

This script will:
1. Build the React app
2. Remove old build files from Django directories
3. Move the new build files to the correct locations for Django to serve

## Project Structure

- `plo_project/settings.py`: Main settings file for the Django project.
- `poker/cli_game`: Command line interface for sampling the Poker game.
- `frontend/`: React-based frontend application.
- `build_react.sh`: Script to build and integrate the React frontend with Django.

## Settings

Key settings in `plo_project/settings.py`:

- `INSTALLED_APPS`: Includes Django apps and the `channels` app for WebSocket support.
- `ASGI_APPLICATION`: Points to the ASGI application for Channels.
- `CHANNEL_LAYERS`: Configuration for Channels layers.
- `DATABASES`: Configured to use SQLite by default.

For more details, refer to the [Django documentation](https://docs.djangoproject.com/en/5.0/).

## @frontend

The frontend is built with React and includes the following key components:

- Material-UI for styling
- React Router for navigation
- A poker strategy grid component

## Sim logs
`tail -f poker_game.log`

## TODO

- **Finish Communication Protocol**: Finalize the communication protocol for real-time game updates and player interactions.
- **Dynamic HTML Generation from WebSocket**: Implement dynamic HTML updates based on WebSocket messages to enhance the user experience.
- **Model Training**: Develop and train machine learning models to improve game strategies and player experience.
- **Automated Testing**: Implement comprehensive unit and integration tests to ensure code quality and reliability.
- **Continuous Integration/Continuous Deployment (CI/CD)**: Set up CI/CD pipelines for automated testing and deployment.
- **Scalability Improvements**: Optimize the application for scalability to handle a large number of concurrent users.
- **Security Enhancements**: Conduct security audits and implement best practices to secure the application.
- **Documentation**: Improve and expand project documentation for developers and users.
- **@frontend: Enhance User Interface**: Improve the React-based frontend with more interactive features and responsive design.
- **@frontend: State Management**: Implement a state management solution (e.g., Redux) for more complex frontend logic.

## License

This project is licensed under the MIT License.
