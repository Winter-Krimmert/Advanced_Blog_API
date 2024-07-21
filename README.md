# Advanced Blog API

## Overview

The **Advanced Blog API** is a comprehensive blogging platform built using Flask and Flask-SQLAlchemy. This application allows users to create, manage, and interact with blog posts and comments while providing administrators with tools to manage users and moderate content. The API includes features such as JWT authentication, rate limiting, caching, and Swagger documentation.

This project aims to offer a robust blogging solution that supports:
- User management
- Blog post creation and management
- Commenting on posts
- Secure API access with JWT
- Rate limiting and caching for performance
- Interactive API documentation

The API is also thoroughly tested to ensure reliability and robustness. Test cases cover various scenarios for all major functionalities, including user management, post management, and comment management.

## Features

- **User Management**: CRUD operations for managing users.
- **Post Management**: CRUD operations for blog posts.
- **Comment Management**: CRUD operations for comments on posts.
- **JWT Authentication**: Secure endpoints using JSON Web Tokens.
- **Rate Limiting**: Protect endpoints with request limits.
- **Caching**: Improve performance with caching for GET requests.
- **Swagger Documentation**: Interactive API documentation using Swagger UI.
- **Comprehensive Testing**: Automated tests for all major functionalities and endpoints.

## Technologies Used

- **Flask**: Micro web framework for Python that provides a lightweight and modular approach to building web applications.
- **Flask-SQLAlchemy**: SQLAlchemy integration for Flask that simplifies database interactions and management.
- **Flask-Migrate**: Tool for handling database migrations, making it easier to evolve your database schema.
- **Flask-Limiter**: Provides rate limiting functionality to control API usage and prevent abuse.
- **Flask-Caching**: Caching support to enhance performance by reducing redundant processing of GET requests.
- **Flask-Swagger-UI**: Integrates Swagger UI with Flask for interactive API documentation.
- **Marshmallow**: A library for object serialization and deserialization, used for validating and formatting input and output data.
- **SQLite**: Lightweight database used for development and testing.
- **JWT**: JSON Web Tokens for secure authentication and authorization.
- **pytest**: Testing framework used for ensuring the reliability and correctness of the API.

## Getting Started

### Prerequisites

Before getting started, ensure you have the following:

- Python 3.12 or higher
- pip (Python package installer)
- virtualenv (recommended for creating isolated environments)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Winter-Krimmert/Advanced_Blog_API.git
   cd Advanced_Blog_API
