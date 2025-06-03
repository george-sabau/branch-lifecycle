import yaml
from pathlib import Path

def load_config(config_path='config.yaml'):
    """
    Load configuration data from a YAML file.

    Args:
        config_path (str): Path to the YAML config file.

    Returns:
        dict: Parsed configuration data.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    config_file = Path(config_path)
    if not config_file.is_file():
        raise FileNotFoundError(f"Config file {config_path} not found.")

    with config_file.open('r') as f:
        config = yaml.safe_load(f)
    return config


def format_duration(duration):
    """
    Format a timedelta duration into a human-readable string.

    Args:
        duration (timedelta): The duration to format.

    Returns:
        str: Formatted string like "X days, Y hours, Z minutes, W seconds".
    """
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
