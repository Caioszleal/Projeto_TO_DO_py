from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route('/')
def index():
    filtro = request.args.get("filtro", "todas")
    busca = request.args.get("busca", "").lower()


    db = get_db()
    tasks = db.execute("SELECT * FROM tasks").fetchall()

    today = date.today()
    tasks_filtradas = []

    for task in tasks:
        deadline = task[3]
        done = task[2]
        title = task[1].lower()

        if busca and busca not in title:
            continue

        overdue = False

        if deadline:
            task_date = date.fromisoformat(deadline)
            if task_date < today and done == 0:
                overdue = True

        #lógica de filtro
        if filtro == "pendentes" and done:
            continue
        elif filtro == "concluídas" and not done:
            continue
        elif filtro == "atrasadas" and not overdue:
            continue


        tasks_filtradas.append({
            "id": task[0],
            "title": task[1],
            "done": done,
            "deadline": deadline,
            "overdue": overdue,
        })

    total = len(tasks_filtradas)

    pendentes = len([task for task in tasks_filtradas if not task["done"]])

    concluidas = len([task for task in tasks_filtradas if task["done"]])

    atrasadas = len([task for task in tasks_filtradas if task["overdue"]])

    return render_template(
        "index.html",
        tasks=tasks_filtradas,
        filtro=filtro,
        busca=busca,
        total=total,
        pendentes=pendentes,
        concluidas=concluidas,
        atrasadas=atrasadas
    )

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

@app.route("/edit/<int:id>")
def edit(id):
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()

    return render_template("edit.html", task=task)

@app.route("/done/<int:id>")
def done(id):
    db = get_db()
    db.execute("UPDATE tasks SET done = 1 WHERE id = ?", (id,))
    db.commit()

    return redirect("/")


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    title = request.form["task"]
    deadline = request.form["deadline"]

    db = get_db()
    db.execute(
        "UPDATE tasks SET title = ?, deadline = ? WHERE id = ?",
        (title, deadline, id)
    )
    db.commit()

    return redirect("/")

app.run(debug=True)
