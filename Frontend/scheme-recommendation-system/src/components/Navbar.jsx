import { useEffect, useState, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { getProfile } from "../services/userServices";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const token = localStorage.getItem("token");

  // ✅ SAFE LOCALSTORAGE PARSE (FIX FOR "undefined")
  const storedUser = localStorage.getItem("user");

  const [user, setUser] = useState(
    storedUser && storedUser !== "undefined"
      ? JSON.parse(storedUser)
      : null
  );

  const [showProfile, setShowProfile] = useState(false);
  const profileRef = useRef();

  // ================= FETCH PROFILE =================
  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }

    getProfile()
      .then((res) => {
        if (!res.error && res.data) {
          setUser(res.data);
          localStorage.setItem(
            "user",
            JSON.stringify(res.data)
          );
        }
      })
      .catch((err) => console.log(err));
  }, [token]);

  // ================= USER UPDATE EVENT =================
  useEffect(() => {
    const updateUser = () => {
      const updated = localStorage.getItem("user");

      if (updated && updated !== "undefined") {
        setUser(JSON.parse(updated));
      } else {
        setUser(null);
      }
    };

    window.addEventListener("userUpdated", updateUser);

    return () => {
      window.removeEventListener("userUpdated", updateUser);
    };
  }, []);

  // ================= OUTSIDE CLICK CLOSE =================
  useEffect(() => {
    const handleClick = (e) => {
      if (
        profileRef.current &&
        !profileRef.current.contains(e.target)
      ) {
        setShowProfile(false);
      }
    };

    document.addEventListener("mousedown", handleClick);

    return () =>
      document.removeEventListener("mousedown", handleClick);
  }, []);

  // ================= CLOSE ON ROUTE CHANGE =================
  useEffect(() => {
    setShowProfile(false);
  }, [location.pathname]);

  // ================= LOGOUT =================
  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    setUser(null);
    setShowProfile(false);

    navigate("/");
  };

  return (
    <nav className="navbar navbar-dark bg-dark px-4 py-2">

      {/* LEFT */}
      <div className="d-flex align-items-center gap-4">

        <Link to="/" className="navbar-brand fw-bold">
          SmartScheme
        </Link>

        {/* PUBLIC LINKS */}
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

      {/* RIGHT */}
      <div className="d-flex align-items-center gap-3 ms-auto">

       
        {!token && (
          <button
            className="btn btn-primary"
            onClick={() => navigate("/login")}
          >
            Login
          </button>
        )}

        {token && (
          <>
            <span className="text-white medium">
              {user?.email}
            </span>

            <div
              className="position-relative"
              ref={profileRef}
            >
              {/* <button
                className="btn btn-outline-light"
                onClick={() => setShowProfile(!showProfile)}
                style={{
                  width: "45px",
                  height: "45px",
                }}
              >
              👤
              </button> */}

              {/* {showProfile && (
                <div
                  className="card position-absolute end-0 mt-2 shadow p-3"
                  style={{
                    width: "280px",
                    zIndex: 1000,
                  }}
                >
                  <div className="text-center mb-3">
                    <div
                      className="mx-auto mb-2 bg-primary text-white d-flex align-items-center justify-content-center"
                      style={{
                        width: "60px",
                        height: "60px",
                        borderRadius: "50%",
                        fontSize: "24px",
                      }}
                    >
                      {user?.name?.charAt(0)}
                    </div>

                    <h6 className="mb-0">{user?.name}</h6>
                    <small className="text-muted">
                      {user?.email}
                    </small>
                  </div>

                  <hr />

                  <small><b>Gender:</b> {user?.gender || "-"}</small><br />
                  <small><b>Category:</b> {user?.category || "-"}</small><br />
                  <small><b>Occupation:</b> {user?.occupation || "-"}</small><br />
                  <small><b>Education:</b> {user?.education_level || "-"}</small><br />
                  <small><b>Age:</b> {user?.age || "-"}</small><br />
                  <small><b>Income:</b> {user?.income || "-"}</small><br />
                  <small><b>State:</b> {user?.state || "-"}</small>

                  <button
                    className="btn btn-outline-primary w-100 mt-3"
                    onClick={() => navigate("/dashboard")}
                  >
                    Update Profile
                  </button> */}

                  <button
                    className="btn btn-danger w-100 mt-2"
                    onClick={logout}
                  >
                    Logout
                  </button>
                </div>
              {/* )}
            </div> */}
          </>
        )}
      </div>
    </nav>
  );
}