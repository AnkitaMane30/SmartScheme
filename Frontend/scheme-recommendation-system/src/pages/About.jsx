import { useEffect, useState } from "react";
import {
  FaUsers,
  FaShieldAlt,
  FaRocket,
  FaHandshake,
  FaUserCheck,
  FaFileAlt,
  FaUniversity
} from "react-icons/fa";

// Same backend base used across the app - adjust the port if yours differs.
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

const fetchJson = async (url) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  const json = await res.json();
  return json && json.data !== undefined ? json.data : json;
};

export default function About() {
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setStatsLoading(true);
      const data = await fetchJson(`${API_BASE}/schemes/stats`);
      setStats(data);
    } catch (error) {
      console.error("Error loading stats:", error);
      setStats(null);
    } finally {
      setStatsLoading(false);
    }
  };

  const statValue = (value) =>
    statsLoading ? "…" : value !== undefined && value !== null ? value : "0";

  return (
    <div className="container-fluid p-0">

      {/* HERO */}
      <div className="bg-light p-5 d-flex justify-content-between align-items-center">
        <div>
          <h1 className="fw-bold">About SmartScheme</h1>
          <h4 className="text-primary mt-3">
            One platform. Real government scheme data. Easier to find.
          </h4>
          <p className="text-muted mt-4">
            SmartScheme collects government welfare scheme information directly
            from official state government portals and brings it together in
            one searchable, filterable place - so you don't have to dig through
            dozens of separate department websites to find what you're
            eligible for.
          </p>
        </div>

        <img
          src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png"
          width="300"
          alt=""
        />
      </div>

      {/* VALUES */}
      <div className="container mt-5">
        <h3 className="mb-4">What We Stand For</h3>

        <div className="row g-4">
          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <FaUsers size={35} color="blue" />
              <h5 className="mt-3">Citizen First</h5>
              <p>We put citizens at the center of everything we do.</p>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <FaShieldAlt size={35} color="green" />
              <h5 className="mt-3">Accuracy</h5>
              <p>
                Scheme details are pulled directly from official government
                sources, not rewritten or guessed.
              </p>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <FaRocket size={35} color="purple" />
              <h5 className="mt-3">Simplicity</h5>
              <p>We make the process of finding and applying simple.</p>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <FaHandshake size={35} color="orange" />
              <h5 className="mt-3">Inclusivity</h5>
              <p>Equal access to government opportunities for all.</p>
            </div>
          </div>
        </div>

        {/* MISSION + STATS */}
        <div className="row mt-5 g-4">
          <div className="col-md-6">
            <div className="card p-4 shadow-sm border-0">
              <h4>Our Mission</h4>
              <p>
                To make it easier for citizens to discover the government
                welfare schemes they're actually eligible for, by collecting
                official scheme information in one place instead of leaving
                it scattered across dozens of department websites.
              </p>

              <p><FaUserCheck className="text-primary" /> Empower Citizens</p>
              <p><FaFileAlt className="text-success" /> Simplify Access</p>
              <p><FaUniversity className="text-purple" /> Surface Real Government Data</p>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card p-4 shadow-sm border-0">
              <h4>Key Stats</h4>
              <p className="text-muted small mb-3">
                Live counts from our database, updated as new schemes are added.
              </p>

              <div className="row text-center mt-3">
                <div className="col-6 mb-3">
                  <div className="border rounded p-3">
                    <h3>{statValue(stats?.total_schemes)}</h3>
                    <small>Schemes Indexed</small>
                  </div>
                </div>

                <div className="col-6 mb-3">
                  <div className="border rounded p-3">
                    <h3>{statValue(stats?.total_categories)}</h3>
                    <small>Categories Covered</small>
                  </div>
                </div>

                <div className="col-6">
                  <div className="border rounded p-3">
                    <h3>{statValue(stats?.total_departments)}</h3>
                    <small>Government Departments</small>
                  </div>
                </div>

                <div className="col-6">
                  <div className="border rounded p-3">
                    <h3>{statValue(stats?.total_states)}</h3>
                    <small>State(s) Covered</small>
                  </div>
                </div>
              </div>

              <div className="alert alert-primary mt-3">
                We're actively expanding coverage to more states and
                departments over time.
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}