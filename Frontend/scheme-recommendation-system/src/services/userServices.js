const BASE_URL = "http://localhost:5000/users";

// REGISTER
export async function registerUser(data) {
  const res = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  return await res.json();
}

// LOGIN
export async function loginUser(email, password) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  return await res.json();
}

// COMPLETE PROFILE
export async function completeProfile(data) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/complete-profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(data),
  });

  return await res.json();
}

// UPDATE PROFILE
export async function updateProfile(data) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/update-profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(data),
  });

  return await res.json();
}

// GET PROFILE
export async function getProfile() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/profile`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    },
  });

  return await res.json();
}