from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="USBIPGUI_")

    host: str = "0.0.0.0"
    port: int = 8000
    usbip_port: int = 3240
    # Prefix usbip commands with sudo -n (requires sudoers configuration)
    use_sudo: bool = True
    log_level: str = "info"


settings = Settings()
