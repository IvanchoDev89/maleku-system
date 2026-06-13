import os
from enum import Enum


class FeatureFlag(str, Enum):
    STRIPE_PAYMENTS = "STRIPE_PAYMENTS"
    EMAIL_NOTIFICATIONS = "EMAIL_NOTIFICATIONS"
    BILLIONMAIL_MARKETING = "BILLIONMAIL_MARKETING"
    VENDOR_REGISTRATION = "VENDOR_REGISTRATION"
    REVIEW_SYSTEM = "REVIEW_SYSTEM"
    CHAT_SUPPORT = "CHAT_SUPPORT"
    NEWSLETTER = "NEWSLETTER"
    BLOG = "BLOG"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"


_defaults: dict[FeatureFlag, bool] = {
    FeatureFlag.STRIPE_PAYMENTS: True,
    FeatureFlag.EMAIL_NOTIFICATIONS: True,
    FeatureFlag.BILLIONMAIL_MARKETING: True,
    FeatureFlag.VENDOR_REGISTRATION: True,
    FeatureFlag.REVIEW_SYSTEM: True,
    FeatureFlag.CHAT_SUPPORT: True,
    FeatureFlag.NEWSLETTER: True,
    FeatureFlag.BLOG: True,
    FeatureFlag.MAINTENANCE_MODE: False,
}


def is_enabled(flag: FeatureFlag) -> bool:
    env_val = os.environ.get(f"FF_{flag.value}")
    if env_val is not None:
        return env_val.lower() in ("1", "true", "yes", "on")
    return _defaults.get(flag, False)


def set_enabled(flag: FeatureFlag, enabled: bool):
    os.environ[f"FF_{flag.value}"] = str(enabled)
