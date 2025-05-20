# Rent Near TU: Affordable Dormitory Solution for Thammasat University

## Abstract

### Purpose
Dormitories are a cornerstone of quality of life, particularly for students, workers, and low-to-middle-income families who frequently encounter barriers in securing affordable and suitable accommodations. This challenge is acutely felt around Thammasat University’s Rangsit Campus, where the high demand for dormitories is underserved by fragmented systems that lack centralized, accessible information and the flexibility to cater to diverse budgetary and lifestyle requirements. The absence of a streamlined platform often forces individuals to rely on time-consuming, costly, and inefficient methods—such as physical visits or unreliable word-of-mouth recommendations—to find suitable living spaces.

To address this critical gap, **Rent Near TU** is a web application meticulously designed to simplify and democratize the search for affordable dormitories near Thammasat University. Built on the robust **Django Web Framework**, the platform serves two primary user groups: **tenants** (primarily students and workers) and **landlords** (property owners and managers). It offers a suite of intuitive features, including budget-based search, advanced filtering by amenities and location, detailed dormitory listings with multimedia support, and a real-time management system that empowers landlords to post, update, and manage their properties efficiently.

Beyond its technological innovation, Rent Near TU is driven by a profound social mission to reduce disparities in dormitory access, particularly for resource-constrained individuals. By minimizing search-related costs, saving time, and providing transparent, reliable information, the platform promotes housing stability, supports educational and professional opportunities, and lays the foundation for a more equitable living environment. Its scalable design also holds promise for adaptation to other communities with similar demographic and housing challenges, making it a versatile solution with far-reaching potential.

## Core Technologies
- **Python, HTML, CSS**: Delivers a responsive, user-friendly interface optimized for both desktop and mobile devices.
- **Django Web Framework**: Provides a reliable backend for efficient data management and scalability.
- **django-widget-tweaks**: Enhances form customization for a seamless user experience.
- **django-allauth, social-auth-app-django**: Enables secure authentication with social media login integration.
- **djangorestframework, djangorestframework-simplejwt**: Supports secure REST API with JWT authentication for robust data exchange.
- **python-dotenv, python-dateutil**: Facilitates environment configuration and date management.
- **qrcode, libscrc**: Enables QR code generation for quick access to listings and secure booking confirmations.
- **gunicorn**: Ensures reliable deployment for production environments.

## Key Features
1. **Search and Filter System**: Allows users to locate dormitories based on budget, location, and amenities like air conditioning or Wi-Fi.
2. **Landlord Listing System**: Empowers landlords to create and manage property listings with ease.
3. **Dormitory Management**: Supports real-time addition, editing, or deletion of listings.
4. **Detailed Listings**: Provides comprehensive property details, including photos, videos, and rental conditions.
5. **Room Status**: Displays real-time availability (vacant or occupied).
6. **User Authentication**: Offers a secure sign-up and login system to access advanced features.
7. **Favorites List**: Enables tenants to save and compare preferred dormitories for informed decision-making.
8. **QR Code Booking**: Facilitates secure booking through QR code-based payment confirmation.

## Community Impact
Rent Near TU revolutionizes the dormitory search process by enabling tenants to explore options remotely, eliminating the need for costly and time-intensive physical visits. This is particularly impactful for students and low-income individuals who face financial and logistical constraints. By offering a centralized platform with robust filtering capabilities, tenants can efficiently compare dormitories based on price, amenities, and proximity to Thammasat University, ensuring they find accommodations that align with their needs and budgets. The inclusion of multimedia, such as photos

For landlords, Rent Near TU provides a powerful tool to showcase their properties comprehensively, reaching a targeted audience of prospective tenants directly. The platform’s real-time management features allow landlords to update listings instantly, ensuring accuracy and relevance, while the direct contact system streamlines communication, reducing intermediaries and associated costs. This creates a mutually beneficial ecosystem that promotes transparency, accessibility, and fairness in the dormitory market. By bridging the gap between tenants and landlords, Rent Near TU not only addresses immediate housing needs but also contributes to long-term community stability, supporting Thammasat University’s academic ecosystem and fostering equitable access to essential resources.

## User Stories

### Tenants
- **As a tenant**, I want to view detailed furniture information included with the room so that I can plan additional purchases effectively.
- **As a tenant**, I want to use the search and filter system to find dormitories based on criteria such as a budget of no more than 5,000 THB, air conditioning, fully furnished rooms, and proximity to the university.
### Landlords
- **As a landlord**, I want to specify room details such as size, furniture, and rental price so that tenants have comprehensive information before contacting me.

## Design and Prototyping
The design process for Rent Near TU prioritized user-centered design to deliver an intuitive and visually appealing experience. Key design assets include:

- **User Flow Diagram**: Mobile-optimized flows for tenant and landlord interactions. [View in Figma](https://www.figma.com/design/ucFm2O23q7mJ3CoAeuyKqi/Rent-near-TU).
- **Sitemap**: Logical navigation structure for efficient user journeys. [View in Figma](https://www.figma.com/design/ucFm2O23q7mJ3CoAeuyKqi/Rent-near-TU).
- **Wireframe and High-Fidelity Design**: Polished UI designs showcasing the app’s aesthetic and functionality. [View in Figma](https://www.figma.com/design/ucFm2O23q7mJ3CoAeuyKqi/Rent-near-TU).
- **Paper Prototype**: Low-fidelity prototype tested to validate user interactions, ensuring tasks are completed in under 30 seconds for optimal usability.
- **Design Specifications**:
  - **Color Theme**: Black and white for a clean, professional aesthetic.
  - **Font**: Inter, a modern typeface optimized for readability across devices.

## Future Enhancements
To further elevate Rent Near TU, the following features are planned to enhance functionality and inclusivity:
- **Advanced Filters**: Introduce filters for specialized needs, such as pet-friendly dormitories, accessibility features for individuals with disabilities, or eco-friendly accommodations, catering to a broader range of tenant preferences.
- **Rating System**: Implement a tenant-driven rating and review system to provide feedback on dormitories, fostering transparency, trust, and accountability within the platform.
- **Language Switching**: Develop a multilingual interface supporting languages such as Thai, English, and potentially others, ensuring accessibility for international students and diverse users.
- **Automatic Address Filling (Cascading Dropdowns)**: Integrate a dynamic address input system where selecting a province automatically populates a dropdown list of districts (amphoes) within that province, followed by sub-districts (tambons) if needed. This streamlines location entry for landlords and enhances search precision for tenants. For example, selecting "Pathum Thani" as the province would populate a dropdown with districts like "Mueang Pathum Thani" or "Khlong Luang," making the process intuitive and efficient.

## Setup Instructions

# Setup Instructions for Rent Near TU

1. **Clone the Repository**
   ```bash
   git clone https://github.com/xuli2317/dsi202_2025.git
   cd dsi202_2025
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**
   ```bash
   python manage.py migrate
   ```

4. **Create a Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

   Access the platform locally at `http://127.0.0.1:8000/`.


## Accessing the Web App
- **Home Page**: `http://localhost:8000/`
- **Admin Page**: `http://localhost:8000/admin/`

## YouTube
- https://youtu.be/qqsSpwAAaU4 (Short Demo)
- https://youtu.be/T3dwY4cetqM (All Features Demo)

## Conclusion
Rent Near TU represents a transformative step toward making dormitories more accessible, affordable, and equitable for the Thammasat University community and beyond. By leveraging user-focused technology and a commitment to social impact, the platform bridges the gap between tenants and landlords, fostering a transparent, efficient, and inclusive dormitory ecosystem that empowers users and supports long-term community development.
