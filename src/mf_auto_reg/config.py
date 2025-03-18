"""
Configuration management for mf-auto-reg.
Handles loading and validation of settings from environment variables and config files.
"""
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GmailSettings(BaseModel):
    """Gmail API related settings."""
    client_id: str = Field(..., description="Gmail API client ID")
    client_secret: SecretStr = Field(..., description="Gmail API client secret")
    token_path: Path = Field(default=Path("token.json"), description="Path to token file")
    credentials_path: Path = Field(default=Path("credentials.json"), description="Path to credentials file")
    search_query: str = Field(default="[ANA Pay] ご利用のお知らせ", description="Email search query")
    max_results: int = Field(default=100, description="Maximum number of emails to fetch")
    poll_interval: int = Field(default=60, description="Polling interval in seconds")


class SupabaseSettings(BaseModel):
    """Supabase related settings."""
    url: str = Field(..., description="Supabase project URL")
    api_key: SecretStr = Field(..., description="Supabase API key")
    table_name: str = Field(default="transactions", description="Table name for storing transactions")


class SlackSettings(BaseModel):
    """Slack related settings."""
    bot_token: SecretStr = Field(..., description="Slack bot token")
    channel_id: str = Field(..., description="Slack channel ID for notifications")
    allowed_reactions: List[str] = Field(
        default=["white_check_mark", "x"],
        description="List of allowed reaction emojis"
    )


class MoneyForwardSettings(BaseModel):
    """MoneyForward related settings."""
    email: str = Field(..., description="MoneyForward login email")
    password: SecretStr = Field(..., description="MoneyForward login password")
    login_url: str = Field(
        default="https://moneyforward.com/sign_in",
        description="MoneyForward login URL"
    )
    transaction_url: str = Field(
        default="https://moneyforward.com/cf",
        description="MoneyForward transaction page URL"
    )


class Settings(BaseSettings):
    """Main settings class that combines all configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Gmail settings
    gmail: GmailSettings = Field(default_factory=GmailSettings)

    # Supabase settings
    supabase: SupabaseSettings = Field(default_factory=SupabaseSettings)

    # Slack settings
    slack: SlackSettings = Field(default_factory=SlackSettings)

    # MoneyForward settings
    moneyforward: MoneyForwardSettings = Field(default_factory=MoneyForwardSettings)

    # Debug mode
    debug: bool = Field(default=False, description="Enable debug mode")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Settings":
        """
        Load settings from environment variables and optionally from a config file.
        
        Args:
            config_path: Optional path to a YAML config file
            
        Returns:
            Settings instance
        """
        # First load from environment variables
        settings = cls()

        # If config file is provided, update settings from it
        if config_path and config_path.exists():
            import yaml
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
                settings = settings.model_validate(config_data)

        return settings


# Global settings instance
settings = Settings.load() 