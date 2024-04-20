# Recommender System

This repository contains code for a recommender system built with FastAPI and collaborative filtering techniques. The system provides recommendations for events and users based on their interactions and preferences.

## Overview

The recommender system consists of three main files:

1. **recommender.py**: This file contains the core functionality of the recommender system. It utilizes FastAPI for creating endpoints to serve recommendations and interactions. The system employs both content-based and collaborative filtering techniques to generate personalized recommendations.

2. **update_parameter.py**: Here, content-based recommendation algorithms are implemented. It uses data from user and event categories to calculate similarities and recommend relevant events to users.

3. **Config.py**: This file establishes a connection to the PostgreSQL database and handles user authentication using JSON Web Tokens (JWT).

## Installation

To run the recommender system locally, follow these steps:

1. Clone this repository to your local machine.
   ```bash
   git clone https://github.com/your_username/recommender-system.git
2. Install the required dependencies.
   ```bash
   pip install -r requirements.txt
3. Set up your PostgreSQL database and configure the environment variables for database connection and JWT authentication. Make sure to update the .env file with your database credentials and JWT settings.
4. Once the server is running, you can access the API endpoints to get recommendations for events or users.

## Usage
The recommender system provides two main endpoints:

/event/: Accepts POST requests with parameters for event scoring. It returns recommended events based on similarity scores.
/user/: Accepts POST requests with parameters for user scoring. It returns recommended events for a given user.

Hint: Make sure to include a valid JWT token in the request headers for authentication.

## Contributing
Contributions to this project are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
