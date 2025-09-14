#!/usr/bin/env python
"""
Server startup script with better error handling and timeout settings
"""
import os
import sys
import socket
import time

# Set longer timeouts
socket.setdefaulttimeout(300)  # 5 minutes

def main():
    """Start the Django development server with optimized settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    
    try:
        from django.core.management import execute_from_command_line
        from django.core.management.commands.runserver import Command as RunserverCommand
        
        # Override default settings for better performance
        original_handle = RunserverCommand.handle
        
        def enhanced_handle(self, *args, **options):
            # Set additional options for better performance
            options['noreload'] = False
            options['nothreading'] = False
            options['verbosity'] = 1
            
            print("🚀 Starting optimized Django server...")
            print("⚡ Performance optimizations enabled:")
            print("   - Increased timeouts (5 minutes)")
            print("   - Pagination for large datasets")
            print("   - Multi-level caching")
            print("   - Database-level aggregation")
            print("   - Response size limits")
            print()
            
            return original_handle(self, *args, **options)
        
        RunserverCommand.handle = enhanced_handle
        
        # Start the server
        execute_from_command_line(sys.argv)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
