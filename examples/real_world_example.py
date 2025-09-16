#!/usr/bin/env python3
"""
Real-world example using devtools-py.

This example demonstrates how devtools-py can be used in a typical
development scenario: building a user management system with configuration,
validation, security, and data processing.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# Import devtools-py modules
from devtools_py import (
    config_utils, validation_utils, security_utils, 
    string_utils, json_utils, time_utils, data_utils,
    file_utils, system_utils
)


class UserManager:
    """Example user management system using devtools-py utilities."""
    
    def __init__(self, config_path: str):
        """Initialize with configuration."""
        self.config = config_utils.ConfigManager([config_path])
        self.config.load()
        
        # Setup validation rules
        self.validator = validation_utils.Validator()
        self.validator.add_rule("email", 
                              lambda x: string_utils.validate_email(x), 
                              "Invalid email format")
        self.validator.add_rule("username", 
                              lambda x: validation_utils.validate_length(x, 3, 20), 
                              "Username must be 3-20 characters")
        self.validator.add_rule("age", 
                              lambda x: validation_utils.validate_range(x, 13, 120), 
                              "Age must be between 13 and 120")
        
        # Initialize storage
        self.users = []
        self.sessions = {}
    
    def create_user(self, user_data: dict) -> dict:
        """Create a new user with validation and security."""
        # Validate input data
        errors = self.validator.validate(user_data)
        if errors:
            return {"success": False, "errors": errors}
        
        # Generate secure user ID and hash password
        user_id = security_utils.generate_uuid()
        password_hash = security_utils.hash_password(user_data["password"])
        
        # Create user record
        user = {
            "id": user_id,
            "username": security_utils.sanitize_input(user_data["username"]),
            "email": user_data["email"].lower(),
            "age": user_data["age"],
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "profile": {
                "display_name": string_utils.to_pascal_case(user_data["username"]),
                "last_login": None,
                "login_count": 0
            }
        }
        
        self.users.append(user)
        return {"success": True, "user_id": user_id}
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user and create session."""
        # Find user
        user = next((u for u in self.users if u["username"] == username), None)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Verify password
        if not security_utils.verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Invalid password"}
        
        # Create JWT session token
        jwt_secret = self.config.get("jwt_secret", default="default-secret")
        session_payload = {
            "user_id": user["id"],
            "username": user["username"],
            "login_time": datetime.now().isoformat()
        }
        
        token = security_utils.generate_jwt_token(
            session_payload, 
            jwt_secret, 
            expires_in=3600  # 1 hour
        )
        
        # Update user login info
        user["profile"]["last_login"] = datetime.now().isoformat()
        user["profile"]["login_count"] += 1
        
        # Store session
        session_id = security_utils.generate_secret_key(16)
        self.sessions[session_id] = {
            "user_id": user["id"],
            "token": token,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True, 
            "session_id": session_id,
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "display_name": user["profile"]["display_name"]
            }
        }
    
    def get_user_stats(self) -> dict:
        """Get user statistics using data utilities."""
        if not self.users:
            return {"total_users": 0}
        
        # Group users by age ranges
        age_groups = data_utils.group_by(
            self.users, 
            lambda u: "teen" if u["age"] < 20 else "adult" if u["age"] < 60 else "senior"
        )
        
        # Calculate statistics
        ages = [u["age"] for u in self.users]
        login_counts = [u["profile"]["login_count"] for u in self.users]
        
        stats = {
            "total_users": len(self.users),
            "age_groups": {k: len(v) for k, v in age_groups.items()},
            "average_age": sum(ages) / len(ages),
            "total_logins": sum(login_counts),
            "active_sessions": len(self.sessions)
        }
        
        return stats
    
    async def export_users(self, export_path: Path) -> bool:
        """Export users to JSON file asynchronously."""
        try:
            # Prepare export data (without password hashes)
            export_data = []
            for user in self.users:
                user_export = data_utils.filter_dict(
                    user, 
                    lambda k, v: k != "password_hash"
                )
                export_data.append(user_export)
            
            # Add metadata
            export_with_meta = {
                "exported_at": datetime.now().isoformat(),
                "total_users": len(export_data),
                "system_info": {
                    "hostname": system_utils.get_system_info()["hostname"],
                    "python_version": system_utils.get_python_info()["version"]
                },
                "users": export_data
            }
            
            # Save using atomic write
            json_utils.save_json(export_with_meta, export_path)
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        jwt_secret = self.config.get("jwt_secret", default="default-secret")
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            # Verify JWT token
            decoded = security_utils.verify_jwt_token(session["token"], jwt_secret)
            if not decoded:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)


async def demo_user_management_system():
    """Demonstrate the user management system."""
    print("👥 USER MANAGEMENT SYSTEM DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create configuration file
        config_file = tmp_path / "config.json"
        config_data = {
            "jwt_secret": security_utils.generate_secret_key(32),
            "session_timeout": 3600,
            "max_login_attempts": 3,
            "password_min_length": 8
        }
        json_utils.save_json(config_data, config_file)
        
        # Initialize user manager
        user_manager = UserManager(str(config_file))
        
        # Create test users
        test_users = [
            {
                "username": "alice_smith", 
                "email": "alice@example.com", 
                "password": "SecurePass123!", 
                "age": 28
            },
            {
                "username": "bob_jones", 
                "email": "bob@example.com", 
                "password": "MyPassword456!", 
                "age": 35
            },
            {
                "username": "charlie_brown", 
                "email": "charlie@example.com", 
                "password": "StrongPass789!", 
                "age": 19
            }
        ]
        
        print("Creating users...")
        created_users = []
        for user_data in test_users:
            result = user_manager.create_user(user_data)
            if result["success"]:
                created_users.append((user_data["username"], user_data["password"]))
                print(f"✅ Created user: {user_data['username']}")
            else:
                print(f"❌ Failed to create user: {result['errors']}")
        
        print(f"\nCreated {len(created_users)} users successfully")
        
        # Test authentication
        print("\nTesting authentication...")
        sessions = []
        for username, password in created_users:
            auth_result = user_manager.authenticate_user(username, password)
            if auth_result["success"]:
                sessions.append(auth_result["session_id"])
                print(f"✅ Authenticated: {username}")
            else:
                print(f"❌ Authentication failed: {auth_result['error']}")
        
        # Get user statistics
        print("\nUser Statistics:")
        stats = user_manager.get_user_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Export users
        export_file = tmp_path / "users_export.json"
        print(f"\nExporting users to {export_file.name}...")
        export_success = await user_manager.export_users(export_file)
        
        if export_success:
            print("✅ Export successful")
            # Verify export file
            exported_data = json_utils.load_json(export_file)
            print(f"  Exported {exported_data['total_users']} users")
            print(f"  Export timestamp: {exported_data['exported_at']}")
        else:
            print("❌ Export failed")
        
        # Clean up sessions
        print("\nCleaning up sessions...")
        # Simulate some time passing (in real scenario, sessions might expire)
        expired_count = user_manager.cleanup_expired_sessions()
        print(f"Cleaned up {expired_count} expired sessions")
        
        print(f"Active sessions remaining: {len(user_manager.sessions)}")
    
    print("\n✅ User management system demo completed!")


async def demo_configuration_management():
    """Demonstrate advanced configuration management."""
    print("\n⚙️ CONFIGURATION MANAGEMENT DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create multiple config files
        base_config = tmp_path / "base.json"
        env_config = tmp_path / "production.json"
        secrets_file = tmp_path / ".env"
        
        # Base configuration
        base_data = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_db"
            },
            "cache": {
                "type": "redis",
                "ttl": 3600
            }
        }
        json_utils.save_json(base_data, base_config)
        
        # Environment-specific overrides
        env_data = {
            "app": {
                "debug": True
            },
            "database": {
                "host": "prod-db.example.com",
                "pool_size": 20
            }
        }
        json_utils.save_json(env_data, env_config)
        
        # Secrets in .env file
        secrets_content = """
DATABASE_PASSWORD=super_secret_password
API_KEY=abc123def456
JWT_SECRET=my_jwt_secret_key
REDIS_URL=redis://localhost:6379/0
"""
        secrets_file.write_text(secrets_content.strip())
        
        # Load and merge configurations
        config_manager = config_utils.ConfigManager([
            str(base_config),
            str(env_config)
        ])
        config_manager.load()
        
        # Merge environment variables
        config_manager.merge_env_vars("DATABASE_")
        
        # Access configuration with type safety
        app_name = config_manager.get("app.name", type_hint=str)
        db_port = config_manager.get("database.port", default=5432, type_hint=int)
        debug_mode = config_manager.get("app.debug", default=False, type_hint=bool)
        pool_size = config_manager.get("database.pool_size", default=10, type_hint=int)
        
        print(f"App name: {app_name}")
        print(f"Database port: {db_port}")
        print(f"Debug mode: {debug_mode}")
        print(f"Pool size: {pool_size}")
        
        # Load secrets separately
        secrets = config_utils.load_dotenv(secrets_file)
        print(f"Loaded {len(secrets)} secrets")
        
        print("✅ Configuration management demo completed!")


async def main():
    """Run all real-world examples."""
    print("🌟 DEVKITX REAL-WORLD EXAMPLES")
    print("=" * 60)
    print("Demonstrating practical usage scenarios")
    print("=" * 60)
    
    await demo_user_management_system()
    await demo_configuration_management()
    
    print("\n" + "=" * 60)
    print("🎉 ALL REAL-WORLD EXAMPLES COMPLETED!")
    print("These examples show how DevKitX can simplify common development tasks:")
    print("• User authentication and session management")
    print("• Data validation and security")
    print("• Configuration management")
    print("• File operations and data export")
    print("• System integration")


if __name__ == "__main__":
    asyncio.run(main())