#!/usr/bin/env python

import getopt
import sys
import socket
import commands

def usage(cmd, full=False):
    if not full:
        print("Options")
        print("-h\tDisplay this help")
        print("-m\tList supported methods")
    else:
        print("Commands")
    verbs = cmd.keys()
    for entry in verbs if full else []:
        print(entry)
        for line in cmd[entry][1]:
            print('\t' + line)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def getAllVmsUUID():
    hostIp = get_host_ip()
    vmUUIDs = commands.getoutput('vdsClient -s ' + hostIp + ' list ids')
    idList = vmUUIDs.split('\n')
    for vmId in idList:
        yield vmId

def shutdownVms():
    hostIp = get_host_ip()
    ids = getAllVmsUUID()
    for vm_id in ids:
        commands.getstatusoutput('vdsClient -s ' + hostIp +
                                 ' shutdown ' + vm_id +
                                 ' 30 System-shutdown false 60 false')


if __name__ == "__main__":
    cmds = {
        'reboot': (rebootVms, ('reboot all vms in the host',)),
        'shutdown': (shutdownVms, ('shutdown all vms in the host',)),
    }

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hmso",
                                   ["help", "methods", "SSL",
                                    "truststore=", "oneliner"])
        for o, v in opts:
            if o == "-h" or o == "--help":
                usage(cmds)
                sys.exit(0)
            if o == '-m' or o == '--methods':
                usage(cmds, True)
                sys.exit(0)

        if len(args) < 1:
            raise Exception("Need at least two arguments!")
    except Exception as e:
        print("ERROR - %s" % (e))
        sys.exit(-1)

    commandArgs = args[0]
    if commandArgs not in cmds:
        print("Not supported command! Please use '-m' " \
              "to list the supported methods!")
        sys.exit(-1)

    cmds[commandArgs][0]()
    #rebootVms()
    #shutdownVms()
