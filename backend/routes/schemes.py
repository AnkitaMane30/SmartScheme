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