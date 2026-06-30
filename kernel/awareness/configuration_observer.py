from __future__ import annotations 

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ConfigurationSnapshot:
    observed_at: str = field(default_factory=utc_now)
    status: str = "unknown"
    config: Dict[str, Any] = field(default_factory=dict)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observed_at": self.observed_at,
            "status": self.status,
            "config": self.config,
            "warnings": self.warnings,
        }


class ConfigurationObserver:
    """Observe AI OS runtime configuration without exposing secrets.

    This observer reports whether important configuration exists, but never
    returns secret values such as API keys or service account JSON.
    """

    def observe(self) -> ConfigurationSnapshot:
        warnings: List[Dict[str, Any]] = []
        config: Dict[str, Any] = {}

        try:
            import config as app_config

            config = {
                "drive_folder_id_configured": bool(getattr(app_config, "DRIVE_FOLDER_ID", None)),
                "google_service_account_configured": bool(getattr(app_config, "GOOGLE_SERVICE_ACCOUNT_JSON", None)),
                "openai_api_key_configured": bool(getattr(app_config, "OPENAI_API_KEY", None)),
                "openai_model": getattr(app_config, "OPENAI_MODEL", None),
                "qdrant_url_configured": bool(getattr(app_config, "QDRANT_URL", None)),
                "qdrant_api_key_configured": bool(getattr(app_config, "QDRANT_API_KEY", None)),
                "max_context_chars": getattr(app_config, "MAX_CONTEXT_CHARS", None),
            }

            for key, value in config.items():
                if key.endswith("_configured") and value is False:
                    warnings.append({
                        "code": "CONFIG_MISSING",
                        "field": key,
                        "level": "warning",
                        "message": f"Configuration field is not configured: {key}",
                    })

            return ConfigurationSnapshot(
                status="ok" if not warnings else "warning",
                config=config,
                warnings=warnings,
            )

        except Exception as exc:
            return ConfigurationSnapshot(
                status="error",
                config={},
                warnings=[{
                    "code": "CONFIG_OBSERVER_ERROR",
                    "level": "error",
                    "message": str(exc),
                    "type": type(exc).__name__,
                }],
            )


configuration_observer = ConfigurationObserver()
