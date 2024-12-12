import os
import subprocess


def run_script(script_name, args):
    """
    Executes a bash script with the provided arguments.
    
    Args:
        script_name (str): The name of the script to execute.
        args (list): A list of arguments to pass to the script.

    Returns:
        tuple: A tuple containing:
            - output (str): The standard output from the script execution.
            - error (str): The standard error from the script execution, if any.

    Raises:
        FileNotFoundError: If the script does not exist in the specified path.
    """
    base_dir = os.getenv("SCRIPTS_DIR", os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    script_path = os.path.join(base_dir, script_name)

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    result = subprocess.run([script_path] + args, capture_output=True, text=True)

    if result.returncode != 0:
        return None, result.stderr

    return result.stdout.strip(), None


def parse_line_to_dict(line):
    """
    Converts a line of script output into a dictionary with the following keys:
    - username
    - folder
    - numberMessages
    - size

    Example input:
        "user1 folder1 10 messages 1024"

    Returns:
        dict: A dictionary containing:
            - username (str): The username extracted from the line.
            - folder (str): The folder name extracted from the line.
            - numberMessages (int): The number of messages.
            - size (int): The size in bytes.

    Args:
        line (str): A line of output from the script.

    Raises:
        ValueError: If the line does not have the expected format or cannot be parsed.

    Example return:
        {
            "username": "user1",
            "folder": "folder1",
            "numberMessages": 10,
            "size": 1024
        }
    """
    parts = line.split()

    if len(parts) < 5:
        raise ValueError(f"Provided line is not correctly formatted: {line}")

    try:
        return {
            "username": parts[0],
            "folder": parts[1],
            "numberMessages": int(parts[2]),
            "size": int(parts[4]),
        }
    except (ValueError, IndexError) as e:
        raise ValueError(f"Error processing the line: {line}. Details: {e}")
