import { useState } from "react";
import { loginUser, getProfile } from "../services/userServices";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const login = async () => {
    if (!email || !password) {
      return toast.warn("Enter all fields");
    }

    const result = await loginUser(email, password);

    if (result.error) {
      return toast.error(result.error);
    }

    // SAVE TOKEN
    localStorage.setItem("token", result.data.token);

    // FETCH PROFILE AFTER LOGIN
    const profileRes = await getProfile();

    if (profileRes.error) {
      return toast.error(profileRes.error);
    }

    // SAVE USER DATA
    localStorage.setItem("user", JSON.stringify(profileRes.data));

    // UPDATE NAVBAR IMMEDIATELY
    window.dispatchEvent(new Event("userUpdated"));

    toast.success("Login successful");

    // ALWAYS GO HOME PAGE AFTER LOGIN
    navigate("/");
  };

  return (
    <div className="container w-50 mt-5">
      <div className="card shadow p-4">
        <h3 className="text-center mb-4">Login</h3>

        <input
          className="form-control mb-3"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="form-control mb-3"
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="btn btn-primary w-100" onClick={login}>
          Login
        </button>

        <p className="mt-3 text-center">
          Don't have account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}