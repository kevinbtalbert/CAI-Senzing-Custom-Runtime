#!/usr/bin/env python3
"""
Senzing SDK Python Example
==========================

This script demonstrates how to use the Senzing Python SDK for entity resolution.

Prerequisites:
1. Create a persistent Senzing project (to keep data between sessions):
   /opt/senzing/er/bin/sz_create_project ~/senzing
   cd ~/senzing && source setupEnv && ./bin/sz_setup_config

2. Configure data sources (run sz_configtool and add CUSTOMERS, REFERENCE, WATCHLIST)

3. Load sample data:
   cd ~/senzing-demo
   sz_file_loader -f customers.jsonl
   sz_file_loader -f reference.jsonl
   sz_file_loader -f watchlist.jsonl

See README.md "Getting Started with Sample Data" section for detailed instructions.

Usage:
    cd ~/senzing
    source setupEnv
    SENZING_PROJECT_DIR=~/senzing python ~/senzing_example.py
    
Note: The setupEnv script may override SENZING_PROJECT_DIR. Explicitly set it
      to ~/senzing (as shown above) to ensure the script uses your persistent project.
"""

import json
import sys
import os

# Import Senzing SDK
try:
    from senzing import SzError
    from senzing_core import SzAbstractFactoryCore
except ImportError as e:
    print(f"Error importing Senzing SDK: {e}")
    print("\nMake sure:")
    print("1. You have sourced setupEnv: source /var/senzing/project/setupEnv")
    print("2. PYTHONPATH includes Senzing SDK: echo $PYTHONPATH")
    sys.exit(1)


def initialize_senzing():
    """
    Initialize the Senzing SDK using the factory pattern.
    
    Returns:
        tuple: (sz_factory, sz_engine) - Both must be kept alive
    """
    print("Initializing Senzing SDK...")
    
    # Get project directory from environment or use default
    # Default to ~/senzing for persistent storage across sessions
    default_project = os.path.expanduser('~/senzing')
    project_dir = os.environ.get('SENZING_PROJECT_DIR', default_project)
    
    # Configuration JSON for Senzing engine
    senzing_engine_configuration_json = json.dumps({
        "PIPELINE": {
            "CONFIGPATH": f"{project_dir}/etc",
            "SUPPORTPATH": f"{project_dir}/data",
            "RESOURCEPATH": f"{project_dir}/resources"
        },
        "SQL": {
            "CONNECTION": f"sqlite3://na:na@{project_dir}/var/sqlite/G2C.db"
        }
    })
    
    try:
        # Create Senzing factory with configuration
        # IMPORTANT: Must keep factory alive as long as engine is in use
        sz_factory = SzAbstractFactoryCore("SenzingExample", senzing_engine_configuration_json)
        
        # Create engine instance
        sz_engine = sz_factory.create_engine()
        
        print(f"✓ Senzing SDK initialized successfully")
        print(f"  Project directory: {project_dir}\n")
        
        # Return both factory and engine - factory must stay alive!
        return sz_factory, sz_engine
        
    except SzError as err:
        print(f"✗ Error initializing Senzing: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"✗ Error initializing Senzing: {err}")
        print("  Make sure you have sourced setupEnv: source /var/senzing/project/setupEnv")
        sys.exit(1)


def add_new_record(sz_engine):
    """
    Example: Add a new record to Senzing.
    
    Args:
        sz_engine: Initialized SzEngine instance
    """
    print("=" * 60)
    print("EXAMPLE 1: Adding a New Record")
    print("=" * 60)
    
    # Create a new record in Senzing's JSON format
    new_record = {
        "DATA_SOURCE": "CUSTOMERS",
        "RECORD_ID": "NEW_001",
        "RECORD_TYPE": "PERSON",
        "PRIMARY_NAME_LAST": "Smith",
        "PRIMARY_NAME_FIRST": "Jane",
        "DATE_OF_BIRTH": "1985-03-15",
        "ADDR_LINE1": "123 Main Street",
        "ADDR_CITY": "Las Vegas",
        "ADDR_STATE": "NV",
        "ADDR_POSTAL_CODE": "89101",
        "PHONE_NUMBER": "702-555-1234",
        "EMAIL_ADDRESS": "jane.smith@example.com"
    }
    
    try:
        # Convert to JSON string
        record_json = json.dumps(new_record)
        
        # Add the record (simple API without flags)
        sz_engine.add_record(
            new_record["DATA_SOURCE"],
            new_record["RECORD_ID"],
            record_json
        )
        
        print(f"✓ Record added successfully!")
        print(f"  Data Source: {new_record['DATA_SOURCE']}")
        print(f"  Record ID: {new_record['RECORD_ID']}")
        print()
        
    except SzError as err:
        print(f"✗ Error adding record: {err}\n")


def get_entity_by_record(sz_engine, data_source, record_id):
    """
    Example: Retrieve an entity by its source record.
    
    Args:
        sz_engine: Initialized SzEngine instance
        data_source: Data source code (e.g., "CUSTOMERS")
        record_id: Record ID within the data source
    """
    print("=" * 60)
    print(f"EXAMPLE 2: Getting Entity for {data_source} {record_id}")
    print("=" * 60)
    
    try:
        # Get entity by record ID (simple API)
        result = sz_engine.get_entity_by_record_id(data_source, record_id)
        
        entity = json.loads(result)
        resolved_entity = entity.get("RESOLVED_ENTITY", {})
        
        print(f"✓ Entity found!")
        print(f"  Entity ID: {resolved_entity.get('ENTITY_ID')}")
        print(f"  Entity Name: {resolved_entity.get('ENTITY_NAME')}")
        
        # Show all records that resolved to this entity
        records = resolved_entity.get("RECORDS", [])
        print(f"  Total Records: {len(records)}")
        for record in records:
            print(f"    - {record.get('DATA_SOURCE')}: {record.get('RECORD_ID')}")
        
        # Show related entities (if any)
        related = entity.get("RELATED_ENTITIES", [])
        if related:
            print(f"  Related Entities: {len(related)}")
            for rel in related[:3]:  # Show first 3
                print(f"    - Entity {rel.get('ENTITY_ID')}: {rel.get('ENTITY_NAME')} "
                      f"({rel.get('MATCH_LEVEL_CODE')})")
        
        print()
        return entity
        
    except SzError as err:
        print(f"✗ Error getting entity: {err}\n")
        return None


def search_by_attributes(sz_engine):
    """
    Example: Search for entities by attributes.
    
    Args:
        sz_engine: Initialized SzEngine instance
    """
    print("=" * 60)
    print("EXAMPLE 3: Searching by Attributes")
    print("=" * 60)
    
    # Search criteria
    search_attributes = {
        "NAME_FULL": "Robert Smith",
        "DATE_OF_BIRTH": "1978-12-11"
    }
    
    try:
        search_json = json.dumps(search_attributes)
        
        # Search by attributes (simple API)
        result = sz_engine.search_by_attributes(search_json)
        
        search_result = json.loads(result)
        entities = search_result.get("RESOLVED_ENTITIES", [])
        
        print(f"✓ Search completed!")
        print(f"  Search criteria: {search_attributes}")
        print(f"  Entities found: {len(entities)}")
        
        for i, entity in enumerate(entities[:5], 1):  # Show first 5
            print(f"\n  Result {i}:")
            print(f"    Entity ID: {entity.get('ENTITY_ID')}")
            print(f"    Entity Name: {entity.get('ENTITY_NAME')}")
            print(f"    Match Score: {entity.get('MATCH_SCORE', 'N/A')}")
            
            # Show some features
            features = entity.get("FEATURES", {})
            if features:
                print(f"    Features:")
                if "NAME" in features:
                    for name in features["NAME"][:2]:
                        print(f"      - Name: {name.get('FEAT_DESC')}")
        
        print()
        
    except SzError as err:
        print(f"✗ Error searching: {err}\n")


def find_path_between_entities(sz_engine, entity_id_1, entity_id_2):
    """
    Example: Find relationship path between two entities.
    
    Args:
        sz_engine: Initialized SzEngine instance
        entity_id_1: First entity ID
        entity_id_2: Second entity ID
    """
    print("=" * 60)
    print(f"EXAMPLE 4: Finding Path Between Entities {entity_id_1} and {entity_id_2}")
    print("=" * 60)
    
    try:
        # Find path between entities (simple API)
        result = sz_engine.find_path_by_entity_id(entity_id_1, entity_id_2, 3)
        
        path_result = json.loads(result)
        entities = path_result.get("ENTITIES", [])
        
        print(f"✓ Path analysis completed!")
        
        if entities:
            print(f"  Path found with {len(entities)} entities:")
            for i, entity in enumerate(entities):
                print(f"    {i+1}. Entity {entity.get('ENTITY_ID')}: {entity.get('ENTITY_NAME')}")
        else:
            print("  No path found between these entities")
        
        print()
        
    except SzError as err:
        print(f"✗ Error finding path: {err}\n")


def why_entity_analysis(sz_engine, data_source_1, record_id_1, data_source_2, record_id_2):
    """
    Example: Explain why two records did or didn't resolve together.
    
    Args:
        sz_engine: Initialized SzEngine instance
        data_source_1: First record's data source
        record_id_1: First record's ID
        data_source_2: Second record's data source
        record_id_2: Second record's ID
    """
    print("=" * 60)
    print(f"EXAMPLE 5: Why Analysis - {data_source_1} {record_id_1} vs {data_source_2} {record_id_2}")
    print("=" * 60)
    
    try:
        # Explain why records did/didn't resolve (simple API)
        result = sz_engine.why_records(data_source_1, record_id_1, data_source_2, record_id_2)
        
        why_result = json.loads(result)
        
        print(f"✓ Why analysis completed!")
        
        # Check if entities match
        why_info = why_result.get("WHY_RESULTS", [{}])[0]
        match_info = why_info.get("MATCH_INFO", {})
        
        if match_info.get("WHY_KEY"):
            print(f"  Result: MATCH")
            print(f"  Reason: {match_info.get('WHY_KEY')}")
            print(f"  Match Level: {match_info.get('MATCH_LEVEL_CODE', 'N/A')}")
        else:
            print(f"  Result: NO MATCH")
        
        # Show matching features
        rules = match_info.get("FEATURE_SCORES", {})
        if rules:
            print(f"\n  Matching Features:")
            for feature_type, features in list(rules.items())[:3]:
                print(f"    - {feature_type}: {len(features)} feature(s)")
        
        print()
        
    except SzError as err:
        print(f"✗ Error in why analysis: {err}\n")


def get_engine_statistics(sz_engine):
    """
    Example: Get basic Senzing statistics.
    
    Args:
        sz_engine: Initialized SzEngine instance
    """
    print("=" * 60)
    print("EXAMPLE 6: Engine Statistics")
    print("=" * 60)
    
    try:
        # Get engine statistics
        result = sz_engine.get_stats()
        print("✓ Engine Statistics:")
        print(result)
        print()
        
    except SzError as err:
        print(f"✗ Error getting statistics: {err}\n")


def main():
    """Main function to run all examples."""
    print("\n" + "=" * 60)
    print("SENZING SDK PYTHON EXAMPLES")
    print("=" * 60 + "\n")
    
    # Initialize Senzing - keep factory alive!
    sz_factory, sz_engine = initialize_senzing()
    
    try:
        # Example 1: Add a new record
        add_new_record(sz_engine)
        
        # Example 2: Get entity by record ID
        # Using a record from the demo data
        get_entity_by_record(sz_engine, "CUSTOMERS", "1070")
        
        # Example 3: Search by attributes
        search_by_attributes(sz_engine)
        
        # Example 4: Find path between entities
        # Note: These entity IDs may vary based on your data
        # You can get actual entity IDs from Example 2 results
        find_path_between_entities(sz_engine, 1, 2)
        
        # Example 5: Why analysis - explain entity resolution
        why_entity_analysis(sz_engine, "CUSTOMERS", "1001", "CUSTOMERS", "1002")
        
        # Example 6: Get engine statistics
        get_engine_statistics(sz_engine)
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up (factory and engine are automatically destroyed when they go out of scope)
        print("Cleaning up...\n")


if __name__ == "__main__":
    main()

