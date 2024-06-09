# File Sharing 

A simple file-sharing site built with Python and Flask. This project allows users to upload and share files easily.

## Features

- Upload files to the server
- Share files
- View a list of uploaded files
- Download shared files


## Working

<a href="https://drive.google.com/file/d/1ajB1Y6FPg4740GM85fNhsfRW9jQNHhgA/view?usp=drive_link"> Click here to view working of the project</a>

## Deployment Steps

1. Provisioning Infrastructure

- Choose a cloud provider (e.g., AWS, DigitalOcean).
- Set up a VM or use a managed service to host the application.

2. Containerization

- Create and push a Docker image to a container registry (e.g., Docker Hub).

3. Database Setup

- Use a managed database service (e.g., Amazon RDS).

4. Deploying the Application

- Use Docker Compose to deploy the application and database containers to the VM.

5. Environment Configuration

- Store environment variables in a .env file and reference it in Docker Compose.
