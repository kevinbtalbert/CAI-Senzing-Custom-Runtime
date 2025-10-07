FROM docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-pbj-jupyterlab-python3.13-standard:2025.09.1-b5

# Add the packages you want to include in this runtime
# Install Senzing SDK following official documentation

ENV SENZING_EULA_ACCEPTED="I_ACCEPT_THE_SENZING_EULA"
ENV SENZING_ACCEPT_EULA="I_ACCEPT_THE_SENZING_EULA"

RUN set -x && \
    apt-get update && \
    apt-get install -y apt-transport-https wget libreadline-dev && \
    wget --verbose https://senzing-production-apt.s3.amazonaws.com/senzingrepo_2.0.1-1_all.deb && \
    apt-get install -y ./senzingrepo_2.0.1-1_all.deb && \
    rm -v senzingrepo_2.0.1-1_all.deb && \
    apt-get update && \
    yes y | DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get install -y senzingsdk-poc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create Senzing project and set up configuration
# Create parent directory only - sz_create_project will create the project directory
RUN set -x && \
    mkdir -p /var/senzing && \
    /opt/senzing/er/bin/sz_create_project /var/senzing/project && \
    cd /var/senzing/project && \
    ls -la && \
    . ./setupEnv && \
    yes | ./bin/sz_setup_config && \
    chmod -R a+rX /var/senzing/project && \
    chmod -R a+w /var/senzing/project/var

# Set Senzing environment variables
ENV SENZING_PROJECT_DIR="/var/senzing/project"
ENV PATH="${SENZING_PROJECT_DIR}/bin:${PATH}"

# Add Senzing Python SDK to PYTHONPATH (set at build time for non-interactive processes)
ENV PYTHONPATH="/opt/senzing/er/sdk/python:${PYTHONPATH}"

# Configure Senzing environment for interactive shell sessions
RUN { \
        echo '# Source Senzing project setup if available'; \
        echo 'if [ -f ${SENZING_PROJECT_DIR}/setupEnv ]; then'; \
        echo '    . ${SENZING_PROJECT_DIR}/setupEnv'; \
        echo 'fi'; \
        echo ''; \
        echo '# Prepend Senzing Python SDK to PYTHONPATH, preserving existing paths'; \
        echo 'if [ -n "$PYTHONPATH" ]; then'; \
        echo '    export PYTHONPATH="/opt/senzing/er/sdk/python:$PYTHONPATH"'; \
        echo 'else'; \
        echo '    export PYTHONPATH="/opt/senzing/er/sdk/python"'; \
        echo 'fi'; \
    } > /etc/profile.d/senzing.sh && \
    chmod +x /etc/profile.d/senzing.sh

# Install Python dependencies
# - gnureadline: Provides readline support for sz_explorer and other interactive tools
# - prettytable: Required for sz_explorer table formatting
# - mcp: Model Context Protocol for future use
RUN pip install gnureadline prettytable mcp>=0.9.0

# Override Runtime label and environment variables metadata
ENV ML_RUNTIME_EDITION="JupyterLab with Senzing SDK" \
    ML_RUNTIME_EDITOR="JupyterLab" \
    ML_RUNTIME_SHORT_VERSION="1" \
    ML_RUNTIME_MAINTENANCE_VERSION="3" \
    ML_RUNTIME_DESCRIPTION="JupyterLab Runtime with Senzing SDK"

ENV ML_RUNTIME_FULL_VERSION="${ML_RUNTIME_SHORT_VERSION}.${ML_RUNTIME_MAINTENANCE_VERSION}"


LABEL com.cloudera.ml.runtime.edition=$ML_RUNTIME_EDITION \
    com.cloudera.ml.runtime.full-version=$ML_RUNTIME_FULL_VERSION \
    com.cloudera.ml.runtime.short-version=$ML_RUNTIME_SHORT_VERSION \
    com.cloudera.ml.runtime.maintenance-version=$ML_RUNTIME_MAINTENANCE_VERSION \
    com.cloudera.ml.runtime.description=$ML_RUNTIME_DESCRIPTION \
    com.cloudera.ml.runtime.editor=$ML_RUNTIME_EDITOR

