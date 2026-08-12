from database.db_connection import get_connection
from utils.helpers import process_scheme
from utils.hash_utils import generate_hash


def _rows_to_dicts(cursor, rows):
    """Convert normal rows into list of dictionaries"""
    if not rows:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def insert_scheme(scheme: dict, content_hash: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO schemes (
        title, details, eligibility, benefits, exclusion,
        documents_required, application_process, category,
        state, department, status, start_date, end_date,
        launch_date, min_income, max_income, gender,
        min_age, max_age, target_group, last_date_to_apply,
        application_link, content_hash
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    values = (
        scheme.get("title"),
        scheme.get("details"),
        scheme.get("eligibility"),
        scheme.get("benefits"),
        scheme.get("exclusion"),
        scheme.get("documents_required"),
        scheme.get("application_process"),
        scheme.get("category"),
        scheme.get("state"),
        scheme.get("department"),
        scheme.get("status"),
        scheme.get("start_date"),
        scheme.get("end_date"),
        scheme.get("launch_date"),
        scheme.get("min_income"),
        scheme.get("max_income"),
        scheme.get("gender"),
        scheme.get("min_age"),
        scheme.get("max_age"),
        scheme.get("target_group"),
        scheme.get("last_date_to_apply"),
        scheme.get("application_link"),
        content_hash
    )

    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()


def update_scheme(scheme: dict, content_hash: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE schemes SET
        title=%s, details=%s, eligibility=%s, benefits=%s,
        exclusion=%s, documents_required=%s, application_process=%s,
        category=%s, state=%s, department=%s, status=%s,
        start_date=%s, end_date=%s, launch_date=%s,
        min_income=%s, max_income=%s, gender=%s,
        min_age=%s, max_age=%s, target_group=%s,
        last_date_to_apply=%s, content_hash=%s
    WHERE application_link=%s
    """

    values = (
        scheme.get("title"),
        scheme.get("details"),
        scheme.get("eligibility"),
        scheme.get("benefits"),
        scheme.get("exclusion"),
        scheme.get("documents_required"),
        scheme.get("application_process"),
        scheme.get("category"),
        scheme.get("state"),
        scheme.get("department"),
        scheme.get("status"),
        scheme.get("start_date"),
        scheme.get("end_date"),
        scheme.get("launch_date"),
        scheme.get("min_income"),
        scheme.get("max_income"),
        scheme.get("gender"),
        scheme.get("min_age"),
        scheme.get("max_age"),
        scheme.get("target_group"),
        scheme.get("last_date_to_apply"),
        content_hash,
        scheme.get("application_link")
    )

    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()


def get_scheme_by_link(application_link: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM schemes WHERE application_link = %s"
    cursor.execute(query, (application_link,))
    row = cursor.fetchone()

    result = None
    if row:
        columns = [col[0] for col in cursor.description]
        result = dict(zip(columns, row))

    cursor.close()
    conn.close()
    return result


def save_scheme(scheme: dict) -> str:
    """
    Returns: "inserted" | "updated" | "skipped"
    """
    scheme = process_scheme(scheme)
    link = scheme.get("application_link")

    if not link:
        print("No application_link – cannot save")
        return "skipped"

    existing = get_scheme_by_link(link)
    new_hash = generate_hash(scheme)

    if not existing:
        insert_scheme(scheme, new_hash)
        return "inserted"

    old_hash = existing.get("content_hash")
    if old_hash != new_hash:
        update_scheme(scheme, new_hash)
        return "updated"

    return "skipped"


def get_all_schemes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schemes ORDER BY scheme_id")
    
    rows = cursor.fetchall()
    
    results = []
    
    if not rows:
        cursor.close()
        conn.close()
        return results

    # Case 1: rows are already dictionaries
    if isinstance(rows[0], dict):
        results = rows
    else:
        # Case 2: rows are tuples/lists
        columns = [col[0] for col in cursor.description]
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(columns):
                row_dict[col_name] = row[i]
            results.append(row_dict)
    
    cursor.close()
    conn.close()
    return results