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

export default function Home() {
  const navigate = useNavigate();

  const token = localStorage.getItem("token");

  return (
    <div className="home-page">

      {/* POPULAR SCHEMES */}

<section className="container py-5">

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

    {/* CARD 1 */}
    <SwiperSlide>
      <div className="card border-0 shadow-lg scheme-main-card">
        <div className="row g-0 align-items-center">

          <div className="col-md-6">
            <img
              src="https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1200"
              className="img-fluid rounded-start scheme-big-image"
              alt="Farmer Scheme"
            />
          </div>

          <div className="col-md-6 p-5">
            <span className="badge bg-success mb-3">
              Agriculture
            </span>

            <h2 className="fw-bold">
              PM Kisan Samman Nidhi
            </h2>

            <p className="text-muted mt-3">
              Financial support provided to eligible farmer families
              across India for agricultural needs.
            </p>

            <button className="btn btn-primary mt-3 px-4">
              Apply Now →
            </button>
          </div>

        </div>
      </div>
    </SwiperSlide>

    {/* CARD 2 */}
    <SwiperSlide>
      <div className="card border-0 shadow-lg scheme-main-card">
        <div className="row g-0 align-items-center">

          <div className="col-md-6">
            <img
              src="https://images.pexels.com/photos/1454360/pexels-photo-1454360.jpeg"
              className="img-fluid rounded-start scheme-big-image"
              alt="Education"
            />
          </div>

          <div className="col-md-6 p-5">
            <span className="badge bg-primary mb-3">
              Education
            </span>

            <h2 className="fw-bold">
              Post Matric Scholarship
            </h2>

            <p className="text-muted mt-3">
              Financial assistance for students belonging
              to SC/ST/OBC categories.
            </p>

            <button className="btn btn-primary mt-3 px-4">
              Apply Now →
            </button>
          </div>

        </div>
      </div>
    </SwiperSlide>

    {/* CARD 3 */}
    <SwiperSlide>
      <div className="card border-0 shadow-lg scheme-main-card">
        <div className="row g-0 align-items-center">

          <div className="col-md-6">
            <img
              src="https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?q=80&w=1200"
              className="img-fluid rounded-start scheme-big-image"
              alt="Health"
            />
          </div>

          <div className="col-md-6 p-5">
            <span className="badge bg-danger mb-3">
              Health
            </span>

            <h2 className="fw-bold">
              Ayushman Bharat Yojana
            </h2>

            <p className="text-muted mt-3">
              Health insurance coverage up to ₹5 lakh
              per family annually.
            </p>

            <button className="btn btn-primary mt-3 px-4">
              Apply Now →
            </button>
          </div>

        </div>
      </div>
    </SwiperSlide>

  </Swiper>
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
                onClick={() => navigate("/recommendation-start")}
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

        <div className="row g-4">

          {[
            ["🏦", "Banking & Finance", "82 Schemes"],
            ["💼", "Business & Industry", "120 Schemes"],
            ["🌾", "Agriculture & Farmers", "95 Schemes"],
            ["🎓", "Education", "110 Schemes"],
            ["❤️", "Health & Wellness", "68 Schemes"],
            ["👩", "Women & Children", "76 Schemes"],
            ["🏠", "Housing", "54 Schemes"],
            ["🧑‍💼", "Employment", "88 Schemes"],
            ["♿", "Disability", "42 Schemes"],
            ["👴", "Senior Citizens", "35 Schemes"],
            ["📚", "Skill Development", "61 Schemes"],
            ["🚀", "Startups", "27 Schemes"]
          ].map((item, index) => (
            <div className="col-md-3" key={index}>

              <div className="category-card shadow-sm p-4 text-center h-100">

                <div className="category-icon mb-3">
                  {item[0]}
                </div>

                <h5>{item[1]}</h5>

                <p className="text-primary fw-semibold mt-2">
                  {item[2]}
                </p>

              </div>

            </div>
          ))}

        </div>
      </section>

      {/* STATS */}
      <section className="stats-section py-5">
        <div className="container">
          <div className="row text-center">

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">1000+</h2>
              <p>Schemes</p>
            </div>

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">10M+</h2>
              <p>Users Benefited</p>
            </div>

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">5M+</h2>
              <p>Applications</p>
            </div>

            <div className="col-md-3">
              <h2 className="fw-bold text-primary">50+</h2>
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