"""
Seed test products with barcodes into Supabase
Run this script to populate test data for barcode lookup testing

Usage:
    python backend/scripts/seed_test_products.py
"""

import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from utils.supabase_client import get_supabase_client

# Test products with barcodes
TEST_PRODUCTS = [
    {
        "brand_name": "Pure Care Organic",
        "barcode": "012345678901",
        "product_type": "tampon",
        "ingredients": [1, 2, 3],  # IDs from ingredients_library
        "coverage_score": 0.95,
        "research_count": 15,
        "status": "active"
    },
    {
        "brand_name": "Nature's Choice",
        "barcode": "054321987654",
        "product_type": "pad",
        "ingredients": [1, 4, 5],
        "coverage_score": 0.88,
        "research_count": 12,
        "status": "active"
    },
    {
        "brand_name": "EcoFlow Tampons",
        "barcode": "123456789012",
        "product_type": "tampon",
        "ingredients": [2, 3, 6],
        "coverage_score": 0.92,
        "research_count": 18,
        "status": "active"
    },
    {
        "brand_name": "Comfort Plus Pads",
        "barcode": "987654321098",
        "product_type": "pad",
        "ingredients": [1, 2, 7],
        "coverage_score": 0.78,
        "research_count": 8,
        "status": "active"
    },
    {
        "brand_name": "Gentle Wave",
        "barcode": "555666777888",
        "product_type": "tampon",
        "ingredients": [3, 4, 8],
        "coverage_score": 0.85,
        "research_count": 11,
        "status": "active"
    }
]


def seed_products():
    """
    Insert test products into the products table
    """
    try:
        supabase = get_supabase_client()
        
        print("🌱 Seeding test products...")
        print(f"   Products to insert: {len(TEST_PRODUCTS)}")
        
        # Insert each product
        for idx, product in enumerate(TEST_PRODUCTS, 1):
            try:
                response = supabase.table('products').insert(product).execute()
                print(f"   ✓ [{idx}/{len(TEST_PRODUCTS)}] Inserted: {product['brand_name']} (barcode: {product['barcode']})")
            except Exception as e:
                print(f"   ✗ [{idx}/{len(TEST_PRODUCTS)}] Failed to insert {product['brand_name']}: {e}")
        
        print("\n✅ Test products seeded successfully!")
        print("\nSample barcodes for testing:")
        for product in TEST_PRODUCTS:
            print(f"   - {product['barcode']}: {product['brand_name']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error seeding products: {e}")
        return False


def verify_seeds():
    """
    Verify that test products were inserted
    """
    try:
        supabase = get_supabase_client()
        
        print("\n🔍 Verifying seeded products...")
        
        # Query all test products
        response = supabase.table('products').select(
            'id, brand_name, barcode, product_type, coverage_score, research_count'
        ).in_('barcode', [p['barcode'] for p in TEST_PRODUCTS]).execute()
        
        if not response.data:
            print("   ⚠️  No test products found")
            return False
        
        print(f"   Found {len(response.data)} test products:")
        for product in response.data:
            print(f"   - {product['barcode']}: {product['brand_name']} ({product['product_type']})")
        
        return True
    
    except Exception as e:
        print(f"❌ Error verifying products: {e}")
        return False


def cleanup_test_products():
    """
    Delete all test products (cleanup)
    """
    try:
        supabase = get_supabase_client()
        
        print("\n🗑️  Cleaning up test products...")
        
        test_barcodes = [p['barcode'] for p in TEST_PRODUCTS]
        response = supabase.table('products').delete().in_('barcode', test_barcodes).execute()
        
        print(f"   ✓ Deleted {len(test_barcodes)} test products")
        return True
    
    except Exception as e:
        print(f"❌ Error cleaning up products: {e}")
        return False


def test_barcode_lookup(barcode: str):
    """
    Test barcode lookup functionality
    
    Args:
        barcode: Barcode to lookup
    """
    try:
        supabase = get_supabase_client()
        
        print(f"\n🔎 Testing barcode lookup: {barcode}")
        
        # Lookup product by barcode
        response = supabase.table('products').select(
            'id, brand_name, barcode, ingredients, product_type, coverage_score, research_count'
        ).eq('barcode', barcode).execute()
        
        if not response.data:
            print(f"   ✗ Product not found for barcode: {barcode}")
            return False
        
        product = response.data[0]
        print(f"   ✓ Found product: {product['brand_name']}")
        print(f"      - ID: {product['id']}")
        print(f"      - Barcode: {product['barcode']}")
        print(f"      - Type: {product['product_type']}")
        print(f"      - Ingredient IDs: {product['ingredients']}")
        print(f"      - Coverage: {product['coverage_score']}")
        print(f"      - Research Count: {product['research_count']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing barcode lookup: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Test Product Seeding Script")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "seed":
            seed_products()
            verify_seeds()
        
        elif command == "verify":
            verify_seeds()
        
        elif command == "cleanup":
            cleanup_test_products()
        
        elif command == "test":
            barcode = sys.argv[2] if len(sys.argv) > 2 else TEST_PRODUCTS[0]['barcode']
            test_barcode_lookup(barcode)
        
        elif command == "help":
            print("""
Usage:
    python backend/scripts/seed_test_products.py <command> [args]

Commands:
    seed            - Insert test products into database
    verify          - Verify test products were inserted
    cleanup         - Delete all test products
    test <barcode>  - Test barcode lookup (defaults to first test product)
    help            - Show this help message

Examples:
    python backend/scripts/seed_test_products.py seed
    python backend/scripts/seed_test_products.py verify
    python backend/scripts/seed_test_products.py test 012345678901
    python backend/scripts/seed_test_products.py cleanup

Test Product Barcodes:
    - 012345678901: Pure Care Organic
    - 054321987654: Nature's Choice
    - 123456789012: EcoFlow Tampons
    - 987654321098: Comfort Plus Pads
    - 555666777888: Gentle Wave
            """)
        
        else:
            print(f"Unknown command: {command}")
            print("Run 'python backend/scripts/seed_test_products.py help' for usage")
    
    else:
        # Default: seed and verify
        seed_products()
        verify_seeds()
        
        # Test first product
        print("\n" + "=" * 60)
        print("Testing Barcode Lookup")
        print("=" * 60)
        test_barcode_lookup(TEST_PRODUCTS[0]['barcode'])
        
        print("\n" + "=" * 60)
        print("✅ Script Complete")
        print("=" * 60)
