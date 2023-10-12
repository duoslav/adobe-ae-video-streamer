from flask import Flask, Response
import socket
import cv2
import numpy as np

app = Flask(__name__)

# UDP parameters
UDP_IP = "127.0.0.1"  # Update this with the sender's IP address
UDP_PORT = 22345  # Update this with the sender's UDP port

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    udp_socket.bind((UDP_IP, UDP_PORT))
except Exception as error:
    print(error)
    udp_socket.shutdown(1)
    udp_socket.close()
    exit(1)

def receive_frames():
    while True:
        try:
          data, _ = udp_socket.recvfrom(54* 96* 4)
          print(len(data))
          image = np.frombuffer(data, dtype=np.uint8).reshape(54, 96, 4)

          # Encode the gray square as a JPEG image
          _, frame_bytes = cv2.imencode('.jpg', image)

          yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes.tobytes() + b'\r\n')
        except KeyboardInterrupt:
            if udp_socket:
              udp_socket.close()
              exit(2)


        # byte_value = 127  # Decimal 94
        # byte_array = bytes([byte_value] * 1024)
        # yield (b'--frame\r\n'
        #         b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', byte_array)[1].tobytes() + b'\r\n')
        # # Ensure the frame is not empty
        # if frame is not None:
        #     yield (b'--frame\r\n'
        #            b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', byte_array)[1].tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(receive_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Video Stream</title>
        </head>
        <body>
            <img src="/video_feed" />
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
