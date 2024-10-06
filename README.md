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

### Building the Trainer

1. Clone the repository:

    `git clone https://github.com/yourusername/plo_project.git`

    `cd plogame`
    

2. Build and run the trainer:

    `cd plogame/scripts`

    `./build_base_image.sh`

    `cd ../ai && ./start.sh`

    `docker run -it --gpus all -v ./models:/app/models --name plo_trainer --network plo_network -p 8000:8000 plo_trainer`

    `python3 ./train.py`

### Building/Running the Poker Game

You can sample the game from the command line interface using the following command:

`./build_game.sh`

`docker run -it -v ./models:/app/models plo /bin/bash`

### Building/Running the Poker Game for Development work

You can sample the game from the command line interface using the following command:

`./build_game.sh`

`docker run -it -v ./models:/app/models -v ./game/Backend:/app plo /bin/bash`

If you have docker-compose-v2 on your linux machine this is setup to bind the volumes for you

`docker compose up -d`

`docker exec -it plo /bin/bash`

If you make changes to the python files you will need to reboot the container to see it

`docker restart plo`

### Service Design Overview

![overview](https://media.wrigglyt.xyz/images/OverallServiceFlow.png)

![frontend](https://media.wrigglyt.xyz/images/FrontEnd.png)

![backend](https://media.wrigglyt.xyz/images/Backend.png)


## Project Structure

- `./ai`: Command line interface for sampling the Poker game and training the models.
- `./game`: Frontend application for interacting with the poker game.
- `scripts`: Scripts folder for building all the images/multiple stages of docker builds.

## AI Component

The AI component includes:
- A command-line interface (CLI) game implementation
- A Deep Q-Network (DQN) agent for AI decision-making
- A training script for the AI
- Metrics collection for monitoring AI performance and system resources

### Training the AI
Run the training script: `python train.py`

## WIP
- **Model Training**: Develop and train machine learning models to improve game strategies and player experience.
- **Finish Communication Protocol**: Finalize the websocket protocol for real-time game updates and player interactions.

## TODO

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
