import { useState } from "react";
import { registerUser } from "../services/userServices";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const register = async () => {
    if (!name || !email || !password) {
      return toast.warn("All fields required");
    }

    const result = await registerUser({ name, email, password });

    if (!result.error) {
      toast.success("Registered successfully");
      navigate("/login");
    } else {
      toast.error(result.error);
    }
  };

  return (
    <div className="container w-50 mt-4">
      <h3>Register</h3>

      <input className="form-control mb-2" placeholder="Name"
        onChange={(e) => setName(e.target.value)} />

      <input className="form-control mb-2" placeholder="Email"
        onChange={(e) => setEmail(e.target.value)} />

      <input className="form-control mb-2" type="password" placeholder="Password"
        onChange={(e) => setPassword(e.target.value)} />

      <button className="btn btn-success" onClick={register}>
        Register
      </button>
    </div>
  );
}