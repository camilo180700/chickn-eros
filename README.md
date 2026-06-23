# CHICANEROS Sales Tracker

A lightweight sales management application built with Python and Streamlit for tracking transactions, monitoring business performance, and generating real-time sales insights.

## Overview

CHICANEROS Sales Tracker was developed to help a small food business move away from manual sales tracking and gain visibility into daily operations through a simple web-based interface.

The application integrates directly with Google Sheets, allowing data to be stored in the cloud while providing an easy-to-use dashboard for business monitoring.

## Features

### Sales Registration

* Register new sales transactions
* Automatic date and time tracking
* Product categorization
* Revenue calculation

### Sales History

* View all recorded transactions
* Filter by date
* Remove incorrect entries

### Business Dashboard

* Total revenue tracking
* Number of transactions
* Active sales days
* Best-selling products
* Revenue by category
* Daily sales charts

## Technology Stack

* Python
* Streamlit
* Pandas
* Google Sheets API
* Google OAuth2 Service Account
* GSpread

## Project Structure

```bash
app.py
├── Google Sheets Integration
├── Sales Registration
├── Sales History
└── Business Analytics Dashboard
```

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/chicaneros-sales-tracker.git
cd chicaneros-sales-tracker
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Google Credentials

Create a Streamlit secrets file:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "your-private-key"
client_email = "your-client-email"
client_id = "your-client-id"
```

### Run Application

```bash
streamlit run app.py
```

## Future Improvements

* Authentication and user roles
* Inventory management
* Sales forecasting
* Profitability analysis
* Export reports to Excel/PDF
* Mobile-first interface
* Multi-location support

## Business Impact

This project demonstrates how a simple data-driven solution can help small businesses improve operational efficiency, centralize information, and gain actionable insights without investing in expensive software.

## Author

Camilo Esteban Mantilla Avendaño

Senior Executive, Ad Operations

Passionate about analytics, automation, and building practical solutions that create measurable business value.
