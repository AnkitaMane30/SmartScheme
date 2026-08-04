import {
  FaUsers,
  FaShieldAlt,
  FaRocket,
  FaHandshake,
  FaUserCheck,
  FaFileAlt,
  FaUniversity
} from "react-icons/fa";

export default function About() {
  return (
    <div className="container-fluid p-0">

      {/* HERO */}
      <div className="bg-light p-5 d-flex justify-content-between align-items-center">
        <div>
          <h1 className="fw-bold">About MyScheme</h1>
          <h4 className="text-primary mt-3">
            One platform. Many schemes. Endless opportunities.
          </h4>
          <p className="text-muted mt-4">
            MyScheme is a unified platform that helps citizens discover,
            check eligibility and apply for government schemes easily.
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
              <h5 className="mt-3">Transparency</h5>
              <p>We provide accurate and updated information.</p>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <FaRocket size={35} color="purple" />
              <h5 className="mt-3">Simplicity</h5>
              <p>We make the process of applying simple.</p>
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
                To empower every citizen by providing a single trusted platform
                to access and benefit from government schemes.
              </p>

              <p><FaUserCheck className="text-primary" /> Empower Citizens</p>
              <p><FaFileAlt className="text-success" /> Simplify Access</p>
              <p><FaUniversity className="text-purple" /> Drive Impact</p>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card p-4 shadow-sm border-0">
              <h4>Key Stats</h4>

              <div className="row text-center mt-3">
                <div className="col-6 mb-3">
                  <div className="border rounded p-3">
                    <h3>25K+</h3>
                    <small>Schemes Integrated</small>
                  </div>
                </div>

                <div className="col-6 mb-3">
                  <div className="border rounded p-3">
                    <h3>10M+</h3>
                    <small>Users Benefited</small>
                  </div>
                </div>

                <div className="col-6">
                  <div className="border rounded p-3">
                    <h3>5M+</h3>
                    <small>Applications Submitted</small>
                  </div>
                </div>

                <div className="col-6">
                  <div className="border rounded p-3">
                    <h3>50+</h3>
                    <small>Partner Ministries</small>
                  </div>
                </div>
              </div>

              <div className="alert alert-primary mt-3">
                MyScheme is your trusted partner in discovering opportunities.
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}