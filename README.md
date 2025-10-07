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
- **Pre-configured Project**: A Senzing project initialized at `/var/senzing/project` for testing (create persistent project at `~/senzing` for production use)
- **Database Configuration**: SQLite database ready for use with proper configuration
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

A comprehensive example file [`senzing_example.py`](senzing_example.py) demonstrates all major SDK features:

**Run the example:**
```bash
# After creating persistent project (see below)
cd ~/senzing
source setupEnv
python ~/senzing_example.py
```

**What the example covers:**
- ✅ Initializing the Senzing v4 SDK using `SzAbstractFactoryCore`
- ✅ Adding new records to the entity repository
- ✅ Retrieving entities by record ID with full details
- ✅ Searching for entities by attributes (name, DOB, etc.)
- ✅ Finding relationship paths between entities
- ✅ "Why" analysis - explaining entity resolution decisions
- ✅ Getting engine statistics

**Quick Python snippet:**
```python
from senzing import SzError
from senzing_core import SzAbstractFactoryCore
import json
import os

# Use persistent project in home directory
project_dir = os.path.expanduser('~/senzing')

# Configuration for your Senzing project
senzing_config = json.dumps({
    "PIPELINE": {
        "CONFIGPATH": f"{project_dir}/etc",
        "SUPPORTPATH": f"{project_dir}/data",
        "RESOURCEPATH": f"{project_dir}/resources"
    },
    "SQL": {
        "CONNECTION": f"sqlite3://na:na@{project_dir}/var/sqlite/G2C.db"
    }
})

# Initialize Senzing (after sourcing setupEnv)
# IMPORTANT: Keep sz_factory alive as long as you use sz_engine!
sz_factory = SzAbstractFactoryCore("MyApp", senzing_config)
sz_engine = sz_factory.create_engine()

# Get an entity by record ID
result = sz_engine.get_entity_by_record_id("CUSTOMERS", "1070")

# Parse and display the JSON result
entity = json.loads(result)
print(f"Entity ID: {entity['RESOLVED_ENTITY']['ENTITY_ID']}")
print(f"Entity Name: {entity['RESOLVED_ENTITY']['ENTITY_NAME']}")
```

> **⚠️ Important**: The `sz_factory` object must remain in scope for as long as you use the `sz_engine`. If the factory is destroyed, the engine becomes unusable.

## Getting Started with Sample Data

This section walks you through loading and exploring the Senzing demo truth set data. This is the best way to learn how Senzing performs entity resolution.

### 📋 Quick Reference

**First time setup** (do once):
```bash
/opt/senzing/er/bin/sz_create_project ~/senzing
cd ~/senzing && source setupEnv && ./bin/sz_setup_config
```

**Every session** (source environment):
```bash
cd ~/senzing && source setupEnv
```

**Data location**: `~/senzing/var/sqlite/G2C.db` ← persists across sessions

---

### 🚀 Complete Walkthrough: Setting Up Persistent Senzing

Follow these steps to create a production-ready Senzing setup that persists across sessions.

#### Step 0: Create a Persistent Senzing Project

⚠️ **Important**: The pre-configured project at `/var/senzing/project` is NOT persistent across sessions. Create your project in your home directory:

```bash
# Create a persistent Senzing project in your home directory
/opt/senzing/er/bin/sz_create_project ~/senzing
```

**Expected output:**
```
Senzing version: 4.0.0

Successfully created
```

#### Step 0.1: Initialize the Configuration

```bash
# Navigate to your new project
cd ~/senzing

# Source the environment variables
source setupEnv

# Set up the initial configuration (type 'y' when prompted for EULA)
./bin/sz_setup_config
```

**What this does:**
- Sets up environment variables (PYTHONPATH, PATH, etc.)
- Initializes the SQLite database at `~/senzing/var/sqlite/G2C.db`
- Registers the default Senzing configuration

✅ **Your project is now set up and will persist across sessions!**

**Verify your setup:**
```bash
# Check that the database exists
ls -lh ~/senzing/var/sqlite/G2C.db

# Test that tools are in your PATH
which sz_explorer

# Check PYTHONPATH includes Senzing
echo $PYTHONPATH | grep senzing
```

**For future sessions**, you only need:
```bash
cd ~/senzing && source setupEnv
```

---

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

Download the demo datasets to your home directory:

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

Before loading data, you need to register each data source in Senzing's configuration.

**Run these commands in your terminal:**

```bash
cd ~/senzing
source setupEnv
sz_configtool
```

**Inside the `sz_configtool` interactive prompt, type these commands ONE AT A TIME:**

> ⚠️ **Important**: Do NOT copy the `>` symbol - it represents the prompt. Only type the commands after it!

| Command to Type | What it Does |
|----------------|--------------|
| `addDataSource CUSTOMERS` | Adds CUSTOMERS as a data source |
| `addDataSource REFERENCE` | Adds REFERENCE as a data source |
| `addDataSource WATCHLIST` | Adds WATCHLIST as a data source |
| `save` | Saves the configuration (type `y` when prompted) |
| `quit` | Exits the configuration tool |

**Expected interaction:**
```
Type help or ? for help

(szcfg) addDataSource CUSTOMERS
Data source successfully added!

(szcfg) addDataSource REFERENCE
Data source successfully added!

(szcfg) addDataSource WATCHLIST
Data source successfully added!

(szcfg) save
WARNING: This will immediately update the current configuration...
Are you certain you wish to proceed and save changes? (y/n) y
Configuration changes saved

(szcfg) quit
```

✅ **Data sources are now configured and saved to your persistent database!**

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

**Expected output** (per file):
```
Processing customers.jsonl...
Records processed: 100... 200... 300...
Successfully loaded XXX records from customers.jsonl
```

✅ **All data is now loaded into your persistent SQLite database!**

**Verify the data:**
```bash
# Check database size (should be several MB now)
ls -lh ~/senzing/var/sqlite/G2C.db

# Quick test with sz_explorer
sz_explorer
```

In `sz_explorer`, try: `get CUSTOMERS 1070` to see a resolved entity.

### Step 4: Explore Entity Resolution Results

Launch the Senzing Explorer to see how entities were resolved:

```bash
sz_explorer
```

#### Example Queries in sz_explorer

> Do NOT copy the `(szeda)` prompt - it's shown for context only. Just type the commands!

**Try these commands ONE AT A TIME:**

| Command | What it Does |
|---------|-------------|
| `get CUSTOMERS 1070` | Shows all details for customer record 1070 |
| `search {"NAME_FULL": "Robert Smith", "DATE_OF_BIRTH": "1978-12-11"}` | Search for entities by attributes |
| `why CUSTOMERS 1001 CUSTOMERS 1002` | Explains why two records were/weren't matched |
| `help` | Lists all available commands |
| `quit` | Exits sz_explorer |

**What you'll see:**
- Entity details with all resolved records
- Name variations and features (DOB, address, IDs)
- Data merged from multiple sources
- Relationships to other entities

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

### Step 5: Run the Python Example

Now that your persistent project is set up with data, run the comprehensive Python example:

```bash
cd ~/senzing
source setupEnv
python ~/senzing_example.py
```

**What the example demonstrates:**
1. ✅ Adding a new record (NEW_001 - Jane Smith)
2. ✅ Retrieving entity for CUSTOMERS 1070 (with all resolved records)
3. ✅ Searching for entities by attributes
4. ✅ Finding relationship paths between entities
5. ✅ Explaining why records did/didn't resolve together
6. ✅ Getting engine statistics

The example will show full results now that you have data loaded!

---

## Next Steps

You now have a fully functional, persistent Senzing environment! Here's what to try next:

1. **Load your own data** - Follow the [Entity Specification](https://senzing.com/docs/entity-spec/) to map your data
2. **Build applications** - Use the Python SDK to build entity resolution into your applications
3. **Explore the API** - Check out the [Python SDK Reference](https://senzing.com/docs/python/index.html)
4. **Production database** - For production, migrate from SQLite to PostgreSQL or MySQL

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

The following Senzing-related environment variables are configured when you source setupEnv:

- `SENZING_PROJECT_DIR` - Points to your project directory (e.g., `~/senzing`)
- `PYTHONPATH` - Includes `/opt/senzing/er/sdk/python` and project SDK path
- `PATH` - Includes `${SENZING_PROJECT_DIR}/bin` for Senzing CLI tools
- Database connection and configuration paths from your project's setupEnv

## Project Structure

A Senzing project (whether at `/var/senzing/project` or `~/senzing`) has this structure:

```
~/senzing/  (or your project directory)
├── bin/              # Senzing command-line tools
├── data/             # Configuration data
├── etc/              # Additional configuration
├── lib/              # Libraries
├── resources/        # Resource files
├── sdk/              # SDK files
├── setupEnv          # Environment setup script (source this!)
└── var/              # Database and runtime data (persists if in ~/senzing)
    └── sqlite/
        └── G2C.db    # SQLite database
```

**Storage Locations:**
- `/var/senzing/project` - Pre-configured for testing, **NOT persistent** across sessions
- `~/senzing` - Recommended for production use, **persists** across Cloudera ML sessions
