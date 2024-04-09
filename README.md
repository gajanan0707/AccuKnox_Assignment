
# AccuKnox_Assignment

Create an API for social networking application using Django Rest Framework

# Environment Setup
Instructions on how to get a dev environment running.

# Prerequisites
List any prerequisites, libraries, OS version, etc., that are needed before installing the program.

- Example: Python 3.8+
- Example: pipenv or virtualenv


## Installation

A step-by-step series of examples that tell you how to get a development environment running.

## Clone the Repository

```bash
git clone https://github.com/gajanan0707/AccuKnox_Assignment.git
cd AccuKnox_Assignment
```

## Setting Up Virtual Environment

### 1. Install Virtual Environment

First, install virtualenv if you haven't already:
```bash
pip install virtualenv
```

### 2. Set Up a Virtual Environment
- For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

- For Unix or MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Required Packages
```bash
pip install -r requirements.txt
```
This will install all the dependencies listed in requirements.txt.

### Set Up the Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create an Admin User
```bash
python manage.py createsuperuser
```

### Run the Development Server
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/ in your web browser to view the project.






    
## API Reference

#### Signup User

```http
  POST {{url}}/api/user/signup
```

| Body | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email` | `string` | **Required**. email |
| `password` | `string` | **Required**. password |

#### Login User

```http
  POST {{url}}/api/user/login
```

| Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `email`      | `string` | **Required**. User email |
| `password`      | `string` | **Required**. User password |


#### User Search

```http
  GET {{url}}/api/user/search-users?search=
```

| QueryParams | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `search`      | `string` | search by email or username |


#### send-friend-request

```http
  POST {{url}}/api/user/send-friend-request/<int:receiver_id>/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | Token {{Authorization}} |


#### update-friend-request

```http
  POST {{url}}/api/user/update-friend-request/<int:request_id>/<str:action>/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | Token {{Authorization}} |
| `action` | `string` | accept, reject |


#### list-pending-requests

```http
  GET {{url}}/api/user/list-pending-requests/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | Token {{Authorization}} |


#### list-friends

```http
  GET {{url}}/api/user/list-friends/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | Token {{Authorization}} |