import { useEffect, useState, useRef } from "react";
import {
  Link,
  useNavigate,
  useLocation
} from "react-router-dom";

import { getUserInfo } from "../services/userServices";

export default function Navbar() {

  const navigate = useNavigate();
  const location = useLocation();

  const [user, setUser] = useState(null);
  const [showProfile, setShowProfile] = useState(false);

  const profileRef = useRef(null);

  // ============================================================
  // LOAD USER FROM LOCAL STORAGE
  // ============================================================

  const loadStoredUser = () => {

    const storedUser =
      localStorage.getItem("user");

    if (
      storedUser &&
      storedUser !== "undefined" &&
      storedUser !== "null"
    ) {

      try {

        return JSON.parse(storedUser);

      } catch (error) {

        console.error(
          "INVALID USER DATA IN LOCAL STORAGE:",
          error
        );

        localStorage.removeItem("user");

        return null;
      }
    }

    return null;
  };

  // ============================================================
  // FETCH LATEST USER FROM BACKEND
  // ============================================================

  const fetchUser = async () => {

    const token =
      localStorage.getItem("token");

    // ----------------------------------------------------------
    // NO TOKEN
    // ----------------------------------------------------------

    if (
      !token ||
      token === "undefined" ||
      token === "null"
    ) {

      setUser(null);

      return;
    }

    // ----------------------------------------------------------
    // GET USER
    // ----------------------------------------------------------

    try {

      const result =
        await getUserInfo();

      console.log(
        "NAVBAR USER INFO:",
        result
      );

      if (
        result?.status === "success" &&
        result?.data
      ) {

        // ======================================================
        // UPDATE REACT STATE
        // ======================================================

        setUser(result.data);

        // ======================================================
        // UPDATE LOCAL STORAGE
        // ======================================================

        localStorage.setItem(
          "user",
          JSON.stringify(result.data)
        );

      } else {

        console.error(
          "INVALID USER INFO RESPONSE:",
          result
        );

      }

    } catch (error) {

      console.error(
        "NAVBAR PROFILE ERROR:",
        error
      );

      // --------------------------------------------------------
      // DO NOT LOG USER OUT JUST BECAUSE API FAILED
      // --------------------------------------------------------

      const storedUser =
        loadStoredUser();

      if (storedUser) {

        setUser(storedUser);

      }

    }
  };

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {

    const storedUser =
      loadStoredUser();

    if (storedUser) {

      setUser(storedUser);

    }

    fetchUser();

  }, []);

  // ============================================================
  // USER UPDATED EVENT
  // ============================================================
  //
  // UpdateProfile will dispatch:
  //
  // window.dispatchEvent(
  //   new CustomEvent("userUpdated", {
  //     detail: latestUser
  //   })
  // );
  //
  // Navbar receives the updated user here.
  // ============================================================

  useEffect(() => {

    const handleUserUpdated = (event) => {

      console.log(
        "USER UPDATED EVENT RECEIVED BY NAVBAR:",
        event
      );

      // ========================================================
      // GET UPDATED USER FROM EVENT
      // ========================================================

      const updatedUser =
        event?.detail;

      if (
        updatedUser &&
        typeof updatedUser === "object"
      ) {

        console.log(
          "INSTANT UPDATED USER:",
          updatedUser
        );

        // ======================================================
        // UPDATE NAVBAR STATE IMMEDIATELY
        // ======================================================

        setUser(updatedUser);

        // ======================================================
        // UPDATE LOCAL STORAGE
        // ======================================================

        localStorage.setItem(
          "user",
          JSON.stringify(updatedUser)
        );

      } else {

        // ======================================================
        // FALLBACK
        // If no event.detail is provided, fetch from backend.
        // ======================================================

        console.log(
          "NO UPDATED USER DATA IN EVENT."
        );

        fetchUser();

      }

    };

    window.addEventListener(
      "userUpdated",
      handleUserUpdated
    );

    return () => {

      window.removeEventListener(
        "userUpdated",
        handleUserUpdated
      );

    };

  }, []);

  // ============================================================
  // CLOSE PROFILE WHEN CLICKING OUTSIDE
  // ============================================================

  useEffect(() => {

    const handleClickOutside = (event) => {

      if (
        profileRef.current &&
        !profileRef.current.contains(
          event.target
        )
      ) {

        setShowProfile(false);

      }

    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {

      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );

    };

  }, []);

  // ============================================================
  // CLOSE PROFILE ON ROUTE CHANGE
  // ============================================================

  useEffect(() => {

    setShowProfile(false);

  }, [location.pathname]);

  // ============================================================
  // LOGOUT
  // ============================================================

  const logout = () => {

    localStorage.removeItem("token");

    localStorage.removeItem("user");

    setUser(null);

    setShowProfile(false);

    navigate("/");

  };

  // ============================================================
  // RETURN UI
  // ============================================================

  return (

    <nav className="navbar navbar-dark bg-dark px-4 py-2">

      {/* ======================================================
          LEFT SIDE
      ====================================================== */}

      <div className="d-flex align-items-center gap-4">

        {/* LOGO */}

        <Link
          to="/"
          className="navbar-brand fw-bold"
        >
          SmartScheme
        </Link>

        {/* NAVIGATION */}

        <div className="d-flex gap-3">

          <Link
            to="/schemes"
            className="btn btn-outline-light btn-sm"
          >
            Schemes
          </Link>

          <Link
            to="/about"
            className="btn btn-outline-light btn-sm"
          >
            About
          </Link>

        </div>

      </div>

      {/* ======================================================
          RIGHT SIDE
      ====================================================== */}

      <div className="d-flex align-items-center gap-3 ms-auto">

        {/* ====================================================
            LOGIN BUTTON
        ==================================================== */}

        {!user && (

          <button
            className="btn btn-primary"
            onClick={() =>
              navigate("/login")
            }
          >
            Login
          </button>

        )}

        {/* ====================================================
            LOGGED-IN USER
        ==================================================== */}

        {user && (

          <>

            {/* ==================================================
                EMAIL
            ================================================== */}

            <span className="text-white">
              {user?.email || "-"}
            </span>

            {/* ==================================================
                PROFILE CONTAINER
            ================================================== */}

            <div
              className="position-relative"
              ref={profileRef}
            >

              {/* PROFILE BUTTON */}

              <button
                className="btn btn-outline-light"
                onClick={() =>
                  setShowProfile(
                    (previous) =>
                      !previous
                  )
                }
                style={{
                  width: "45px",
                  height: "45px",
                  borderRadius: "50%"
                }}
              >
                👤
              </button>

              {/* =================================================
                  PROFILE DROPDOWN
              ================================================= */}

              {showProfile && (

                <div
                  className="card position-absolute end-0 mt-2 shadow p-3"
                  style={{
                    width: "300px",
                    zIndex: 1000
                  }}
                >

                  {/* =============================================
                      PROFILE HEADER
                  ============================================= */}

                  <div className="text-center mb-3">

                    <div
                      className="mx-auto mb-2 bg-primary text-white d-flex align-items-center justify-content-center"
                      style={{
                        width: "60px",
                        height: "60px",
                        borderRadius: "50%",
                        fontSize: "24px"
                      }}
                    >

                      {user?.name
                        ?.charAt(0)
                        ?.toUpperCase() || "U"}

                    </div>

                    <h6 className="mb-0">

                      {user?.name || "-"}

                    </h6>

                    <small className="text-muted">

                      {user?.email || "-"}

                    </small>

                  </div>

                  <hr />

                  {/* =============================================
                      PROFILE INFORMATION
                  ============================================= */}

                  <small>
                    <b>Gender:</b>{" "}
                    {user?.gender || "-"}
                  </small>

                  <br />

                  <small>
                    <b>Category:</b>{" "}
                    {user?.caste_category || "-"}
                  </small>

                  <br />

                  <small>
                    <b>Occupation:</b>{" "}
                    {user?.occupation || "-"}
                  </small>

                  <br />

                  <small>
                    <b>Education:</b>{" "}
                    {user?.education_level || "-"}
                  </small>

                  <br />

                  <small>
                    <b>Age:</b>{" "}
                    {user?.age ?? "-"}
                  </small>

                  <br />

                  <small>
                    <b>Income:</b>{" "}
                    {user?.annual_income ?? "-"}
                  </small>

                  <br />

                  <small>
                    <b>State:</b>{" "}
                    {user?.state || "-"}
                  </small>

                  <br />

                  <small>
                    <b>District:</b>{" "}
                    {user?.district || "-"}
                  </small>

                  <br />

                  <small>
                    <b>Marital Status:</b>{" "}
                    {user?.marital_status || "-"}
                  </small>

                  {/* =============================================
                      UPDATE PROFILE
                  ============================================= */}

                  <button
                    className="btn btn-outline-primary w-100 mt-3"
                    onClick={() => {

                      setShowProfile(false);

                      navigate(
                        "/update-profile"
                      );

                    }}
                  >
                    Update Profile
                  </button>

                  {/* =============================================
                      LOGOUT
                  ============================================= */}

                  <button
                    className="btn btn-danger w-100 mt-2"
                    onClick={logout}
                  >
                    Logout
                  </button>

                </div>

              )}

            </div>

          </>

        )}

      </div>

    </nav>

  );
}