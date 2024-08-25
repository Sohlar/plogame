# PLO Project

This is a project for a Pot Limit Omaha Trainer. 

## Features
- Poker game implementation
- Docker with multistage builds for containerization and ease of development

## Quick Start

### Prerequisites

- Python 3.x

### Building the Trainer

1. Clone the repository:

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
- **@frontend**: Implement a frontend.

## License

This project is licensed under the MIT License.
