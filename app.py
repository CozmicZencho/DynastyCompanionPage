import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DYNASTY_FILE = "dynasties.json"

# -------------------------------
# Utility functions
# -------------------------------
def load_dynasties():
    if os.path.exists(DYNASTY_FILE):
        with open(DYNASTY_FILE, "r") as f:
            return json.load(f)
    return []

def save_dynasties(dynasties):
    with open(DYNASTY_FILE, "w") as f:
        json.dump(dynasties, f, indent=4)

# -------------------------------
# Landing / Menu
# -------------------------------
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/home")
def home():
    return render_template("dynasty_menu.html")

# -------------------------------
# Select Dynasty
# -------------------------------
@app.route("/select")
def select_dynasty_page():
    dynasties = load_dynasties()
    return render_template("select_dynasty.html", dynasties=dynasties)

@app.route("/dynasty/<int:dynasty_id>")
def dynasty_page(dynasty_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "<h1>Dynasty not found</h1>", 404

    # Ensure seasons have IDs
    if "seasons" in dynasty["coach"]:
        next_id = 1
        for s in dynasty["coach"]["seasons"]:
            if "id" not in s:
                s["id"] = next_id
                next_id += 1
        save_dynasties(dynasties)

    return render_template("dynasty_page.html", dynasty=dynasty)

# -------------------------------
# Create Dynasty
# -------------------------------
@app.route("/create", methods=["GET", "POST"])
def create_dynasty():
    if request.method == "POST":
        dynasties = load_dynasties()
        new_id = max([d["id"] for d in dynasties], default=0) + 1

        new_dynasty = {
            "id": new_id,
            "name": request.form["name"],
            "description": request.form["description"],
            "coach": {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "college": request.form["college"],
                "alma_mater": request.form.get("alma_mater", ""),
                "year": request.form["year"],
                "seasons": []
            }
        }

        dynasties.append(new_dynasty)
        save_dynasties(dynasties)

        return redirect(url_for("dynasty_page", dynasty_id=new_id))

    return render_template("create_dynasty.html")

# -------------------------------
# Edit / Delete Dynasty
# -------------------------------
@app.route("/edit")
def edit_dynasty_page():
    dynasties = load_dynasties()
    return render_template("edit_dynasty.html", dynasties=dynasties)

@app.route("/edit/<int:dynasty_id>", methods=["GET", "POST"])
def edit_single_dynasty(dynasty_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "<h1>Dynasty not found</h1>", 404

    if request.method == "POST":
        dynasty["name"] = request.form["name"]
        dynasty["description"] = request.form["description"]
        save_dynasties(dynasties)
        return redirect(url_for("edit_dynasty_page"))

    return render_template("edit_single_dynasty.html", dynasty=dynasty)

@app.route("/delete/<int:dynasty_id>", methods=["POST"])
def delete_dynasty(dynasty_id):
    dynasties = load_dynasties()
    dynasties = [d for d in dynasties if d["id"] != dynasty_id]
    save_dynasties(dynasties)
    return redirect(url_for("edit_dynasty_page"))

# -------------------------------
# Edit Coach
# -------------------------------
@app.route("/dynasty/<int:dynasty_id>/coach/edit")
def edit_coach_page(dynasty_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "<h1>Dynasty not found</h1>", 404
    return render_template("edit_coach.html", dynasty=dynasty)

@app.route("/dynasty/<int:dynasty_id>/coach", methods=["POST"])
def update_coach(dynasty_id):
    dynasties = load_dynasties()
    for d in dynasties:
        if d["id"] == dynasty_id:
            d["coach"] = {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "college": request.form["college"],
                "alma_mater": request.form.get("alma_mater", ""),
                "year": request.form["year"],
                "seasons": d["coach"].get("seasons", [])
            }
            break
    save_dynasties(dynasties)
    return redirect(url_for("dynasty_page", dynasty_id=dynasty_id))

# -------------------------------
# Seasons (Add / Edit / Delete)
# -------------------------------
@app.route("/dynasty/<int:dynasty_id>/season/add", methods=["GET", "POST"])
def add_season(dynasty_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "<h1>Dynasty not found</h1>", 404

    if request.method == "POST":
        if "seasons" not in dynasty["coach"]:
            dynasty["coach"]["seasons"] = []

        new_id = max([s["id"] for s in dynasty["coach"]["seasons"]], default=0) + 1

        season = {
            "id": new_id,
            "year": int(request.form["year"]),
            "team": request.form["team"],   # ✅ new field
            "wins": int(request.form["wins"]),
            "losses": int(request.form["losses"]),
            "achievements": []              # ✅ replaces bowl_game + trophies
        }

        dynasty["coach"]["seasons"].append(season)
        save_dynasties(dynasties)
        return redirect(url_for("dynasty_page", dynasty_id=dynasty_id))

    return render_template("add_season.html", dynasty=dynasty)


@app.route("/dynasty/<int:dynasty_id>/season/<int:season_id>/edit", methods=["GET", "POST"])
def edit_season(dynasty_id, season_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty or "seasons" not in dynasty["coach"]:
        return "<h1>Dynasty or seasons not found</h1>", 404

    season = next((s for s in dynasty["coach"]["seasons"] if s["id"] == season_id), None)
    if not season:
        return "<h1>Season not found</h1>", 404

    if request.method == "POST":
        season["year"] = int(request.form["year"])
        season["team"] = request.form["team"]  
        season["wins"] = int(request.form["wins"])
        season["losses"] = int(request.form["losses"])
        if "achievements" not in season:
            season["achievements"] = []
        save_dynasties(dynasties)
        return redirect(url_for("dynasty_page", dynasty_id=dynasty_id))

    return render_template("edit_season.html", dynasty=dynasty, season=season)


@app.route("/dynasty/<int:dynasty_id>/season/<int:season_id>/delete", methods=["POST"])
def delete_season(dynasty_id, season_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty or "seasons" not in dynasty["coach"]:
        return "<h1>Dynasty or seasons not found</h1>", 404

    dynasty["coach"]["seasons"] = [s for s in dynasty["coach"]["seasons"] if s["id"] != season_id]
    save_dynasties(dynasties)
    return redirect(url_for("dynasty_page", dynasty_id=dynasty_id))

# -------------------------------
# View Achievements
# -------------------------------

@app.route("/dynasty/<int:dynasty_id>/season/<int:season_id>/achievements")
def season_achievements(dynasty_id, season_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)

    if not dynasty:
        return "Dynasty not found", 404

    season = next((s for s in dynasty["coach"]["seasons"] if s["id"] == season_id), None)
    if not season:
        return "Season not found", 404

    # 🔄 Temporary compatibility:
    # Convert bowl_game + trophies → unified achievements list
    achievements = []

    if season.get("bowl_game"):
        achievements.append({"type": "Team", "award": season["bowl_game"]})

    if season.get("trophies"):
        for t in season["trophies"]:
            achievements.append({"type": "Team", "award": t})

    # Attach to season for rendering
    season["achievements"] = achievements

    return render_template("season_achievements.html", dynasty=dynasty, season=season)

@app.route("/dynasty/<int:dynasty_id>/season/<int:season_id>/add_award", methods=["GET", "POST"])
def add_award(dynasty_id, season_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "Dynasty not found", 404

    season = next((s for s in dynasty["coach"]["seasons"] if s["id"] == season_id), None)
    if not season:
        return "Season not found", 404

    if request.method == "POST":
        award_type = request.form["type"]
        award_name = request.form["award"]
        player_name = request.form.get("player", "")

        new_award = {"type": award_type, "award": award_name}
        if award_type == "Player" and player_name:
            new_award["player"] = player_name

        season.setdefault("achievements", []).append(new_award)
        save_dynasties(dynasties)

        return redirect(url_for("season_achievements", dynasty_id=dynasty_id, season_id=season_id))

    return render_template("add_award.html", dynasty=dynasty, season=season)


@app.route("/dynasty/<int:dynasty_id>/season/<int:season_id>/edit_awards", methods=["GET", "POST"])
def edit_awards(dynasty_id, season_id):
    dynasties = load_dynasties()
    dynasty = next((d for d in dynasties if d["id"] == dynasty_id), None)
    if not dynasty:
        return "Dynasty not found", 404

    season = next((s for s in dynasty["coach"]["seasons"] if s["id"] == season_id), None)
    if not season:
        return "Season not found", 404

    if request.method == "POST":
        # Replace achievements with new submitted list
        new_achievements = []
        awards = request.form.getlist("award")
        types = request.form.getlist("type")
        players = request.form.getlist("player")

        for i in range(len(awards)):
            entry = {"type": types[i], "award": awards[i]}
            if types[i] == "Player" and players[i]:
                entry["player"] = players[i]
            new_achievements.append(entry)

        season["achievements"] = new_achievements
        save_dynasties(dynasties)

        return redirect(url_for("season_achievements", dynasty_id=dynasty_id, season_id=season_id))

    return render_template("edit_awards.html", dynasty=dynasty, season=season)


# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
