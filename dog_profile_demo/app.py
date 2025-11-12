from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_db, close_db

app = Flask(__name__)
app.secret_key = "dev-secret"  # for flash()

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route("/")
def index():
    db = get_db()
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    size = request.args.get("size", "").strip()

    sql = "SELECT * FROM dogs WHERE 1=1"
    params = []
    if q:
        sql += " AND (name LIKE ? OR notes LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if status:
        sql += " AND status = ?"
        params.append(status)
    if size:
        sql += " AND size = ?"
        params.append(size)
    sql += " ORDER BY name"
    dogs = db.execute(sql, params).fetchall()
    return render_template("index.html", dogs=dogs)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        db = get_db()
        form = request.form
        db.execute(
            "INSERT INTO dogs (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes) VALUES (?,?,?,?,?,?,?,?)",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
            ),
        )
        db.commit()
        flash("Dog created.")
        return redirect(url_for("index"))
    return render_template("form.html", dog=None)

@app.route("/edit/<int:dog_id>", methods=["GET", "POST"])
def edit(dog_id):
    db = get_db()
    dog = db.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,)).fetchone()
    if not dog:
        flash("Dog not found.")
        return redirect(url_for("index"))
    if request.method == "POST":
        form = request.form
        db.execute(
            "UPDATE dogs SET name=?, age=?, size=?, status=?, kid_friendly=?, cat_friendly=?, dog_friendly=?, notes=? WHERE id=?",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
                dog_id,
            ),
        )
        db.commit()
        flash("Dog updated.")
        return redirect(url_for("index"))
    # Convert Row to simple object with attrs for template convenience
    class Obj: pass
    o = Obj()
    for k in dog.keys():
        setattr(o, k, dog[k])
    return render_template("form.html", dog=o)

@app.route("/delete/<int:dog_id>")
def delete(dog_id):
    db = get_db()
    db.execute("DELETE FROM dogs WHERE id=?", (dog_id,))
    db.commit()
    flash("Dog deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

