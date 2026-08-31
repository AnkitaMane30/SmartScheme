const BASE_URL = "http://localhost:5000/users";

// =====================================================
// REGISTER
// =====================================================

export async function registerUser(data) {
  const response = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Registration failed"
    );
  }

  return result;
}


// =====================================================
// LOGIN
// =====================================================

export async function loginUser(email, password) {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Login failed"
    );
  }

  return result;
}


// =====================================================
// GET BASIC PROFILE
// =====================================================

export async function getProfile() {
  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    throw new Error("No authentication token found");
  }

  const response = await fetch(`${BASE_URL}/profile`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });

  const result = await response.json();

  console.log("GET PROFILE RESPONSE:", result);

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Failed to get profile"
    );
  }

  return result;
}


// =====================================================
// GET COMPLETE USER INFO
// =====================================================

export async function getUserInfo() {
  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    throw new Error("No authentication token found");
  }

  const response = await fetch(`${BASE_URL}/user-info`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  const result = await response.json();

  console.log("GET USER INFO RESPONSE:", result);

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Failed to get user information"
    );
  }

  return result;
}


// =====================================================
// COMPLETE PROFILE
// =====================================================

export async function completeProfile(data) {
  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    throw new Error("User is not logged in");
  }

  console.log("TOKEN BEFORE COMPLETE PROFILE:", token);

  const response = await fetch(
    `${BASE_URL}/complete-profile`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
  );

  const result = await response.json();

  console.log("COMPLETE PROFILE RESPONSE:", result);

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Failed to complete profile"
    );
  }

  return result;
}


// =====================================================
// UPDATE USER INFO
// =====================================================

export async function updateUserInfo(data) {
  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    throw new Error("User is not logged in");
  }

  const response = await fetch(
    `${BASE_URL}/update-user-info`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
  );

  const result = await response.json();

  console.log("UPDATE USER INFO RESPONSE:", result);

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Failed to update user information"
    );
  }

  return result;
}

// =====================================================
// PROFILE STATUS
// =====================================================

export async function getProfileStatus() {
  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    throw new Error("User is not logged in");
  }

  const response = await fetch(
    `${BASE_URL}/profile-status`,
    {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    }
  );

  const result = await response.json();

  console.log("PROFILE STATUS RESPONSE:", result);

  if (!response.ok) {
    throw new Error(
      result?.error ||
      result?.message ||
      "Failed to fetch profile status"
    );
  }

  return result;
}