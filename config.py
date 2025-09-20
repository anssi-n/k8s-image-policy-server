from pathlib import Path
import yaml
from app_logger import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

def read_config(repo_whitelist):

    if not repo_whitelist:
        logger.critical("Repository whitelist environment variable REPOSITORY_WHITELIST is not set.")
        exit(1)

    repo_whitelist_file = Path(repo_whitelist)
    if not repo_whitelist_file.is_file():
        logger.critical(f"Repository whitelist file {repo_whitelist} does not exist.")
        exit(1)
    try:
        config_data = yaml.full_load(repo_whitelist_file.open())
    except Exception as _:
        logger.critical(f"{repo_whitelist} not a valid yaml file.")
        exit(1)

    if  "valid_repositories" not in config_data:
        logger.critical(f"valid_repositories not found in yaml conifg: {config_data}.")
        exit(1)

    valid_repos = set(config_data["valid_repositories"])
    logger.info(f"Configured valid image repositories: {valid_repos}")
    return valid_repos


repo_whitelist = os.environ.get("REPOSITORY_WHITELIST","")
class  ConfigHandler(FileSystemEventHandler):

    def __init__(self, whitelist: str) -> None:
        self.whitelist = whitelist
        self.valid_repos: set[str] = read_config(whitelist)

    def  on_modified(self,  event) -> None:
        logger.info(f"Repository whitelist file updated!: {event.src_path}")
        self.valid_repos = read_config(self.whitelist)

config_handler = ConfigHandler(repo_whitelist)
observer = Observer()
observer.schedule(config_handler,  path=repo_whitelist,  recursive=True)
