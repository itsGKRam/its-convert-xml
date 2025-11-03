#!/usr/bin/env python3
"""
Development server with automatic reload on file changes using watchdog.

This script monitors Python files and configuration files for changes,
and automatically restarts the Flask development server.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FlaskRestartHandler(FileSystemEventHandler):
    """Handler for file system events that triggers Flask server restart."""
    
    def __init__(self, server_process=None):
        super().__init__()
        self.server_process = server_process
        self.last_restart = 0
        self.restart_delay = 2  # Delay in seconds to avoid multiple rapid restarts
        
    def should_ignore_file(self, file_path):
        """Check if file should be ignored."""
        ignore_patterns = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.pyd',
            '.git',
            'htmlcov',
            '.pytest_cache',
            'Icon',
            '.DS_Store',
        ]
        file_str = str(file_path).lower()
        return any(pattern in file_str for pattern in ignore_patterns)
    
    def should_restart(self, file_path):
        """Determine if restart is needed based on file type."""
        file_path = Path(file_path)
        
        # Ignore certain files
        if self.should_ignore_file(file_path):
            return False
        
        # Watch Python files
        if file_path.suffix in ['.py', '.yaml', '.yml', '.txt', '.cfg', '.ini']:
            return True
        
        return False
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if self.should_restart(event.src_path):
            current_time = time.time()
            # Throttle restarts to avoid rapid-fire restarts
            if current_time - self.last_restart < self.restart_delay:
                return
            
            self.last_restart = current_time
            print(f"\n🔄 File changed: {event.src_path}")
            print("⏳ Restarting server...\n")
            self.restart_server()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        if self.should_restart(event.src_path):
            print(f"\n🔄 New file created: {event.src_path}")
            print("⏳ Restarting server...\n")
            self.restart_server()
    
    def set_server_process(self, process):
        """Set the server process to restart."""
        self.server_process = process
    
    def restart_server(self):
        """Restart the Flask server."""
        if self.server_process:
            try:
                # Terminate the current server process
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")


def start_flask_server(port=5000):
    """Start the Flask development server."""
    env = os.environ.copy()
    env['FLASK_APP'] = 'app'
    env['FLASK_ENV'] = 'development'
    
    cmd = ['flask', 'run', '--port', str(port), '--reload']
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=None,  # Let Flask output go directly to terminal
            stderr=None,
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        sys.exit(1)


def monitor_server(process, observer):
    """Monitor server process and handle shutdown."""
    try:
        # Wait for process to complete (or be interrupted)
        process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        print("\n\n🛑 Stopping server...")
        observer.stop()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def main():
    """Main entry point for the development server."""
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Clear port if in use
    try:
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔄 Clearing port {port}...")
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    try:
                        subprocess.run(['kill', '-9', pid.strip()], 
                                     capture_output=True, timeout=1)
                    except:
                        pass
            time.sleep(1)
    except:
        pass
    
    print("🚀 Starting Flask development server with auto-reload...")
    print(f"📡 Server will run on port {port}")
    print("👀 Watching for file changes...\n")
    
    # Start Flask server
    server_process = start_flask_server(port)
    
    # Give server a moment to start and check if it failed
    time.sleep(2)
    if server_process.poll() is not None:
        print(f"❌ Server failed to start (exit code: {server_process.returncode})")
        print("💡 Check if port is available or if there are any errors above")
        sys.exit(1)
    
    # Setup file watcher
    event_handler = FlaskRestartHandler(server_process)
    observer = Observer()
    
    # Watch the project directory
    watch_paths = [
        Path('app'),
        Path('tests'),
        Path('gunicorn_config.py'),
        Path('pytest.ini'),
        Path('requirements.txt'),
        Path('requirements-dev.txt'),
    ]
    
    for watch_path in watch_paths:
        if watch_path.exists():
            observer.schedule(event_handler, str(watch_path), recursive=True)
            print(f"👁️  Watching: {watch_path}")
    
    observer.start()
    
    # Wait a bit for server to start
    time.sleep(1)
    
    try:
        # Monitor server process
        monitor_server(server_process, observer)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        observer.stop()
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
    
    observer.join()
    print("✅ Server stopped.")


if __name__ == '__main__':
    main()
