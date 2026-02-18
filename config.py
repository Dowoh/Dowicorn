
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    environments=True,
    merge_enabled=True,
    settings_files=[
        'config/settings.toml',
        'config/settings.development.toml',
        'config/settings.production.toml',
        'config/.secrets.toml',
        'config/.secrets.development.toml',
        'config/.secrets.production.toml',
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
