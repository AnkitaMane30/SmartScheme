# SmartScheme – AI Based Government Scheme Intelligent System with Automated Web Scraping

## Project Overview

SmartScheme is an AI-based Government Scheme Recommendation System developed to simplify the process of discovering government welfare schemes in India. Government schemes provide financial assistance, educational support, healthcare benefits, employment opportunities, housing support, and other welfare services. However, information about these schemes is distributed across multiple government websites, making it difficult for citizens to identify schemes relevant to their needs.

SmartScheme addresses this problem by providing a centralized web-based platform that automatically collects government scheme information, analyses user profiles, checks eligibility conditions, and recommends relevant schemes.

The system uses automated web scraping to collect scheme information from official government sources. The collected data is cleaned, structured, and stored in a MySQL database. Based on user attributes such as age, gender, income, occupation, education, location, and caste category, the recommendation module identifies potentially eligible schemes and ranks them according to their relevance.

By integrating automated data collection, eligibility checking, content-based similarity, and machine-learning-based ranking, SmartScheme aims to make government welfare information more accessible, organized, and personalized.

## Objectives

The main objectives of SmartScheme are:

1. **Centralized Scheme Access:** To provide a centralized platform for accessing multiple government schemes through a single system.
2. **Intelligent Scheme Recommendation:** To analyse user attributes such as age, income, occupation, and location to determine eligibility and recommend relevant government schemes using an intelligent, data-driven approach.
3. **Automated Scheme Data Updates:** To maintain up-to-date government scheme information through automated web scraping and regular data updates.

## Problem Statement

Citizens face difficulties accessing government welfare schemes because information is scattered across multiple websites, eligibility criteria are complex, and scheme details may change frequently. This can lead to limited awareness and underutilization of available government benefits.

SmartScheme addresses this problem by combining automated scheme data collection with personalized eligibility analysis and recommendation in a single platform.

## Key Features

- **User Registration and Authentication:** Supports user account creation and secure login using JWT-based authentication.
- **User Profile Management:** Allows users to provide and update personal and socioeconomic details required for eligibility analysis.
- **Automated Web Scraping:** Collects government scheme information from relevant official websites using Python, Requests, and BeautifulSoup.
- **Scheme Data Processing:** Cleans, validates, structures, and stores collected information in a MySQL database.
- **Change Detection:** Uses hash-based comparison to detect changes in previously collected scheme information.
- **Rule-Based Eligibility Checking:** Compares user profile attributes with scheme eligibility conditions.
- **AI-Based Scheme Recommendation:** Combines eligibility filtering, content similarity, machine-learning predictions, and weighted scoring to rank relevant schemes.
- **Search and Filtering:** Enables users to search schemes using keywords and filter results by criteria such as category, state, age, and income range.
- **Detailed Scheme Information:** Displays scheme descriptions, eligibility criteria, benefits, required documents, application procedures, and available official links.
- **Administrative Management:** Provides administrative functionality for managing scheme-related information and system operations.

## Recommendation Methodology

SmartScheme uses a hybrid recommendation approach to identify and rank government schemes relevant to individual users.

The recommendation workflow consists of the following stages:

1. **User Profile Analysis:** Collects relevant user attributes, including age, gender, income, occupation, education, location, and other eligibility-related details.
2. **Eligibility Filtering:** Applies rule-based logic to compare user attributes with scheme eligibility requirements.
3. **TF-IDF and Cosine Similarity:** Represents user-profile information and scheme content numerically and measures their textual similarity.
4. **Random Forest Prediction:** Uses relevant user, scheme, eligibility, and similarity-based features to estimate scheme relevance.
5. **Category-Based Score Boosting:** Gives additional importance to relevant scheme categories where appropriate.
6. **Weighted Scoring and Ranking:** Combines the relevant recommendation signals to calculate the final ranking.
7. **Top-N Recommendations:** Presents a ranked list of the most relevant schemes to reduce information overload.

This hybrid approach combines explicit eligibility checking with content-based matching and machine-learning-based ranking.

## System Architecture

SmartScheme follows a modular client-server architecture consisting of the following components:

- **Frontend Layer:** Provides the user interface for registration, login, profile management, scheme search, and recommendations.
- **Backend Layer:** Handles API requests, authentication, application logic, and communication between system components.
- **Web Scraping Module:** Collects scheme information from official government websites.
- **Data Processing Module:** Cleans, validates, structures, and prepares the collected data for storage.
- **Recommendation Module:** Performs eligibility checking, similarity analysis, machine-learning prediction, and recommendation ranking.
- **Database Layer:** Stores user profiles and structured government scheme information.
- **External Data Sources:** Supplies scheme information through relevant government websites and portals.

The React.js frontend communicates with the Python Flask backend through REST APIs, while MySQL provides structured data storage.

## 🛠️ Technologies Used

| Component | Technologies |
|---|---|
| Frontend | React.js, HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | MySQL |
| Web Scraping | Python, Requests, BeautifulSoup |
| Recommendation Techniques | Rule-based eligibility, TF-IDF, Cosine Similarity, Random Forest |
| Ranking Techniques | Category-based score boosting, weighted scoring, Top-N ranking |
| Authentication | JWT-based authentication, password hashing |
| API Communication | REST APIs |
| Development Tools | Visual Studio Code, Git, GitHub |



## 🔄 Working Flow

The overall workflow of SmartScheme is as follows:

1. Government scheme information is collected from relevant official government websites.
2. The scraped information is cleaned, validated, and converted into a structured format.
3. Hash-based change detection helps identify modifications in previously collected information.
4. Processed scheme records are stored in the MySQL database.
5. Users register, log in, and provide their profile information.
6. The system evaluates the user's profile against scheme eligibility conditions.
7. Eligible schemes are evaluated using content similarity and the Random Forest recommendation model.
8. Category-based boosting and weighted scoring are applied to rank relevant schemes.
9. The system displays a personalized Top-N list of recommended schemes.
10. Users can search, filter, and view detailed scheme information, including available application links.

## 📂 Project Structure

The project is organized into frontend and backend components, along with supporting data processing and recommendation functionality.

```text
SmartScheme/
│
├── Backend/
│   ├── Flask application
│   ├── API routes
│   ├── User authentication and profile management
│   ├── Web scraping module
│   ├── Data processing module
│   └── Recommendation module
│
├── Frontend/
│   └── scheme-recommendation-system/
│       ├── src/
│       │   ├── components/
│       │   └── services/
│       ├── public/
│       ├── package.json
│       └── vite.config.js
│
├── README.md
└── .gitignore
```

*Note: This is a logical overview of the project structure. Refer to the actual repository for the complete list of files and folders.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following software before running the application:

- Python 3.x
- Node.js and npm
- MySQL Server
- MySQL Workbench
- Git
- Visual Studio Code or another compatible IDE
- An internet connection

### 1. Clone the Repository

```bash
git clone https://github.com/AnkitaMane30/SmartScheme.git
cd SmartScheme
```

### 2. Configure the MySQL Database

1. Install and start MySQL Server.
2. Create the project database.
3. Create or import the required tables for users, schemes, and related information.
4. Configure the database connection settings in the Flask backend.
5. Import existing scheme data if it is available.

Use the database name and configuration values expected by your backend code.

### 3. Set Up the Backend

Open a terminal and navigate to the directory containing the Flask application.

```bash
cd Backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install the Python dependencies using the project's dependency file:

```bash
pip install -r requirements.txt
```

Configure the required database connection details and other environment variables.

Start the Flask application using the actual entry-point file configured in your repository. For example:

```bash
python app.py
```

The backend is configured to run on the address and port specified by the application, commonly `http://localhost:5000` during local development.

### 4. Set Up the Frontend

Open another terminal and navigate to the React frontend directory:

```bash
cd Frontend/scheme-recommendation-system
```

Install the dependencies:

```bash
npm install
```

Start the frontend development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal to access SmartScheme.

**Note:** The backend and frontend must both be running. Verify the actual backend entry-point filename, dependency files, database configuration, and API URL in the repository before executing these commands.

## User Guide

### Registration and Login
- Open the SmartScheme web application.
- Register using the required details.
- Log in using your registered credentials.

### Profile Management
- Navigate to the profile section.
- Enter relevant details such as age, income, occupation, education, location, and other required attributes.
- Save the profile to use it for eligibility analysis and recommendations.

### Scheme Recommendation
- Open the recommended schemes section.
- Allow the system to analyse your profile against scheme eligibility conditions.
- Review the personalized list of potentially eligible and relevant schemes.

### Scheme Search and Filtering
- Enter a keyword to search for schemes.
- Apply available filters such as category, state, age, or income range.
- Review the matching results.

### Viewing Scheme Details
Select a scheme to view available information, including:

- Scheme name and description
- Eligibility criteria
- Benefits
- Required documents
- Application procedure
- Official source or application link

## Hardware and Software Requirements

### Hardware Requirements
- Processor: Intel Core i3 or equivalent and above
- RAM: Minimum 4 GB
- Storage: Minimum 10 GB of available space
- Internet connection for accessing government websites and web scraping

### Software Requirements
- Operating System: Windows or Linux
- Frontend: React.js, HTML, CSS, JavaScript
- Backend: Python Flask
- Database: MySQL
- Web Scraping: Requests and BeautifulSoup
- Development Environment: Visual Studio Code or a compatible IDE
- Browser: Google Chrome, Microsoft Edge, or an equivalent modern browser

## Testing

Testing is performed to verify the functionality and integration of the major system modules.

- **Unit Testing:** Tests individual functions, including user registration, login, profile management, eligibility checking, searching, and recommendation generation.
- **Integration Testing:** Verifies communication between the React frontend, Flask backend, MySQL database, web scraping module, and recommendation engine.
- **System Testing:** Evaluates the complete application, including authentication, profile completion, scheme discovery, eligibility evaluation, and personalized recommendations.

The project report documents test cases for login, profile completion, scheme search, eligibility checking, scheme recommendation, scheme details, profile updates, and scheme filtering.

## Applications

SmartScheme can support several areas of government welfare and public service discovery:

1. **Citizen Welfare Services:** Helps citizens discover potentially eligible government schemes.
2. **Educational Support:** Helps students identify scholarships and educational assistance schemes.
3. **Financial Assistance:** Supports the discovery of subsidies, financial assistance, and government support programs.
4. **Rural and Social Welfare:** Helps citizens explore relevant welfare schemes offered by Central and State Governments.
5. **Government Service Facilitation:** Can assist public service centres and welfare organizations in guiding citizens.
6. **Centralized Scheme Discovery:** Reduces the need to search multiple websites manually.

## Future Scope

Possible future enhancements include:

- Integrating additional Central and State Government portals.
- Introducing multilingual support for regional Indian languages.
- Developing a dedicated Android or iOS application.
- Incorporating user feedback to improve recommendation quality.
- Adding email, SMS, or application notifications for new schemes, eligibility changes, and important deadlines.
- Improving scalability, accessibility, and personalization.

## 🎓 Project Information

- **Project Name:** SmartScheme – AI Based Government Scheme Intelligent System with Automated Web Scraping
- **Project Type:** Final Year Project
- **Domain:** Web Development, Artificial Intelligence, and Machine Learning
- **Primary Goal:** To simplify government scheme discovery through automated data collection, eligibility analysis, and personalized recommendations.

## Contributors

Developed collaboratively as part of a final-year academic project.

- [Siddhi Chavan](https://github.com/siddhichavan026)
- [Ankita Mane](https://github.com/AnkitaMane30)
- [Anuradha Mudhale]
- [Gouri Mangore]
- [Samiksha Mane]

## References

The project is informed by research on government scheme recommendation, eligibility matching, semantic search, automated web scraping, and AI-based information processing.

The literature reviewed in the project report includes works by Rokade et al., Sharma and Borkar, Barba et al., Maheshwari et al., Vaishnavi et al., Dixit et al., Thiyagarajan et al., and Velmurugan et al.

Refer to the final project report's bibliography for the full reference details.

## License

This project has been developed for academic purposes. No specific open-source license is declared here. Add an appropriate license if the project is intended for public distribution or reuse.

## Acknowledgements

We acknowledge the official government portals and publicly available resources used for government scheme information. We also thank our project guide, faculty member, and team contributors for their support and guidance throughout the development of SmartScheme.

