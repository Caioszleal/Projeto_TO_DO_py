from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route('/')
def index():
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks").fetchall()

    today = date.today()

    tasks_with_status = []

    for task in tasks:
        deadline = task[3]

        overdue = False

        if deadline:
            task_date = date.fromisoformat(deadline)
            if task_date < today and task[2] == 0:
                overdue = True

        tasks_with_status.append({
            "id": task[0],
            "title": task[1],
            "done": task[2],
            "deadline": deadline,
            "overdue": overdue,
        })
    return render_template("index.html", tasks=tasks_with_status)

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    deadline = request.form["deadline"]

    db = get_db()
    db.execute(
        "INSERT INTO tasks (title, done, deadline) VALUES (?, ?, ?)",
        (task, 0, deadline)
    )
    db.commit()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (id,))
    db.commit()

    return redirect("/")

@app.route("/done/<int:id>")
def done(id):
    db = get_db()
    db.execute("UPDATE tasks SET done = 1 WHERE id = ?", (id,))
    db.commit()

    return redirect("/")

app.run(debug=True)
