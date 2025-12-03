from django.apps import AppConfig
import os


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        import main.signals

        # Auto-start sync service on server startup (only in main process)
        # Skip during migrations or when running management commands
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            # Use threading to defer sync service start until Django is fully loaded
            import threading
            threading.Thread(target=self._start_sync_service_on_startup, daemon=True).start()

    def _start_sync_service_on_startup(self):
        """Start the scheduled sync service automatically if auto_sync is enabled."""
        import time

        # Wait for Django to fully initialize
        time.sleep(3)

        try:
            from .models import SystemSettings
            from .services.scheduled_sync_service import start_scheduled_sync_service

            # Check if auto_sync is enabled
            settings = SystemSettings.objects.first()
            if settings and settings.auto_sync_enabled:
                print("\n" + "="*80)
                print("AUTO-START: Auto Sync is enabled in settings")
                print("   Starting Scheduled Sync Service automatically...")
                print("="*80)

                # Start the sync service
                success, message = start_scheduled_sync_service()

                if success:
                    print(f"[OK] {message}")
                    print("   The service will automatically sync:")
                    print("   - Google Sheets (client data)")
                    print("   - SQL Server (inspection data)")
                    print(f"   Sync interval: {settings.sync_interval_hours} hours")
                else:
                    print(f"[WARNING] {message}")

                print("="*80 + "\n")
            else:
                print("\nAuto Sync is disabled - Scheduled Sync Service will not start automatically")

        except Exception as e:
            # Don't crash the app if sync service fails to start
            print(f"\n[WARNING] Could not auto-start sync service: {e}")
            print("   You can manually start it from the Settings page.\n")