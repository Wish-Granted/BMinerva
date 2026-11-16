from flask import Blueprint, jsonify, request, current_app, session

from ..utils.decorators import login_required

selection_bp = Blueprint("selection", __name__, url_prefix="/api/selection")

def _username() -> str:
    return session["user"]

@selection_bp.route("", methods=["GET"])
@login_required
def get_selection():
    user = _username()
    repo = current_app.selection_repository
    student_repo = current_app.student_repository

    students, called = [], []
    for item in repo.get_selection(user):
        student = student_repo.get_by_id(item["student_id"])
        if not student:          # student no longer in the directory
            continue
        students.append(student)
        if item["called"]:
            called.append(student["id"])

    return jsonify({"students": students, "called": called, "sort": repo.get_sort(user)})

@selection_bp.route("", methods=["PUT"])
@login_required
def save_selection():
    data = request.get_json(silent=True) or {}
    student_ids = data.get("student_ids")
    called = data.get("called", [])
    sort = data.get("sort")

    if not isinstance(student_ids, list) or not all(isinstance(s, str) for s in student_ids):
        return jsonify({"error": "student_ids must be a list of strings"}), 400
    if not isinstance(called, list) or not all(isinstance(s, str) for s in called):
        return jsonify({"error": "called must be a list of strings"}), 400

    if sort is not None:
        if (not isinstance(sort, dict) or not isinstance(sort.get("key"), str)
                or sort.get("dir") not in (1, -1)):
            return jsonify({"error": "invalid sort"}), 400
        sort = {"key": sort["key"], "dir": sort["dir"]}

    # only keep real students, de-duplicated, preserving order
    student_repo = current_app.student_repository
    valid, seen = [], set()
    for sid in student_ids:
        student = student_repo.get_by_id(sid) if sid else None
        if student and student["id"] not in seen:
            seen.add(student["id"])
            valid.append(student["id"])

    current_app.selection_repository.replace_selection(
        _username(), valid, set(called) & seen, sort
    )
    return jsonify({"saved": len(valid)})
