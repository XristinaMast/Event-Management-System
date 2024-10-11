## Table of Contents

1. [Additional Assumptions and Deviations](#Additional-Assumptions-and-Deviations)
2. [Technologies Used](#Technologies-Used)
3. [File Descriptions](#File-Descriptions)
4. [How to Run the System](#How-to-Run-the-System)
5. [How to Use the System (with Execution Examples)](#How-to-Use-the-System-with-Execution-Examples)
6. [References](#References)

## Additional Assumptions and Deviations
- The admin is automatically created when the system starts and cannot be registered like normal users. The admin login credentials are:
  - **Username**: `admin`
  - **Password**: `@dm!n69%`
- The system assumes that events are stored in cookies.
- Event dates are compared using Python's `datetime` library, ensuring that only future events are displayed during searches.
- The admin password is encrypted for security reasons.

## Technologies Used
- **Flask**: A web framework used to create the REST API.
- **Flask-PyMongo**: An extension to integrate Flask with MongoDB.
- **MongoDB**: A NoSQL database for storing users and events.
- **Werkzeug**: Provides tools for encrypting and securely comparing passwords.
- **Docker**: Used for containerizing the Flask application and MongoDB for easy deployment and scaling.
- **Python 3.9**: The programming language used to write the application.
- **pymongo**: The native Python driver for connecting to MongoDB.

## File Descriptions

- **code.py**: The main application file containing all the API routes, including user registration, login, event creation, etc.
- **Dockerfile**: Contains instructions for building the Docker image of the Flask application, installing dependencies, and starting the app.
- **docker-compose.yaml**: Defines the services (Flask and MongoDB), their configurations, and network settings. It manages the execution of multiple containers.
- **requirements.txt**: A list of Python dependencies required for the project (Flask, Flask-PyMongo, Werkzeug, pymongo).
- **/data/**: A folder mounted to the MongoDB container for data storage, ensuring data persistence even if the container is deleted.

## How to Run the System

### Prerequisites
Before running the system, ensure the following are installed:

- **Docker**: Docker allows you to run the application inside containers, so you can run the MongoDB database and Flask application without having to install everything separately.
- **Docker Compose**: Lets you start multiple services (Flask, MongoDB) simultaneously and manage them through `docker-compose.yaml`.

### Steps to Run

1. **Clone the Repository**: First, download the project files from GitHub or the storage location where they are hosted. Run the following command to clone the repository:
   ```bash
   git clone https://github.com/XristinaMast/YpoxreotikiErgasia24_E20095_Mastoraki_Xristina-Eleni
   cd your-repository
   ```
   This command creates a local copy of the project and takes you to the appropriate folder where the `docker-compose.yaml` file is located.

2. **Create and Start the Application**: 
   Docker Compose is used to start both the Flask application and MongoDB in separate containers. Once in the correct folder, run the following command:
   ```bash
   docker-compose up
   ```
   What happens when you run the above command:
   - **MongoDB container**: A container with MongoDB starts, and the database is accessible on port 27017. A volume (./data:/data/db) ensures that data is stored on your local disk and not only inside the container.
   - **Flask container**: A container with the Python Flask API starts on port 5000, communicating with MongoDB via the address `mongodb://mongodb:27017/HospitalDB`.
   If all containers start successfully, you will see something like this in your terminal:

   ```bash
   Starting mongodb ... done
   Starting flask ... done
   flask |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
   ```

3. **Access the Application**:  
   To confirm that the application is running correctly, open a browser and go to the address:
   ```
   http://localhost:5000
   ```

4. **Stopping the System**:  
   To stop the containers, press `Ctrl + C` in the terminal and then run:
   ```bash
   docker-compose down
   ```
   This command will stop and remove the containers, but the data in the database will be retained in the `./data` folder.

### Data Persistence
The `./data` folder created on the local disk is mounted to the MongoDB container. This means that even if you delete the container, the data will not be lost.

## How to Use the System (with Execution Examples)

Below are details on interacting with the system via the API endpoints. You can use tools like **Postman** or **cURL** to send requests.

### 1. **Admin Registration (Predefined Admin)**
   - The admin is automatically created when the system starts and does not need to be registered via the API.

   - Credentials:
     - Username: `admin`
     - Password: `@dm!n69%`

### 2. **User Registration**
  Any new user can register in the system with a POST request to the `/register` endpoint. The API accepts a JSON object containing the user's details.
   - **URL**: `/register`
   - **Method**: `POST`
   - **Example Request**:
     ```bash
     curl -X POST http://localhost:5000/register \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Doe",
       "email": "john@gmail.com",
       "username": "john123",
       "password": "mypassword"
     }'
     ```
   - **Expected Response**:
     - 201: "User registered successfully!"
     - 409: "Username or Email already exists!"

### 3. **User Login**
  After registering, a user can log into the system to gain access to features like creating and managing events.
   - **URL**: `/login`
   - **Method**: `POST`
   - **Example Request**:
     ```bash
     curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john123",
       "password": "mypassword"
     }'
     ```
   - **Expected Response**:
     - 200: "Login successful!"
     - 401: "Invalid username or password!"
   
   After login, we can use the session cookie to perform other actions (creating events, viewing events, etc.).

### 4. **Creating an Event**
  Users can create events after logging in. These events will be available for viewing and searching by other users.
   - **URL**: `/events`
   - **Method**: `POST`
   - **Example Request**:
     ```bash
     curl -X POST http://localhost:5000/events \
     -H "Content-Type: application/json" \
     -b cookie.txt \
     -d '{
       "event_title": "Tech Conference",
       "event_description": "A conference on tech trends",
       "event_date": "2024-10-10",
       "event_hour": "10:00",
       "event_placement": "New York",
       "event_type": "conference"
     }'
     ```
   - **Expected Response**:
     - 201: "Event created successfully!"
     - 403: "Please log in first!" (if the user is not logged in)

### 5. **Viewing All Events**
  Users can view all future events registered in the system with a GET request to the `/events` endpoint.
   - **URL**: `/events`
   - **Method**: `GET`
   - **Example Request**:
     ```bash
     curl -X GET http://localhost:5000/events -b cookie.txt
     ```
   - **Expected Response**:  
     A list of all upcoming events in JSON format.

     **Example response:**
     ```json
     [
       {
         "_id": "614c0e7e6f8b4c35b048c123",
         "event_title": "Tech Conference",
         "event_description": "A conference on tech trends",
         "event_date": "2024-10-10",
         "event_hour": "10:00",
         "event_placement": "New York",
         "event_type": "conference"
       }
     ]
     ```

### 6. **Updating an Event**
  The creator of an event can update it using the `/events/<id>` endpoint. The update can include fields like title, description, date, etc.
   - **URL**: `/events/<id>`
   - **Method**: `PUT`
   - **Example Request**:
     ```bash
     curl -X PUT http://localhost:5000/events/614c0e7e6f8b4c35b048c123 \
     -H "Content-Type: application/json" \
     -b cookie.txt \
     -d '{
       "event_title": "Updated Tech Conference",
       "event_description": "An updated conference description",
       "event_date": "2024-10-15",
       "event_hour": "

14:00"
     }'
     ```
   - **Expected Response**:
     - 200: "Event updated successfully!"
     - 403: "Unauthorized!" (if the event does not belong to the logged-in user)

### 7. **Deleting an Event**
  Users can delete their own events using the `/events/<id>` endpoint.
   - **URL**: `/events/<id>`
   - **Method**: `DELETE`
   - **Example Request**:
     ```bash
     curl -X DELETE http://localhost:5000/events/614c0e7e6f8b4c35b048c123 -b cookie.txt
     ```
   - **Expected Response**:
     - 200: "Event deleted successfully!"
     - 403: "Unauthorized!" (if the event does not belong to the logged-in user)
