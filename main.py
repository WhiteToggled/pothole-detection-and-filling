from capture import capture
import time

if __name__ == "__main__":
    while True:
        filename = capture.captureImage()
        time.sleep(5)
