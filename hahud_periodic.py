import time, threading, os


def hahudRun():
    print("Update: " + time.ctime())
    os.system("hahud.py")
    threading.Timer((60 * 15), hahudRun).start()  # 15 min


# Run
hahudRun()
