# PLO Project

This is a project for a Pot Limit Omaha Trainer. 

## Features
- Poker game implementation
- Docker with multistage builds for containerization and ease of development

## Quick Start

### Prerequisites

- Docker and Docker Compose

For local development without Docker:
- Python 3.x
<<<<<<< HEAD
- Node.js and npm (for frontend)


## Quick Start with Docker
=======

### Building the Trainer
>>>>>>> origin/master

1. Clone the repository:
    ```
    git clone https://github.com/yourusername/plo_project.git
    cd plo_project
    ```

<<<<<<< HEAD
2. Build and run the Docker containers:
    ```
    docker-compose up --build
    ```

3. Access the application at `http://localhost:8000`

## Local Development Setup (without Docker)

If you prefer to set up the project locally without Docker:

1. Set up a Python virtual environment and install backend dependencies:
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

2. Apply migrations:
    ```
    python manage.py migrate
    ```

3. Run the development server:
    ```
    daphne plo_project.asgi:application
    ```

4. In a separate terminal, set up and run the frontend:
    ```
    cd frontend
    npm install
    npm start
    ```

## Project Structure

- `plo_project/`: Main Django project directory
- `poker/`: Django app for poker game logic
- `frontend/`: React-based frontend application
- `Dockerfile`: Docker configuration for the backend
- `docker-compose.yml`: Docker Compose configuration for the entire project

## Key Components

### Backend

- `plo_project/settings.py`: Main settings file for the Django project
- `poker/consumers.py`: WebSocket consumer for real-time game updates
- `poker/models.py`: Database models for the poker game

### Frontend

- `frontend/src/App.js`: Main React component and routing setup
- `frontend/src/components/`: React components for various features

## Development

- For backend development, work in the Django project and app directories.
- For frontend development, work in the `frontend/` directory.
- When using Docker, changes to the code will require rebuilding the containers:
    ```
    docker-compose up --build
    ```

## Building the Frontend

To build the React frontend and integrate it with Django:
    ```
    ./build_react.sh
    ```
This script will build the React app, remove old build files, and move the new build files to the correct locations for Django to serve.

## Testing

- Backend tests: `docker-compose run web python manage.py test`
- Frontend tests: `docker-compose run frontend npm test`
=======
    `git clone https://github.com/yourusername/plo_project.git`
    
    `cd plogame/scripts`

    `./build_base_image.sh`

   `./build_trainer.sh`

    `docker run -it -v ./models:/app/models plo_trainer /bin/bash`

    `python3 ./train.py`



### Building/Running the Poker Game

You can sample the game from the command line interface using the following command:

`./build_game.sh`

`docker run -it -v ./models:/app/models plo /bin/bash`

## Project Structure

- `./ai`: Command line interface for sampling the Poker game and training the models.
- `./game`: Frontend application for interacting with the poker game.
- `scripts`: Scripts folder for building all the images/multiple stages of docker builds.
>>>>>>> origin/master

## Sim logs

To view simulation logs:
    ```
    docker-compose logs -f web
    ```

## TODO

- Finish Communication Protocol
- Dynamic HTML Generation from WebSocket
- Model Training
- Automated Testing
- CI/CD Setup
- Scalability Improvements
- Security Enhancements
- Documentation
- Frontend: Enhance User Interface
- Frontend: Implement State Management

##WIP
- **Model Training**: Develop and train machine learning models to improve game strategies and player experience.


## TODO

- **Finish Communication Protocol**: Finalize the websocket protocol for real-time game updates and player interactions.
- **Dynamic HTML Generation from WebSocket**: Implement dynamic HTML updates based on WebSocket messages to enhance the user experience.
- **Automated Testing**: Implement comprehensive unit and integration tests to ensure code quality and reliability.
- **Continuous Integration/Continuous Deployment (CI/CD)**: Set up CI/CD pipelines for automated testing and deployment.
- **Scalability Improvements**: Optimize the application for scalability to handle a large number of concurrent users.
- **Security Enhancements**: Conduct security audits and implement best practices to secure the application.
- **Documentation**: Improve and expand project documentation for developers and users.
- **@frontend: Enhance User Interface**: Improve the React-based frontend with more interactive features and responsive design.
- **@frontend**: Implement a frontend.

## License

This project is licensed under the MIT License.
