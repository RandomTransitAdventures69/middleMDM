# middleMDM Server Package

The macOS and Linux release archives contain the server source, a setup script, and a launcher. They require Python 3.8 or newer and an internet connection during setup to install Python dependencies.

Extract the matching archive, then run:

```bash
./install.sh
```

The installer creates a virtual environment, generates separate local secrets if `server/.env` does not already exist, initializes the database, and prompts for the initial administrator password. The enrollment secret is stored in `server/.env` for client configuration. Start or stop the local server with:

```bash
./run.sh
```

The server listens on `http://127.0.0.1:5001/` and is bound to the local machine only. Press Ctrl+C in the terminal to stop it. This package is configured for local development; use the [server deployment guide](docs/server-setup.md) for a production HTTPS deployment.
