# Fashion Data ETL Pipeline

[![Python 3.12.9](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![SOLID](https://img.shields.io/badge/SOLID-principles-orange)](https://en.wikipedia.org/wiki/SOLID)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust ETL (Extract, Transform, Load) pipeline for processing fashion product data from [Fashion Studio Dicoding](https://fashion-studio.dicoding.dev/). This project demonstrates a comprehensive implementation of SOLID design principles to create a maintainable and scalable data processing solution.

## 📋 Overview

This pipeline extracts fashion product data from a web source, transforms it into a structured format suitable for analysis, and loads the processed data into three distinct storage destinations:

- **CSV File** - Local storage for quick analysis and import to other systems
- **PostgreSQL Database** - Structured storage for advanced querying and data management
- **Google Spreadsheet** - Cloud-based collaborative access

This architecture follows industry best practices for data engineering, making it adaptable for various business analytics needs.

---

## 🧩 Features

### 🔍 Extract

Efficiently extracts product data from web pages with:

- HTTP content fetching with error handling and retries
- HTML parsing with BeautifulSoup
- Concurrent scraping capability with rate limiting

### 🔧 Transform

Performs comprehensive data cleaning and transformation:

- **Data Validation**: Filters out invalid entries
- **Currency Conversion**: Converts prices from USD to IDR (exchange rate: 16,000)
- **Data Type Conversion**: Ensures appropriate data types across columns:
  - `Price` → float (IDR value)
  - `Rating` → float (normalized ratings)
  - `Colors` → integer (number of color options)
  - `Size` → string (standardized size format)
  - `Gender` → string (categorized gender)
- **Timestamp Management**: ISO format timestamps for tracking data lineage

### 💾 Load

Multi-destination loading with configuration flexibility:

- **CSV Storage**: Configurable file path and formatting options
- **PostgreSQL Integration**: Transaction-safe database operations with SQLAlchemy
- **Google Sheets API**: Automated spreadsheet updates with authentication handling

---

## 📁 Project Structure

```
├── docker-compose.yml         # Docker configuration for PostgreSQL
├── fashion_data.csv           # Generated output data
├── google-sheets-api.json     # Google API credentials
├── main.py                    # Main ETL pipeline orchestration
├── Makefile                   # Build and execution automation
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── htmlcov/                   # Test coverage reports
├── migrations/                # Database schema definitions
│   └── init_database.sql      # PostgreSQL initialization script
├── postgres_data/             # Docker volume for database persistence
├── screenshoot
│   ├── postgres.png           # Database visualization
│   ├── spreadsheet.png        # Google Sheets results
│   └── test.png               # Test results screenshot
├── tests/                     # Test suite directory
│   ├── test_extract.py        # Extraction tests
│   ├── test_load.py           # Loading tests
│   ├── test_main.py           # Main pipeline tests
│   └── test_transform.py      # Transformation tests
└── utils/                     # Core functionality modules
    ├── config.py              # Configuration management
    ├── extract.py             # Data extraction module
    ├── interfaces.py          # Interface definitions (SOLID)
    ├── load.py                # Data loading module
    └── transform.py           # Data transformation module
```

---

## ⚙️ Technology Stack

| Category              | Technologies                       |
| --------------------- | ---------------------------------- |
| **Core Language**     | Python 3.12.9                      |
| **Web Scraping**      | Requests 2.32, BeautifulSoup4 4.12 |
| **Data Processing**   | Pandas 2.2                         |
| **Database**          | PostgreSQL 15, SQLAlchemy 2.0      |
| **Cloud Integration** | Google API Client 2.152            |
| **DevOps**            | Docker, Docker Compose             |
| **Testing**           | Pytest 8.4.1, pytest-cov 6.0       |
| **Configuration**     | python-dotenv 1.0                  |
| **Automation**        | Make, Python-crontab 3.2           |

## 📤 Output Destinations

| Destination            | Details                                                                                                                         | Access           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| **CSV File**           | `fashion_data.csv`                                                                                                              | Local filesystem |
| **PostgreSQL**         | Database: `fashion_db`<br>Table: `fashion_products`                                                                             | localhost:5432   |
| **Google Spreadsheet** | [Fashion Data Processing](https://docs.google.com/spreadsheets/d/1bZOhgq65Tqkw-rIBBQTcHNMnGeW2tYQ7A-nMpXe-Lt0/edit?gid=0#gid=0) | View in browser  |

---

## � Pipeline Execution Sample

```bash
Starting data extraction process...
Scraping page: https://fashion-studio.dicoding.dev/
# ... [Scraping pages 2-49] ...
Scraping page: https://fashion-studio.dicoding.dev/page50
Extraction completed. Number of records: 1000

=======Data Information Before Transformation:=======
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1000 entries, 0 to 999
Data columns (total 7 columns):
 #   Column     Non-Null Count  Dtype
---  ------     --------------  -----
 0   Title      1000 non-null   object
 1   Price      1000 non-null   object
 2   Rating     1000 non-null   object
 3   Colors     1000 non-null   object
 4   Size       1000 non-null   object
 5   Gender     1000 non-null   object
 6   Timestamp  1000 non-null   datetime64[ns]
dtypes: datetime64[ns](1), object(6)
memory usage: 54.8+ KB

=======Data Head Before Transformation:=======
             Title    Price          Rating Colors Size  Gender                  Timestamp
0  Unknown Product  $100.00  Invalid Rating      5    M     Men 2025-06-29 22:18:20.739984
1        T-shirt 2  $102.15           ⭐ 3.9      3    M   Women 2025-06-29 22:18:20.740125
2         Hoodie 3  $496.88           ⭐ 4.8      3    L  Unisex 2025-06-29 22:18:20.740239
3          Pants 4  $467.31           ⭐ 3.3      3   XL     Men 2025-06-29 22:18:20.740444
4      Outerwear 5  $321.59           ⭐ 3.5      3  XXL   Women 2025-06-29 22:18:20.740517

Starting data transformation process...
Transformation completed. Number of records after cleaning: 867

=======Data Information After Transformation:=======
<class 'pandas.core.frame.DataFrame'>
Index: 867 entries, 1 to 999
Data columns (total 7 columns):
 #   Column     Non-Null Count  Dtype
---  ------     --------------  -----
 0   Title      867 non-null    object
 1   Price      867 non-null    float64
 2   Rating     867 non-null    float64
 3   Colors     867 non-null    int64
 4   Size       867 non-null    object
 5   Gender     867 non-null    object
 6   Timestamp  867 non-null    object
dtypes: float64(2), int64(1), object(4)
memory usage: 54.2+ KB

=======Data Head After Transformation:=======
         Title      Price  Rating  Colors Size  Gender                   Timestamp
1    T-shirt 2  1634400.0     3.9       3    M   Women  2025-06-29T22:18:20.740125
2     Hoodie 3  7950080.0     4.8       3    L  Unisex  2025-06-29T22:18:20.740239
3      Pants 4  7476960.0     3.3       3   XL     Men  2025-06-29T22:18:20.740444
4  Outerwear 5  5145440.0     3.5       3  XXL   Women  2025-06-29T22:18:20.740517
5     Jacket 6  2453920.0     3.3       3    S  Unisex  2025-06-29T22:18:20.740583

Starting data loading process to storage (CSV, PostgreSQL, Google Sheets)...
[Flatfile-.CSV] Data successfully saved to fashion_data.csv
[PostgreSQL] Data successfully saved to table fashion_products.
[Google Sheets] Data successfully saved to Spreadsheet (Fashion Data Processing).
Loading completed. 3/3 destinations successful.
  ✓ csv
  ✓ postgresql
  ✓ google_sheets

ETL process completed successfully.
```

## 📊 Test Coverage

Comprehensive test suite covering 95% of the codebase with 44 individual tests:

| File                    | Statements | Missing | Coverage |
| ----------------------- | ---------- | ------- | -------- |
| tests/test_extract.py   | 104        | 1       | 99%      |
| tests/test_load.py      | 63         | 0       | 100%     |
| tests/test_main.py      | -          | -       | 100%     |
| tests/test_transform.py | 27         | 0       | 100%     |
| utils/extract.py        | 67         | 13      | 81%      |
| utils/load.py           | 32         | 0       | 100%     |
| utils/transform.py      | 17         | 0       | 100%     |
| **Total**               | **310**    | **14**  | **95%**  |

## 🚀 Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/farismnrr/membangun_etl_pipeline_sederhana.git
   cd membangun_etl_pipeline_sederhana
   ```

2. **Set up virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   # Create .env file with database credentials
   cat > .env << EOL
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=fashion_db
   POSTGRES_HOST=localhost
   EOL
   ```

5. **Start PostgreSQL database**:

   ```bash
   make migrate
   ```

6. **Place Google API credentials**:
   - Save your Google Sheets API credentials as `google-sheets-api.json` in the project root

## 🏃 Running the Pipeline

```bash
# Run the complete ETL pipeline
make app

# Run tests
make test

# Generate test coverage report
make report
```

## 🏗️ Architecture

The project follows SOLID design principles to ensure maintainability and extensibility:

- **Single Responsibility**: Each class has a single responsibility
- **Open/Closed**: Components are open for extension but closed for modification
- **Liskov Substitution**: Implementation classes adhere to their interfaces
- **Interface Segregation**: Interfaces are focused on specific functionality
- **Dependency Inversion**: High-level modules depend on abstractions

The architecture implements a modular approach through interface-based design:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Extract   │────▶│  Transform  │────▶│    Load     │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                  │
      ▼                    ▼                  ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Interfaces  │     │ Interfaces  │     │ Interfaces  │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                  │
      ▼                    ▼                  ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│Implementations│    │Implementations│    │   Storage   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 👨‍💻 Author

**Faris Munir Mahdi**

- GitHub: [farismnrr](https://github.com/farismnrr)

## 📄 License

This project is open-sourced under the MIT License.
