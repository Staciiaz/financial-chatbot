from dotenv import load_dotenv
from src.servers import Server


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()
