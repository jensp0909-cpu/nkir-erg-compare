from flask import Blueprint, jsonify, render_template, request

from common.time_parse import format_seconds, parse_time
from webapp import queries

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    conn = queries.get_connection()
    try:
        fields = queries.list_fields(conn)
    finally:
        conn.close()
    return render_template("index.html", fields=fields)


@bp.route("/fields")
def fields_json():
    conn = queries.get_connection()
    try:
        fields = queries.list_fields(conn)
    finally:
        conn.close()
    return jsonify(fields)


@bp.route("/compare", methods=["POST"])
def compare():
    field_key = request.form.get("field_key", "")
    time_input = request.form.get("time_input", "")

    conn = queries.get_connection()
    try:
        fields = queries.list_fields(conn)
        field = queries.get_field(conn, field_key)

        def error_page(message):
            return (
                render_template(
                    "index.html",
                    fields=fields,
                    error=message,
                    time_input=time_input,
                    selected_field=field_key,
                ),
                400,
            )

        if field is None:
            return error_page("Kies een geldige categorie.")

        try:
            user_seconds = parse_time(time_input)
        except ValueError:
            return error_page(f"Kon de tijd '{time_input}' niet lezen. Gebruik een formaat zoals 6:02.0.")

        if user_seconds is None:
            return error_page("Vul je 2000m ergtijd in.")

        comparison = queries.compute_comparison(conn, field_key, user_seconds)
        if comparison is None:
            return error_page(f"Nog geen historische data beschikbaar voor {field['display_name']}.")

        return render_template(
            "result.html",
            field=field,
            user_seconds=user_seconds,
            user_time_display=format_seconds(user_seconds),
            comparison=comparison,
            format_seconds=format_seconds,
        )
    finally:
        conn.close()
