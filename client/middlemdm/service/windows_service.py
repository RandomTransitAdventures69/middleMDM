"""Windows service wrapper for middleMDM client."""
import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
from .. import agent


class MiddleMDMService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MiddleMDM"
    _svc_display_name_ = "middleMDM Agent"
    _svc_description_ = "middleMDM Device Management Client"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.agent = agent.Agent()
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.agent.stop()
    
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()
    
    def main(self):
        try:
            self.agent.run()
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MiddleMDMService)
