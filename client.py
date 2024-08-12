import requests
import json
import base64
import time


from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def encrypt_data(public_key, data):
    data_str = json.dumps(data)
    encrypted_data = public_key.encrypt(
        data_str.encode("utf-8"),  # Convert the string to bytes
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    encrypted_data_base64 = base64.b64encode(encrypted_data)
    print(encrypted_data_base64.decode("utf-8"))
    return encrypted_data_base64


if __name__ == "__main__":
    base_url = "http://localhost:5000"
    keys_url = "http://localhost:5000/generate_keys"
    webhook_url = "http://localhost:5000/webhook_event"
    register_url = f"{base_url}/register"

    # Sample user data
    user_data = {"username": "test_user", "password": "test_pass"}

    # Make the POST request to register the user
    response = requests.post(register_url, json=user_data)

    # Check the response
    if response.status_code == 201:
        print("User registered successfully!")
        print(response.json())
    elif response.status_code == 400:
        print("Registration failed:")
        print(response.json())
    else:
        print(f"Unexpected status code: {response.status_code}")
        print(response.text)
    response = requests.get(keys_url, auth=("test_user", "test_pass"))
    print(response)
    public_key_pem = response.json()["public_key"]
    print(public_key_pem)
    public_key_pem = public_key_pem.encode("utf-8")
    public_key = serialization.load_pem_public_key(
        public_key_pem, backend=default_backend()
    )

    command = ""

    while command != "exit":
        command = input("Enter event :")
        if command == "Transaction Done":
            transaction_id = input("Enter transaction id")
            data = {"transaction_id": transaction_id}
            encrypted_data = encrypt_data(public_key=public_key, data=data)
            # response = requests.post(
            #     webhook_url,
            #     auth=("test_user", "test_pass"),
            #     json={"data": encrypted_data.decode("utf-8")},
            # )
            max_retries = 5
            initial_delay = 1
            backoff_factor = 2

            # Initialize retry counter and delay
            retries = 0
            delay = initial_delay

            # Begin retry loop
            while retries < max_retries:
                try:
                    # Attempt the POST request
                    response = requests.post(
                        webhook_url,
                        auth=("test_user", "test_pass"),
                        json={"data": encrypted_data.decode("utf-8")},
                    )

                    # Check the response status
                    if response.status_code == 200:
                        print("Request was successful!")
                        break  # Exit loop on success
                    else:
                        print(f"Received non-200 response code: {response.status_code}")

                    # Raise an error for non-200 status codes
                    response.raise_for_status()

                except requests.exceptions.HTTPError as http_err:
                    print(f"HTTP error occurred: {http_err}")
                except requests.exceptions.ConnectionError as conn_err:
                    print(f"Connection error occurred: {conn_err}")
                except requests.exceptions.Timeout as timeout_err:
                    print(f"Timeout occurred: {timeout_err}")
                except requests.exceptions.RequestException as req_err:
                    print(f"Request error occurred: {req_err}")

                # Increment retries and calculate next delay
                retries += 1
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor  # Apply exponential backoff

        elif command == "Transaction Failed":
            pass
        else:
            print("Wrong command given , to exit please write exit")
