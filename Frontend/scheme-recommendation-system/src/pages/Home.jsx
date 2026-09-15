import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";
import { Swiper, SwiperSlide } from "swiper/react";

import {
  Autoplay,
  Navigation,
  Pagination,
} from "swiper/modules";

import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

// -----------------------------------------------------------------
// Point this at your Flask backend. Adjust the port if yours differs
// (e.g. if Flask runs on 5000 this is correct; change if needed).
// -----------------------------------------------------------------
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

// Stock photos used as carousel backgrounds since the `schemes` table
// has no image column - cycled through by index, not tied to content.
const CAROUSEL_IMAGES = [
  "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1200",
  "https://images.pexels.com/photos/1454360/pexels-photo-1454360.jpeg",
  "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?q=80&w=1200",
];

const CAROUSEL_BADGE_COLORS = ["bg-success", "bg-primary", "bg-danger"];

// Keyword -> emoji lookup for whatever category strings actually exist
// in the database (these differ per scraped source, e.g. "Agriculture
// Credit", "Water & Sanitation" etc.) - falls back to a generic icon
// for anything unrecognized instead of breaking the layout.
const CATEGORY_ICON_RULES = [
  [/bank|finance|credit/i, "🏦"],
  [/business|industry|enterprise|startup/i, "🚀"],
  [/agricult|farm|crop|dairy|animal husbandry/i, "🌾"],
  [/educat|scholarship|student/i, "🎓"],
  [/health|wellness|medical|hospital/i, "❤️"],
  [/women|child|maternity/i, "👩"],
  [/hous(e|ing)|shelter/i, "🏠"],
  [/employ|job|labour|labor|skill/i, "🧑‍💼"],
  [/disab|differently.?abled/i, "♿"],
  [/senior|elder|old age/i, "👴"],
  [/water|sanitation|irrigation/i, "💧"],
  [/social|welfare|caste|tribal/i, "🤝"],
  [/pension|insurance/i, "🛡️"],
];

const getCategoryIcon = (categoryName) => {
  const match = CATEGORY_ICON_RULES.find(([regex]) => regex.test(categoryName || ""));
  return match ? match[1] : "📋";
};

// Light text cleanup for the carousel description only - strips an
// embedded "Date : ..." line if present and truncates to a teaser.
const buildTeaser = (rawDetails, maxLength = 150) => {
  if (!rawDetails) return "";
  let text = rawDetails
    .toString()
    .replace(/Date\s*:\s*\d{2}\/\d{2}\/\d{4}\s*-\s*(?:\d{2}\/\d{2}\/\d{4})?/, "")
    .replace(/\s+/g, " ")
    .trim();

  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + "…";
};

// Fetch helper: unwraps the backend's { message, data } response shape
// (falls back to the raw payload if the shape differs).
const fetchJson = async (url) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  const json = await res.json();
  return json && json.data !== undefined ? json.data : json;
};

export default function Home() {
  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  const [categories, setCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);

  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  const [featuredSchemes, setFeaturedSchemes] = useState([]);
  const [featuredLoading, setFeaturedLoading] = useState(true);

  useEffect(() => {
    loadCategories();
    loadStats();
    loadFeaturedSchemes();
  }, []);

  const loadCategories = async () => {
    try {
      setCategoriesLoading(true);
      const data = await fetchJson(`${API_BASE}/schemes/categories`);
      setCategories(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error loading categories:", error);
      setCategories([]);
    } finally {
      setCategoriesLoading(false);
    }
  };

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

  const loadFeaturedSchemes = async () => {
    try {
      setFeaturedLoading(true);
      const data = await fetchJson(`${API_BASE}/schemes/featured?limit=3`);
      setFeaturedSchemes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error loading featured schemes:", error);
      setFeaturedSchemes([]);
    } finally {
      setFeaturedLoading(false);
    }
  };

  return (
    <div className="home-page">

      {/* POPULAR SCHEMES */}

      <section className="container py-5">

        {featuredLoading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary"></div>
          </div>
        ) : featuredSchemes.length === 0 ? (
          <div className="text-center text-muted py-5">
            No schemes available right now.
          </div>
        ) : (
          <Swiper
            spaceBetween={30}
            slidesPerView={1}
            autoplay={{
              delay: 5000,
              disableOnInteraction: false,
            }}
            navigation={true}
            pagination={{ clickable: true }}
            modules={[Autoplay, Navigation, Pagination]}
          >
            {featuredSchemes.map((scheme, index) => (
              <SwiperSlide key={scheme.scheme_id}>
                <div className="card border-0 shadow-lg scheme-main-card">
                  <div className="row g-0 align-items-center">

                    <div className="col-md-6">
                      <img
                        src={CAROUSEL_IMAGES[index % CAROUSEL_IMAGES.length]}
                        className="img-fluid rounded-start scheme-big-image"
                        alt={scheme.title}
                      />
                    </div>

                    <div className="col-md-6 p-5">
                      {scheme.category && (
                        <span
                          className={`badge ${CAROUSEL_BADGE_COLORS[index % CAROUSEL_BADGE_COLORS.length]} mb-3`}
                        >
                          {scheme.category}
                        </span>
                      )}

                      <h2 className="fw-bold">{scheme.title}</h2>

                      <p className="text-muted mt-3">
                        {buildTeaser(scheme.details) || "Details available on the scheme page."}
                      </p>

                      <button
                        className="btn btn-primary mt-3 px-4"
                        onClick={() => navigate(`/schemes/${scheme.scheme_id}`)}
                      >
                        View Details →
                      </button>
                    </div>

                  </div>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        )}
      </section>

      {/* FIND SCHEME SECTION */}
      <section className="find-section py-5">
        <div className="container">
          <div className="row align-items-center">

            <div className="col-md-6">
              <h2 className="fw-bold">
                Not sure which schemes are right for you?
              </h2>

              <p className="text-muted mt-3">
                Answer simple questions and discover schemes
                based on your profile.
              </p>

              <button
                className="btn btn-primary mt-3"
                onClick={() => navigate("/findscheme")}
              >
                Start Recommendation
              </button>
            </div>

          </div>
        </div>
      </section>

      {/* POPULAR CATEGORIES */}
      <section className="container py-5">

        <div className="text-center mb-5">
          <h2 className="fw-bold">Popular Categories</h2>

          <p className="text-muted">
            Browse schemes by categories that matter to you
          </p>
        </div>

        {categoriesLoading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary"></div>
          </div>
        ) : categories.length === 0 ? (
          <div className="text-center text-muted py-5">
            No categories found yet.
          </div>
        ) : (
          <div className="row g-4">
            {categories.map((cat) => (
              <div className="col-md-3" key={cat.category}>
                <div
                  className="category-card shadow-sm p-4 text-center h-100"
                  role="button"
                  onClick={() =>
                    navigate(`/schemes?category=${encodeURIComponent(cat.category)}`)
                  }
                >
                  <div className="category-icon mb-3">
                    {getCategoryIcon(cat.category)}
                  </div>

                  <h5>{cat.category}</h5>

                  <p className="text-primary fw-semibold mt-2">
                    {cat.scheme_count} {cat.scheme_count === 1 ? "Scheme" : "Schemes"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* STATS */}
      <section className="stats-section py-5">
        <div className="container">
          <div className="row text-center">

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">
                {statsLoading ? "…" : `${stats?.total_schemes ?? 0}+`}
              </h2>
              <p>Schemes</p>
            </div>

            {/* Not tracked in the schemes table - kept as a placeholder */}
            <div className="col-md-3">
              <h2 className="fw-bold text-primary">10M+</h2>
              <p>Users Benefited</p>
            </div>

            {/* Not tracked in the schemes table - kept as a placeholder */}
            <div className="col-md-3">
              <h2 className="fw-bold text-primary">5M+</h2>
              <p>Applications</p>
            </div>

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">
                {statsLoading ? "…" : `${stats?.total_departments ?? 0}+`}
              </h2>
              <p>Departments</p>
            </div>

          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer-section text-white py-5">
        <div className="container">

          <div className="row">

            <div className="col-md-4">
              <h4>SmartScheme</h4>

              <p className="mt-3">
                Your trusted platform for discovering
                government schemes easily.
              </p>
            </div>

            <div className="col-md-2">
              <h5>Quick Links</h5>

              <p>Schemes</p>
              <p>Resources</p>
              <p>About</p>
            </div>

            <div className="col-md-3">
              <h5>Support</h5>

              <p>Help Center</p>
              <p>FAQs</p>
              <p>Contact</p>
            </div>

          </div>

        </div>
      </footer>

    </div>
  );
}