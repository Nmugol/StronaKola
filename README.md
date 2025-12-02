# Strona Koła Naukowego

This project contains the backend and frontend for the student group website.

## Running the application with Docker Compose

To run the entire application (both backend and frontend), you need to have Docker and Docker Compose installed.

1.  **Clone the repository** (if you haven't already).

2.  **Navigate to the project root directory.**

3.  **Run Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images for both the frontend and backend services and start the containers.

4.  **Access the application:**
    *   The frontend will be available at [http://localhost:8080](http://localhost:8080).
    *   The backend API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Services

-   **frontend:** A React application served with Nginx. It's accessible on port `8080`.
-   **backend:** A FastAPI application. The API is accessible on port `8000`. Nginx on the frontend service proxies requests to `/api` and `/static` to this service.

### Admin Access

To use the administrative functions, navigate to the "Admin View" on the website and enter your API key. The default key is `super_secret_api_key` but can be configured through environment variables in the backend.
