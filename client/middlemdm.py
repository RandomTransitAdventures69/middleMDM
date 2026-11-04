#!/usr/bin/env python3
"""Main entry point for middleMDM client."""
import sys
from middlemdm import agent

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        # Run as Windows service
        from middlemdm.service import windows_service
        import win32serviceutil
        win32serviceutil.HandleCommandLine(windows_service.MiddleMDMService)
    else:
        # Run as console application
        a = agent.Agent()
        a.run()

if __name__ == '__main__':
    main()
