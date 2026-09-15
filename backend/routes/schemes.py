from flask import Blueprint, request
import utils.db_connection as db
from utils.utils import createResult

schemesRouter = Blueprint(
    "schemes",
    __name__,
    url_prefix="/schemes"
)

# =========================================
# GET ALL SCHEMES
# =========================================

@schemesRouter.route("/", methods=["GET"])
def getAllSchemes():

    sql = """
        SELECT
            scheme_id,
            title,
            details,
            category,
            state,
            department,
            application_link
        FROM schemes
    """

    result = db.executeQuery(sql, ())

    return createResult(None, result)


# =========================================
# GET SINGLE SCHEME
# =========================================

@schemesRouter.route("/<int:scheme_id>", methods=["GET"])
def getSingleScheme(scheme_id):

    sql = """
        SELECT *
        FROM schemes
        WHERE scheme_id = %s
    """

    result = db.executeQuery(sql, (scheme_id,))

    if not result:
        return createResult("Scheme not found")

    return createResult(None, result[0])


# =========================================
# SEARCH SCHEMES
# =========================================

@schemesRouter.route("/search", methods=["GET"])
def searchSchemes():

    query = request.args.get("query")

    if not query:
        return createResult("Search query required")

    sql = """
        SELECT
            scheme_id,
            title,
            details,
            category,
            state
        FROM schemes
        WHERE
            title LIKE %s
            OR details LIKE %s
            OR category LIKE %s
    """

    searchTerm = f"%{query}%"

    result = db.executeQuery(
        sql,
        (
            searchTerm,
            searchTerm,
            searchTerm
        )
    )

    return createResult(None, result)


# =========================================
# FILTER SCHEMES
# =========================================

@schemesRouter.route("/filter", methods=["GET"])
def filterSchemes():

    category = request.args.get("category")
    state = request.args.get("state")

    sql = """
        SELECT
            scheme_id,
            title,
            details,
            category,
            state
        FROM schemes
        WHERE 1=1
    """

    values = []

    if category:
        sql += " AND category = %s"
        values.append(category)

    if state:
        sql += " AND state = %s"
        values.append(state)

    result = db.executeQuery(sql, tuple(values))

    return createResult(None, result)

    # =========================================
# CATEGORY COUNTS  (for the Popular Categories section on the homepage)
# =========================================

@schemesRouter.route("/categories", methods=["GET"])
def getCategoryStats():
    """
    Returns real category names + how many schemes exist in each,
    e.g. [{"category": "Water & Sanitation", "scheme_count": 14}, ...]
    Ordered by most schemes first, capped at 12 to fit the homepage grid.
    """
    sql = """
        SELECT category, COUNT(*) AS scheme_count
        FROM schemes
        WHERE category IS NOT NULL
          AND TRIM(category) <> ''
          AND LOWER(TRIM(category)) NOT IN ('null', 'n/a', 'na', 'undefined')
        GROUP BY category
        ORDER BY scheme_count DESC
        LIMIT 12
    """
    result = db.executeQuery(sql, ())
    return createResult(None, result)


# =========================================
# OVERALL STATS  (for the Stats section on the homepage)
# =========================================

# @schemesRouter.route("/stats", methods=["GET"])
# def getOverallStats():
#     """
#     Returns real totals derived from the schemes table:
#     total schemes, distinct departments, distinct states.
#     (User/application counts aren't tracked in this table, so the
#     frontend keeps those two static.)
#     """
#     sql = """
#         SELECT
#             COUNT(*) AS total_schemes,
#             COUNT(DISTINCT department) AS total_departments,
#             COUNT(DISTINCT state) AS total_states
#         FROM schemes
#     """
#     result = db.executeQuery(sql, ())
#     stats = result[0] if result else {
#         "total_schemes": 0,
#         "total_departments": 0,
#         "total_states": 0,
#     }
#     return createResult(None, stats)
# Replace your existing getOverallStats() function with this version -
# it just adds COUNT(DISTINCT category) to the same query.

@schemesRouter.route("/stats", methods=["GET"])
def getOverallStats():
    """
    Returns real totals derived from the schemes table:
    total schemes, distinct departments, distinct states, distinct categories.
    (User/application counts aren't tracked in this table, so the
    frontend doesn't display those.)
    """
    sql = """
        SELECT
            COUNT(*) AS total_schemes,
            COUNT(DISTINCT department) AS total_departments,
            COUNT(DISTINCT state) AS total_states,
            COUNT(DISTINCT category) AS total_categories
        FROM schemes
    """
    result = db.executeQuery(sql, ())
    stats = result[0] if result else {
        "total_schemes": 0,
        "total_departments": 0,
        "total_states": 0,
        "total_categories": 0,
    }
    return createResult(None, stats)

# =========================================
# FEATURED SCHEMES  (for the homepage carousel)
# =========================================

@schemesRouter.route("/featured", methods=["GET"])
def getFeaturedSchemes():
    """
    Returns the most recently updated schemes with real title/
    category/details/application_link, for the homepage carousel.
    ?limit=N controls how many (default 3, capped 1-10).
    """
    limit = request.args.get("limit", default=3, type=int)
    limit = max(1, min(limit, 10))

    sql = f"""
        SELECT scheme_id, title, details, category, department, application_link
        FROM schemes
        WHERE title IS NOT NULL AND TRIM(title) <> ''
        ORDER BY last_updated DESC
        LIMIT {limit}
    """
    result = db.executeQuery(sql, ())
    return createResult(None, result)