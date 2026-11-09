#!/usr/bin/env python3
"""Main entry point for middleMDM client."""
import sys
import argparse
import importlib
import signal
from middlemdm import __version__, agent

def main():
    parser = argparse.ArgumentParser(description="middleMDM device management client")
    parser.add_argument(
        "--version",
        action="version",
        version=f"middleMDM client {__version__}",
    )
    parser.add_argument(
        "--service",
        action="store_true",
        help="Install or control the Windows service",
    )
    args, service_args = parser.parse_known_args()

    if args.service:
        if sys.platform != "win32":
            parser.error("--service is supported only on Windows; use systemd or launchd")
        windows_service = importlib.import_module("middlemdm.service.windows_service")
        import win32serviceutil
        sys.argv = [sys.argv[0], *service_args]
        win32serviceutil.HandleCommandLine(windows_service.MiddleMDMService)
    else:
        a = agent.Agent()
        for signal_name in ("SIGINT", "SIGTERM"):
            signal_number = getattr(signal, signal_name, None)
            if signal_number is not None:
                signal.signal(signal_number, lambda signum, frame: a.stop())
        a.run()

if __name__ == '__main__':
    main()
