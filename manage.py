import project, os

if __name__ == '__main__':
    project.socketio.run(project.project, host="127.0.0.1", port=int(os.environ.get("PORT")), debug=True)