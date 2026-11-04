"""System settings model."""
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(20), default="string", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def get_value(self):
        if self.value_type == "integer":
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.value_type == "boolean":
            return str(self.value).lower() in ("true", "1", "yes", "on")
        elif self.value_type == "json":
            import json
            try:
                return json.loads(self.value or "{}")
            except (ValueError, TypeError):
                return {}
        return self.value

    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.get_value()
        return default

    @classmethod
    def set(cls, key, value, value_type="string", description=None):
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            setting = cls(key=key, value=str(value), value_type=value_type, description=description)
            db.session.add(setting)
        else:
            setting.value = str(value)
            setting.value_type = value_type
            if description:
                setting.description = description
        db.session.commit()
        return setting

    def __repr__(self):
        return f"<SystemSetting {self.key}>"
