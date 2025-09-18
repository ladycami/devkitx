#!/usr/bin/env python3
"""
Configuration Management Examples

This module demonstrates practical usage of devkitx.config_utils
including loading various config formats, environment variable handling,
and configuration validation.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from devkitx.config_utils import (
    ConfigManager,
    load_dotenv,
    load_yaml_config,
    load_toml_config,
    load_json_config,
    merge_configs,
    validate_config,
    get_config_value,
    set_config_value
)


def basic_config_loading():
    """Demonstrate loading different configuration formats."""
    print("=== Basic Configuration Loading ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample configuration files
        
        # JSON config
        json_config = {
            "app_name": "MyApp",
            "debug": True,
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_db"
            },
            "features": ["auth", "api", "ui"]
        }
        
        json_file = temp_path / "config.json"
        import json
        with open(json_file, 'w') as f:
            json.dump(json_config, f, indent=2)
        
        # YAML config
        yaml_content = """
app_name: MyApp
debug: true
database:
  host: localhost
  port: 5432
  name: myapp_db
features:
  - auth
  - api
  - ui
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""
        yaml_file = temp_path / "config.yaml"
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # TOML config
        toml_content = """
app_name = "MyApp"
debug = true

[database]
host = "localhost"
port = 5432
name = "myapp_db"

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

features = ["auth", "api", "ui"]
"""
        toml_file = temp_path / "config.toml"
        with open(toml_file, 'w') as f:
            f.write(toml_content)
        
        # .env file
        env_content = """
# Environment variables
APP_NAME=MyApp
DEBUG=true
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myapp_db
SECRET_KEY=your-secret-key-here
API_KEY=abc123def456
"""
        env_file = temp_path / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        # Load each format
        json_data = load_json_config(json_file)
        print(f"✓ Loaded JSON config: {json_data['app_name']}")
        
        yaml_data = load_yaml_config(yaml_file)
        print(f"✓ Loaded YAML config: {yaml_data['app_name']}")
        
        toml_data = load_toml_config(toml_file)
        print(f"✓ Loaded TOML config: {toml_data['app_name']}")
        
        env_data = load_dotenv(env_file)
        print(f"✓ Loaded .env file: {len(env_data)} variables")
        print(f"  Sample: APP_NAME={env_data.get('APP_NAME')}")


def config_manager_examples():
    """Demonstrate ConfigManager class usage."""
    print("\n=== ConfigManager Examples ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create base configuration
        base_config = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "ssl": False
            },
            "cache": {
                "type": "memory",
                "ttl": 3600
            }
        }
        
        base_file = temp_path / "base.json"
        import json
        with open(base_file, 'w') as f:
            json.dump(base_config, f, indent=2)
        
        # Create environment-specific overrides
        dev_config = {
            "app": {
                "debug": True
            },
            "database": {
                "name": "myapp_dev"
            }
        }
        
        dev_file = temp_path / "dev.json"
        with open(dev_file, 'w') as f:
            json.dump(dev_config, f, indent=2)
        
        # Create production overrides
        prod_config = {
            "database": {
                "host": "prod-db.example.com",
                "ssl": True,
                "name": "myapp_prod"
            },
            "cache": {
                "type": "redis",
                "host": "redis.example.com"
            }
        }
        
        prod_file = temp_path / "prod.json"
        with open(prod_file, 'w') as f:
            json.dump(prod_config, f, indent=2)
        
        # Initialize ConfigManager
        config_manager = ConfigManager([base_file, dev_file])
        config_manager.load()
        
        print("✓ ConfigManager initialized with base + dev configs")
        
        # Get configuration values with type hints
        app_name = config_manager.get("app.name", type_hint=str)
        debug_mode = config_manager.get("app.debug", type_hint=bool)
        db_port = config_manager.get("database.port", type_hint=int)
        
        print(f"  App name: {app_name}")
        print(f"  Debug mode: {debug_mode}")
        print(f"  DB port: {db_port}")
        
        # Get nested values
        db_config = config_manager.get("database", default={})
        print(f"  Database config: {db_config}")
        
        # Set new values
        config_manager.set("app.environment", "development")
        config_manager.set("database.pool_size", 10)
        
        # Save updated configuration
        updated_file = temp_path / "updated.json"
        config_manager.save(updated_file)
        print(f"✓ Saved updated configuration to {updated_file.name}")


def environment_variable_integration():
    """Demonstrate environment variable integration."""
    print("\n=== Environment Variable Integration ===")
    
    # Set some environment variables for testing
    test_env_vars = {
        "MYAPP_DATABASE_HOST": "env-db.example.com",
        "MYAPP_DATABASE_PORT": "3306",
        "MYAPP_DEBUG": "true",
        "MYAPP_SECRET_KEY": "env-secret-key",
        "OTHER_VAR": "should-be-ignored"
    }
    
    # Temporarily set environment variables
    original_env = {}
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create base configuration
            base_config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "myapp"
                },
                "debug": False,
                "secret_key": "default-secret"
            }
            
            config_file = temp_path / "config.json"
            import json
            with open(config_file, 'w') as f:
                json.dump(base_config, f, indent=2)
            
            # Initialize ConfigManager with environment variable merging
            config_manager = ConfigManager([config_file])
            config_manager.load()
            
            print("✓ Base configuration loaded:")
            print(f"  Database host: {config_manager.get('database.host')}")
            print(f"  Database port: {config_manager.get('database.port')}")
            print(f"  Debug: {config_manager.get('debug')}")
            
            # Merge environment variables with MYAPP_ prefix
            config_manager.merge_env_vars(prefix="MYAPP_")
            
            print("✓ After merging environment variables:")
            print(f"  Database host: {config_manager.get('database.host')}")
            print(f"  Database port: {config_manager.get('database.port')}")
            print(f"  Debug: {config_manager.get('debug')}")
            print(f"  Secret key: {config_manager.get('secret_key')}")
            
            # Environment variables override config file values
            assert config_manager.get('database.host') == "env-db.example.com"
            assert config_manager.get('database.port') == 3306  # Converted to int
            assert config_manager.get('debug') is True  # Converted to bool
    
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def configuration_validation():
    """Demonstrate configuration validation."""
    print("\n=== Configuration Validation ===")
    
    # Define configuration schema
    config_schema = {
        "app": {
            "name": str,
            "version": str,
            "debug": bool
        },
        "database": {
            "host": str,
            "port": int,
            "name": str,
            "ssl": bool
        },
        "cache": {
            "ttl": int
        }
    }
    
    # Valid configuration
    valid_config = {
        "app": {
            "name": "MyApp",
            "version": "1.0.0",
            "debug": True
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp_db",
            "ssl": False
        },
        "cache": {
            "ttl": 3600
        }
    }
    
    # Invalid configuration
    invalid_config = {
        "app": {
            "name": "MyApp",
            "version": "1.0.0",
            "debug": "not-a-boolean"  # Should be boolean
        },
        "database": {
            "host": "localhost",
            "port": "not-a-number",  # Should be integer
            "name": "myapp_db"
            # Missing required 'ssl' field
        },
        "cache": {
            "ttl": -1  # Negative TTL might be invalid
        }
    }
    
    # Validate configurations
    valid_result = validate_config(valid_config, config_schema)
    print(f"✓ Valid config validation: {valid_result.is_valid}")
    
    invalid_result = validate_config(invalid_config, config_schema)
    print(f"✗ Invalid config validation: {invalid_result.is_valid}")
    print("  Validation errors:")
    for error in invalid_result.errors:
        print(f"    - {error}")


def advanced_config_patterns():
    """Demonstrate advanced configuration patterns."""
    print("\n=== Advanced Configuration Patterns ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Multi-environment configuration pattern
        environments = {
            "development": {
                "database": {
                    "host": "localhost",
                    "name": "myapp_dev",
                    "debug_queries": True
                },
                "logging": {
                    "level": "DEBUG"
                }
            },
            "staging": {
                "database": {
                    "host": "staging-db.example.com",
                    "name": "myapp_staging",
                    "debug_queries": False
                },
                "logging": {
                    "level": "INFO"
                }
            },
            "production": {
                "database": {
                    "host": "prod-db.example.com",
                    "name": "myapp_prod",
                    "debug_queries": False
                },
                "logging": {
                    "level": "WARNING"
                },
                "monitoring": {
                    "enabled": True,
                    "endpoint": "https://monitoring.example.com"
                }
            }
        }
        
        # Save environment configs
        for env_name, env_config in environments.items():
            env_file = temp_path / f"{env_name}.json"
            import json
            with open(env_file, 'w') as f:
                json.dump(env_config, f, indent=2)
        
        # Load configuration based on environment
        current_env = "development"  # Could come from env var
        
        config_manager = ConfigManager([temp_path / f"{current_env}.json"])
        config_manager.load()
        
        print(f"✓ Loaded {current_env} configuration:")
        print(f"  Database host: {config_manager.get('database.host')}")
        print(f"  Debug queries: {config_manager.get('database.debug_queries')}")
        print(f"  Log level: {config_manager.get('logging.level')}")
        
        # Feature flags pattern
        feature_flags = {
            "features": {
                "new_ui": True,
                "beta_api": False,
                "advanced_analytics": True,
                "experimental_cache": False
            }
        }
        
        # Merge feature flags
        merged_config = merge_configs(config_manager.config, feature_flags)
        
        print("✓ Feature flags:")
        for feature, enabled in merged_config["features"].items():
            status = "enabled" if enabled else "disabled"
            print(f"  {feature}: {status}")


def configuration_templating():
    """Demonstrate configuration templating and interpolation."""
    print("\n=== Configuration Templating ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Configuration template with placeholders
        config_template = {
            "app": {
                "name": "${APP_NAME}",
                "version": "${APP_VERSION}",
                "environment": "${ENVIRONMENT}"
            },
            "database": {
                "url": "postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}",
                "pool_size": "${DB_POOL_SIZE}"
            },
            "redis": {
                "url": "redis://${REDIS_HOST}:${REDIS_PORT}/0"
            },
            "logging": {
                "level": "${LOG_LEVEL}",
                "file": "/var/log/${APP_NAME}.log"
            }
        }
        
        # Template variables
        template_vars = {
            "APP_NAME": "myapp",
            "APP_VERSION": "1.2.3",
            "ENVIRONMENT": "production",
            "DB_USER": "app_user",
            "DB_PASS": "secure_password",
            "DB_HOST": "db.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "myapp_prod",
            "DB_POOL_SIZE": "20",
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6379",
            "LOG_LEVEL": "INFO"
        }
        
        # Resolve template
        def resolve_template(config: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
            """Recursively resolve template variables in configuration."""
            import re
            
            def resolve_value(value):
                if isinstance(value, str):
                    # Replace ${VAR} patterns
                    def replace_var(match):
                        var_name = match.group(1)
                        return variables.get(var_name, match.group(0))
                    
                    return re.sub(r'\$\{([^}]+)\}', replace_var, value)
                elif isinstance(value, dict):
                    return {k: resolve_value(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [resolve_value(item) for item in value]
                else:
                    return value
            
            return resolve_value(config)
        
        resolved_config = resolve_template(config_template, template_vars)
        
        print("✓ Resolved configuration template:")
        print(f"  App: {resolved_config['app']['name']} v{resolved_config['app']['version']}")
        print(f"  Database URL: {resolved_config['database']['url']}")
        print(f"  Redis URL: {resolved_config['redis']['url']}")
        print(f"  Log file: {resolved_config['logging']['file']}")


def error_handling_examples():
    """Demonstrate error handling for configuration operations."""
    print("\n=== Error Handling Examples ===")
    
    # Handle missing configuration files
    try:
        config = load_json_config("nonexistent.json")
    except FileNotFoundError as e:
        print(f"✓ Handled missing config file: {type(e).__name__}")
    
    # Handle invalid JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        invalid_json_file = temp_path / "invalid.json"
        with open(invalid_json_file, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        try:
            config = load_json_config(invalid_json_file)
        except ValueError as e:
            print(f"✓ Handled invalid JSON: {type(e).__name__}")
        
        # Handle invalid YAML
        invalid_yaml_file = temp_path / "invalid.yaml"
        with open(invalid_yaml_file, 'w') as f:
            f.write('invalid: yaml: content: [')  # Invalid YAML
        
        try:
            config = load_yaml_config(invalid_yaml_file)
        except Exception as e:
            print(f"✓ Handled invalid YAML: {type(e).__name__}")
        
        # Handle type conversion errors
        config_manager = ConfigManager([])
        config_manager.config = {"port": "not-a-number"}
        
        try:
            port = config_manager.get("port", type_hint=int)
        except ValueError as e:
            print(f"✓ Handled type conversion error: {type(e).__name__}")


def performance_and_best_practices():
    """Demonstrate performance considerations and best practices."""
    print("\n=== Performance and Best Practices ===")
    
    print("Performance considerations:")
    print("1. Cache loaded configurations to avoid repeated file I/O")
    print("2. Use lazy loading for large configuration files")
    print("3. Validate configuration once at startup, not on every access")
    print("4. Use environment variables for sensitive data")
    print("5. Consider configuration hot-reloading for development")
    
    print("\nBest practices:")
    print("- Use type hints for configuration values")
    print("- Provide sensible defaults for optional settings")
    print("- Validate configuration at application startup")
    print("- Use environment-specific configuration files")
    print("- Keep sensitive data in environment variables or secret stores")
    print("- Document configuration options and their effects")
    print("- Use configuration schemas for validation")
    print("- Implement graceful degradation for missing optional configs")
    
    # Example of configuration caching
    class CachedConfigManager:
        def __init__(self, config_files):
            self.config_files = config_files
            self._cache = None
            self._last_modified = None
        
        def get_config(self):
            """Get configuration with caching and modification time checking."""
            current_modified = max(
                Path(f).stat().st_mtime for f in self.config_files if Path(f).exists()
            )
            
            if self._cache is None or current_modified > self._last_modified:
                # Reload configuration
                self._cache = self._load_config()
                self._last_modified = current_modified
            
            return self._cache
        
        def _load_config(self):
            """Load and merge all configuration files."""
            config = {}
            for config_file in self.config_files:
                if Path(config_file).exists():
                    file_config = load_json_config(config_file)
                    config = merge_configs(config, file_config)
            return config
    
    print("✓ Implemented configuration caching with modification time checking")


def limitations_and_gotchas():
    """Document known limitations and gotchas."""
    print("\n=== Limitations and Gotchas ===")
    
    print("Known limitations:")
    print("1. YAML/TOML support requires additional dependencies")
    print("2. Environment variable type conversion is basic (string/int/bool)")
    print("3. Configuration merging may not handle all edge cases")
    print("4. No built-in configuration encryption/decryption")
    print("5. File watching for hot-reload may be platform-specific")
    
    print("\nCommon gotchas:")
    print("- Environment variables are always strings initially")
    print("- Configuration merging order matters (later configs override earlier)")
    print("- Nested key access uses dot notation ('database.host')")
    print("- Type conversion failures raise exceptions")
    print("- Missing required configuration should fail fast")
    
    print("\nSecurity considerations:")
    print("- Never commit sensitive configuration to version control")
    print("- Use environment variables or secret management for credentials")
    print("- Validate and sanitize configuration values")
    print("- Be careful with configuration templating and user input")
    print("- Consider configuration file permissions")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - Configuration Management Examples")
    print("=" * 60)
    
    basic_config_loading()
    config_manager_examples()
    environment_variable_integration()
    configuration_validation()
    advanced_config_patterns()
    configuration_templating()
    error_handling_examples()
    performance_and_best_practices()
    limitations_and_gotchas()
    
    print("\n" + "=" * 60)
    print("All configuration management examples completed!")