"""Server entry point for ms_test — delegates to the application factory."""
from ms_test.application.app import start_server

if __name__ == "__main__":
    start_server()
