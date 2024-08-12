
# Webhook Simulation Project

## Overview

This project simulates a webhook event handling system. The application consists of a server that manages user registration, key generation, and secure event handling. Events are encrypted using RSA public key encryption on the client side, sent to the server, decrypted with the corresponding private key, and securely stored.

## Webhook Concept

### What is a Webhook?

A webhook is a user-defined HTTP callback. It is a mechanism that allows one system to send real-time data to another whenever a particular event occurs. Unlike traditional polling mechanisms, where a client repeatedly requests information from a server, webhooks push data to the client when an event occurs, providing a more efficient and real-time update mechanism.

### How This Project Simulates a Webhook

In this simulation:
1. **User Registration**: A new user can register with a username and password.
2. **Key Generation**: After registration, a unique RSA key pair (public and private keys) is generated for the user.
3. **Client Event Trigger**: The client simulates an event (e.g., "Transaction Done") and encrypts the event data using the server's public key.
4. **Server Decryption and Storage**: The encrypted data is sent to the server, which decrypts it using the corresponding private key and stores the decrypted event data.

## Project Structure

```plaintext
.
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── venv/                 # Virtual environment directory
└── README.md             # Project documentation
```

### Detailed Flow

1. **User Registration**:
   - Endpoint: \`/register\`
   - Method: \`POST\`
   - Payload: \`{ "username": "test_user", "password": "test_pass" }\`
   - Registers a new user with hashed password storage.

2. **Key Generation**:
   - Endpoint: \`/generate_keys\`
   - Method: \`GET\`
   - Requires Basic Auth.
   - Generates and stores RSA public/private key pair.

3. **Event Handling (Webhook Simulation)**:
   - Endpoint: \`/webhook_event\`
   - Method: \`POST\`
   - Requires Basic Auth.
   - The client encrypts event data using the public key and sends it to this endpoint.
   - The server decrypts the data and stores it securely.

## Setup & Installation

### Prerequisites

- Python 3.x
- Virtual environment (optional but recommended)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/webhook-simulation.git

   cd webhook-simulation
   ```

2. **Set up a virtual environment**:

   ``` bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use \`venv\Scripts\activate\`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Project

1. **Initialize the Database**:
   
   The database will be automatically initialized on the first run.

2. **Start the Flask Server**:

   ```bash
   python app.py
   ```

3. **Simulate Webhook Events**:
   
   Run the client-side script to simulate event handling:

   ```bash
   python client.py
   ```

   You can interact with the system by entering commands such as "Transaction Done" and providing a transaction ID.

## Future Scope

Yet to be decided 
, Open for suggestions : )

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (\`git checkout -b feature-branch\`).
3. Make your changes.
4. Commit and push (\`git push origin feature-branch\`).
5. Create a Pull Request.

## License

This project is licensed under the MIT License 

## Acknowledgments

- Flask framework for providing an easy way to create web servers ⚡.
- The cryptography library for secure key handling and encryption #️⃣.
- Sqlite3 for lightweight database management 🙇‍♂️.
