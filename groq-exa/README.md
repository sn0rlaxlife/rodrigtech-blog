# Installation Guide

This guide will walk you through the steps to install the required dependencies and set up a virtual environment for your project.

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- Python (version 3.6 or higher)
- pip (Python package installer)

## Installation Steps

1. Clone the repository to your local machine:

    ```shell
    git clone https://github.com/sn0rlaxlife/rodrigtech-blog.git
    ```

2. Navigate to the project directory:

    ```shell
    cd groq-exa
    ```

3. Install the project dependencies from the `requirements.txt` file:

    ```shell
    pip install -r requirements.txt
    ```

4. Create a virtual environment for your project:

    ```shell
    python -m venv venv
    ```

5. Activate the virtual environment:

    - For Windows:

      ```shell
      venv\Scripts\activate
      ```

    - For macOS and Linux:

      ```shell
      source venv/bin/activate
      ```

6. Congratulations! You have successfully installed the project dependencies and set up a virtual environment.

## Usage

Now that you have everything set up, you can start using the project. Refer to the project documentation or README for further instructions.

## Setup environment variables
For Groq API
```shell
setx GROQ_API_KEY
```
For EXA AI API
```shell
setx EXA_API_KEY
```

Ensure once you are complete you run the following to remove environment variables
```shell
unset EXA_API_KEY
unset GROQ_API_KEY
```
