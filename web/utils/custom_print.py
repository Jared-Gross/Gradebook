from datetime import datetime

from utils.colors import Colors

messages = []
connected_clients = []
expected_clients: dict = {
    "10.0.0.75": "Jordan",
    "10.0.0.155": "Justin",
    "10.0.0.5": "Lynden",
}


def convert_set_to_list(s):
    return list(map(lambda x: x, s))


class CustomPrint:
    @staticmethod
    def print(*args, **kwargs):
        """
        This is a customized print function that formats and colors the output text and also displays
        the IP addresses of connected clients if provided.
        """
        global messages, connected_clients
        try:
            connected_clients = convert_set_to_list(kwargs["connected_clients"])
            connected_clients = [
                connected_client.request.remote_ip
                for connected_client in connected_clients
            ]
        except Exception:
            connected_clients = []
        text = " ".join(str(arg) for arg in args)
        formatted_text = f"{Colors.BOLD}{str(datetime.now())} - {text}{Colors.ENDC}"
        formatted_text = formatted_text.replace(
            "INFO", f"{Colors.OKGREEN}INFO{Colors.BOLD}"
        )  # Green
        formatted_text = formatted_text.replace(
            "ERROR", f"{Colors.ERROR}ERROR{Colors.BOLD}"
        )  # Red
        formatted_text = formatted_text.replace(
            "WARN", f"{Colors.WARNING}WARN{Colors.BOLD}"
        )  # Yellow
        # messages.append(formatted_text)
        # if len(messages) > 50:
        #     messages = messages[50:]
        print(formatted_text)
        # print_clients()
