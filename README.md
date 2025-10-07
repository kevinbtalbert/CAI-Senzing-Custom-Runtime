# CAI Senzing Custom Runtime

A custom Cloudera ML Runtime with the Senzing SDK for entity resolution and data analysis.

## Overview

This Docker image extends the Cloudera ML Runtime with JupyterLab and Python 3.13, adding the complete Senzing SDK/API for entity resolution capabilities. The Senzing SDK is pre-configured with a project and ready to use for data loading, entity resolution, and analysis.

## Building the Docker Image

```bash
docker build -t senzing-ml-runtime:1.3 .
```

## Use the Pre-Built Docker Image

If you don't want to build from source, use the pre-built image from Docker Hub:

```bash
docker pull docker.io/kevintalbert/caisenzingcustomruntime:latest
```

Use in Cloudera ML:
```
docker.io/kevintalbert/caisenzingcustomruntime:latest
```

## What's Included

- **Senzing SDK POC v4.0.0**: Full installation of the Senzing entity resolution SDK
- **Pre-configured Project**: A Senzing project initialized at `/var/senzing/project` with proper permissions
- **Database Configuration**: SQLite database pre-configured and ready for immediate use
- **Environment Setup**: Senzing environment variables automatically configured for both interactive and non-interactive sessions
- **Python Support**: Includes `gnureadline` and `prettytable` for interactive tools like `sz_explorer`
- **MCP Integration**: Model Context Protocol support for AI agent integration

## Using Senzing in the Runtime

The Senzing environment is automatically configured. You can use Senzing tools and APIs immediately:

### Command-line Tools

```bash
# Load data files
sz_file_loader -f your_data.jsonl

# Explore entities
sz_explorer

# Configure data sources
sz_configtool
```

### Python SDK

```python
# Example: Using Senzing in Python
from senzing import SzEngine, SzConfig

# The environment is already configured, start using the SDK
engine = SzEngine()
# ... your entity resolution code ...
```

## Getting Started with Sample Data

This section walks you through loading and exploring the Senzing demo truth set data. This is the best way to learn how Senzing performs entity resolution.

### Understanding the Truth Set Files

The demo truth set includes three types of data files, each serving a distinct purpose:

#### 1. **Customers Dataset**
Represents your subjects of interest - in this case, customer records. These could easily be:
- Employees for insider threat detection
- Vendors for supply chain management  
- Patients for healthcare analytics
- Any other entities you need to track and resolve

This forms the core dataset you aim to analyze and resolve.

#### 2. **Watchlist Dataset**
Contains entities you want to flag or avoid due to potential risks:
- Past fraudsters
- Known terrorists or money launderers
- Entities on mandated exclusion lists (e.g., OFAC sanctions)

By integrating watchlist data, Senzing helps you:
- Identify high-risk entities by matching them against your records
- Enable risk assessment and compliance monitoring
- Mitigate threats like fraud, regulatory non-compliance, or reputational damage

#### 3. **Reference Dataset**
Supplemental data purchased or acquired about individuals or companies:
- **Individuals**: Demographics, past addresses, contact methods
- **Companies**: Firmographics, corporate structure, executives, ownership

This enrichment data provides:
- Additional context for better entity resolution
- Historical tracking (e.g., address changes over time)
- Relationship mapping (e.g., corporate hierarchies, beneficial ownership)

### Step 1: Download the Sample Files

Open a terminal in your Cloudera ML session and navigate to your workspace:

```bash
cd ~/
mkdir -p senzing-demo
cd senzing-demo

# Download the three demo datasets
wget https://raw.githubusercontent.com/Senzing/truth-sets/main/truthsets/demo/customers.jsonl
wget https://raw.githubusercontent.com/Senzing/truth-sets/main/truthsets/demo/reference.jsonl
wget https://raw.githubusercontent.com/Senzing/truth-sets/main/truthsets/demo/watchlist.jsonl
```

### Step 2: Configure Data Sources

Before loading data, you need to register each data source in Senzing's configuration:

```bash
# Navigate to the Senzing project
cd /var/senzing/project

# Source the environment
source setupEnv

# Launch the configuration tool
sz_configtool
```

In the `sz_configtool` interactive prompt, add each data source:

```
Type help or ? for help

> addDataSource CUSTOMERS
Data source successfully added!

> addDataSource REFERENCE
Data source successfully added!

> addDataSource WATCHLIST
Data source successfully added!

> save
WARNING: This will immediately update the current configuration in the Senzing repository with the current configuration!

Are you certain you wish to proceed and save changes? (y/n) y
Configuration changes saved

> quit
```

### Step 3: Load the Data Files

Now load each dataset into Senzing:

```bash
cd ~/senzing-demo

# Load customers (subject records)
sz_file_loader -f customers.jsonl

# Load reference data (enrichment)
sz_file_loader -f reference.jsonl

# Load watchlist (risk entities)
sz_file_loader -f watchlist.jsonl
```

As files load, you'll see progress indicators and statistics about records processed.

### Step 4: Explore Entity Resolution Results

Launch the Senzing Explorer to see how entities were resolved:

```bash
sz_explorer
```

#### Example Queries

Try these commands in `sz_explorer`:

**Get a specific entity:**
```
(szeda) get CUSTOMERS 1070
```

This will show you entity details including:
- All records that resolved to this entity
- Features (name, DOB, address, identifiers)
- Data from multiple sources
- Relationships to other entities

**Search by attributes:**
```
(szeda) search {"NAME_FULL": "Robert Smith", "DATE_OF_BIRTH": "1978-12-11"}
```

**Find possible relationships:**
```
(szeda) why CUSTOMERS 1001 CUSTOMERS 1002
```

Shows why two records were (or weren't) resolved together.

**Exit the explorer:**
```
(szeda) quit
```

### Example Output

When you query an entity (e.g., `get CUSTOMERS 1070`), you'll see output like:

```
Entity summary for entity 98: Jie Wang
┼───────────┼────────────────────────────────────────┼─────────────────┼
│ Sources   │ Features                               │ Additional Data │
┼───────────┼────────────────────────────────────────┼─────────────────┼
│ CUSTOMERS │ NAME: Jie Wang (PRIMARY)               │ AMOUNT: 100     │
│ 1069      │ NAME: 王杰 (NATIVE)                    │ AMOUNT: 200     │
│ 1070      │ DOB: 9/14/93                           │ DATE: 1/26/18   │
│           │ GENDER: Male                           │ DATE: 1/27/18   │
│           │ ADDRESS: 12 Constitution Street (HOME) │ STATUS: Active  │
│           │ NATIONAL_ID: 832721 Hong Kong          │                 │
┼───────────┼────────────────────────────────────────┼─────────────────┼
│ REFERENCE │ NAME: Wang Jie (PRIMARY)               │ CATEGORY: Owner │
│ 2013      │ DOB: 1993-09-14                        │ STATUS: Current │
│           │ RECORD_TYPE: PERSON                    │                 │
│           │ REL_POINTER: 2011 (OWNS 60%)           │                 │
┼───────────┼────────────────────────────────────────┼─────────────────┼
```

This shows:
- **Multiple records** (1069, 1070 from CUSTOMERS and 2013 from REFERENCE) resolved to one entity
- **Name variations** (Jie Wang, Wang Jie, 王杰)
- **Enrichment data** from reference source showing business ownership
- **Disclosed relationships** to other entities

### What Just Happened?

Senzing automatically:
1. ✅ **Matched records** across different data sources based on features (name, DOB, address, etc.)
2. ✅ **Resolved entities** by determining which records represent the same real-world person or organization
3. ✅ **Enriched data** by combining information from all sources
4. ✅ **Identified relationships** between entities (e.g., ownership, addresses)
5. ✅ **Flagged risks** by matching against watchlist data

All of this happened **automatically** without writing any custom matching rules!

## Documentation

- [Senzing Quickstart Guide](https://senzing.com/docs/quickstart/quickstart_api/)
- [Senzing Python SDK Reference](https://senzing.com/docs/python/index.html)
- [Entity Specification](https://senzing.com/docs/entity-spec/)

## Key Features

- **Automated EULA Acceptance**: Environment variables handle license agreement automatically during build
- **Proper Permissions**: All project files are accessible to non-root users (cdsw user)
- **PYTHONPATH Management**: Intelligently preserves and extends existing PYTHONPATH from base image
- **Verbose Build Logging**: Enhanced build output for troubleshooting
- **Interactive Tool Support**: Full readline support for `sz_explorer` and other CLI tools
- **Version Management**: Runtime version automatically derived from SHORT and MAINTENANCE versions

## Environment Variables

The following Senzing-related environment variables are automatically configured:

- `SENZING_PROJECT_DIR=/var/senzing/project`
- `PYTHONPATH` includes `/opt/senzing/er/sdk/python`
- `PATH` includes `${SENZING_PROJECT_DIR}/bin`

## Project Structure

```
/var/senzing/project/
├── bin/              # Senzing command-line tools
├── data/             # Configuration data
├── etc/              # Additional configuration
├── lib/              # Libraries
├── resources/        # Resource files
├── sdk/              # SDK files
├── setupEnv          # Environment setup script
└── var/              # Database and runtime data (writable)
```

## Notes

- **Evaluation Limits**: The runtime includes 500 free source records for evaluation
- **Database**: SQLite is used for evaluation; production systems should use PostgreSQL, MySQL, or other enterprise RDBMS
- **Support**: Senzing Support is 100% FREE - contact them for assistance or additional evaluation records
- **Runtime Version**: Currently v1.3 with all dependencies for interactive tools pre-installed

