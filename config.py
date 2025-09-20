from pathlib import Path
import yaml
from app_logger import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

repo_whitelist = Path(os.environ.get("REPOSITORY_WHITELIST",""))
if not repo_whitelist:
    logger.critical("REPOSITORY_WHITELIST environment variable is not defined!")
    exit(1)

def read_config(repo_whitelist: Path): 

    if not repo_whitelist.is_file():
        logger.critical(f"Repository whitelist file {repo_whitelist} does not exist.")
        exit(1)
    try:
        config_data = yaml.full_load(repo_whitelist.open())
    except Exception as _:
        logger.critical(f"{repo_whitelist} not a valid yaml file.")
        exit(1)

    if  "valid_repositories" not in config_data:
        logger.critical(f"valid_repositories not found in yaml conifg: {config_data}.")
        exit(1)

    valid_repos = set(config_data["valid_repositories"])
    logger.info(f"Configured valid image repositories: {valid_repos}")
    return valid_repos


class  ConfigHandler(FileSystemEventHandler):

    def __init__(self, whitelist: Path, app_config_handler: "AppConfigHandler") -> None:
        self.whitelist_config = str(whitelist)
        self.app_config_handler = app_config_handler
        self.valid_repos: set[str] = read_config(whitelist)

    def _reload_config(self, event):
        logger.info(f"Updating valid repos from {self.whitelist_config}. Valid repos before: {self.valid_repos}")
        self.valid_repos = read_config(Path(self.whitelist_config))
        logger.info(f"Updating valid repos from {self.whitelist_config}. Valid repos after: {self.valid_repos}")
        logger.info("Resetting observer")
        self.app_config_handler.reset_observer()

    def  on_modified(self,  event) -> None:
        logger.info(f"{event.src_path} was modified! Reloading configuration.")
        self._reload_config(event)

class AppConfigHandler:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config_handler = ConfigHandler(self.config_file, self)
        self.reset_observer()
        logger.info(f"AppConfigHandler initialized with resolved config file: {self.config_file.resolve()}")

    def reset_observer(self):
        logger.info(f"Resetting observer with resolved config file {self.config_file.resolve()}")
        self.observer = Observer()
        self.observer.schedule(self.config_handler,  path=str(self.config_file.resolve()),  recursive=False)
        self.observer.start()
    
    @property
    def valid_repos(self) -> set[str]:
        return self.config_handler.valid_repos

config_handler = AppConfigHandler(repo_whitelist)