# -*- coding: utf-8 -*-
# @Author: Ultraxime
# @Date:   2023-03-15 14:38:54
# @Last Modified by:   Ultraxime
# @Last Modified time: 2023-03-17 15:10:42

"""Main execution script"""

import sys
from src.manager import Manager
from src.worker import Worker

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "healthcheck":
        sys.exit(0)

    if len(sys.argv) == 3 and sys.argv[1] == "start":
        match sys.argv[2]:
            case "manager":
                manager = Manager()
                manager.start()
            case "worker":
                worker = Worker()
                worker.start()
            case typ:
                print("Unknown type: " + typ)
                sys.exit(1)
    else:
        sys.exit(1)
else:
    sys.exit(1)
