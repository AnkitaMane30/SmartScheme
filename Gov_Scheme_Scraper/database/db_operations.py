from database.db_connection import get_connection
from utils.helpers import process_scheme


def insert_scheme(scheme, content_hash):
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
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    conn.close()

    print("Inserted:", scheme.get("title"))


def get_scheme_by_link(application_link):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM schemes WHERE application_link = %s"
    cursor.execute(query, (application_link,))
    result = cursor.fetchone()

    conn.close()
    return result

def update_scheme(scheme, content_hash):
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
    conn.close()

    print("Updated:", scheme.get("title"))


from utils.hash_utils import generate_hash


def save_scheme(scheme):
    # Normalize and prepare scheme
    scheme = process_scheme(scheme)
    link = scheme.get("application_link")

    existing = get_scheme_by_link(link)
    new_hash = generate_hash(scheme)

    if not existing:
        insert_scheme(scheme, new_hash)

    elif existing.get("content_hash") != new_hash:
        update_scheme(scheme, new_hash)

    else:
        print("No change, skipped:", scheme.get("title"))

#fetch data from database
def get_all_schemes():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM schemes"
    cursor.execute(query)

    results = cursor.fetchall()
    conn.close()

    return results