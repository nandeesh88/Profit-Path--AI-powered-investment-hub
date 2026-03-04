#!/usr/bin/env python
"""Test MongoDB connection and display database info"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        
        # Test connection by getting server info
        await client.admin.command('ping')
        print("[OK] MongoDB Connection Successful!\n")
        
        # Get profitpath database
        db = client['profitpath']
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"Collections in 'profitpath' database: {collections if collections else 'None (empty database)'}\n")
        
        # Get collection details
        if collections:
            for collection_name in collections:
                collection = db[collection_name]
                count = await collection.count_documents({})
                print(f"  {collection_name}: {count} documents")
                
                # Show a sample document (first one)
                if count > 0:
                    sample = await collection.find_one()
                    print(f"     Sample doc: {sample}\n")
        
        # List all databases
        admin_db = client['admin']
        databases = await admin_db.command('listDatabases')
        db_names = [db['name'] for db in databases['databases']]
        print(f"\nAll databases on server: {db_names}")
        
        await client.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[WARNING] Make sure MongoDB is running!")
        print("   Command: mongod")

if __name__ == "__main__":
    asyncio.run(test_connection())
