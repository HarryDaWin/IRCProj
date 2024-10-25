# IRCProj

IRCProj is a basic implementation of an Internet Relay Chat (IRC) client and server written in Python. This project demonstrates foundational networking concepts and allows for basic real-time messaging functionality across a server and multiple clients.

## Features

- **Server**: Listens for incoming client connections and manages client messaging and broadcasting.
- **Client**: Allows users to connect to the server, join channels, and send messages.
- **Multi-user chat**: Support for multiple clients connected to a single server.
- **Commands**: Supports basic IRC commands

## Getting Started

### Prerequisites

- Python 3
- Sockets library or specific modules.

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/HarryDaWin/IRCProj.git
    cd IRCProj
    ```

2. Install required dependencies:
    ```bash
    # For Python:
    pip install -r requirements.txt
    ```

### Usage

1. **Start the Server**:
    ```bash
    python server.py
    ```
    The server will start and listen on the specified port for incoming client connections.

2. **Start a Client**:
    ```bash
    python client.py
    ```
    Once the client connects, you can begin interacting with the IRC server.

## Project Structure

- `server.py`: Contains the server code for managing clients and channels.
- `client.py`: Contains the client code for interacting with the server.


