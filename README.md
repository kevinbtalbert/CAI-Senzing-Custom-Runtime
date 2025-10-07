# CAI-Senzing-Custom-Runtime

A custom Cloudera ML Runtime with the Senzing SDK for entity resolution and data analysis.

## Overview

This Docker image extends the Cloudera ML Runtime with JupyterLab and Python 3.13, adding the complete Senzing SDK/API for entity resolution capabilities. The Senzing SDK is pre-configured with a project and ready to use for data loading, entity resolution, and analysis.

## Building the Docker Image

```bash
docker build -t senzing-ml-runtime:1.2 .
```

## What's Included

- **Senzing SDK POC v4.0.0**: Full installation of the Senzing entity resolution SDK
- **Pre-configured Project**: A Senzing project initialized at `/var/senzing/project` with proper permissions
- **Database Configuration**: SQLite database pre-configured and ready for immediate use
- **Environment Setup**: Senzing environment variables automatically configured for both interactive and non-interactive sessions
- **Python Support**: Includes `gnureadline` for interactive tools like `sz_explorer`
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

- The runtime includes 500 free source records for evaluation
- SQLite is used for evaluation; production systems should use PostgreSQL or other enterprise RDBMS
- Senzing Support is 100% FREE - contact them for assistance or additional evaluation records
