import { useState } from "react";
import { loginUser, getUserInfo } from "../services/userServices";
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

  try {
    const result = await loginUser(email, password);

    console.log("LOGIN RESPONSE:", result);

    if (!result?.data?.token) {
      console.error("TOKEN NOT FOUND:", result);
      return toast.error("Login failed: token not received");
    }

    // SAVE TOKEN FIRST
    localStorage.setItem("token", result.data.token);

    console.log(
      "TOKEN SAVED:",
      localStorage.getItem("token")
    );

    // FETCH COMPLETE USER INFO
    const profileRes = await getUserInfo();

    console.log("USER INFO AFTER LOGIN:", profileRes);

    if (!profileRes?.data) {
      return toast.error("Failed to load user profile");
    }

    // SAVE USER
    localStorage.setItem(
      "user",
      JSON.stringify(profileRes.data)
    );

    // TELL NAVBAR TO UPDATE
    window.dispatchEvent(
      new Event("userUpdated")
    );

    toast.success("Login successful");

    navigate("/");
  } catch (error) {
    console.error("LOGIN ERROR:", error);

    toast.error(
      error.message || "Login failed"
    );
  }
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