import subprocess
import json
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

results_data = {}

@app.route("/start", methods=["POST"])
def start_test():
    process = subprocess.Popen(
        ["locust", "--headless", "--users", "10","--spawn-rate","1", "-H", "https://www.ip-label.fr/"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout_output, stderr_output = process.communicate()

    if stdout_output:
        lines = stdout_output.strip().split('\n')
        results_data[url] = lines
        return jsonify({"results": lines})
    else:
        error_message = "No results found"
        print(error_message)
        print("stderr output:", stderr_output)
        return jsonify({"error": error_message})

if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={"port": 8080}).start()