"""
Test database and Kafka connectivity

Run: python realtime/test_infrastructure.py
"""

import sys


def test_postgres():
    """Test PostgreSQL connection and schema"""
    print("=" * 60)
    print("TEST 1: PostgreSQL Connection")
    print("=" * 60)
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="credit_risk",
            user="credit",
            password="risk"
        )
        
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'risk_scored'
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Table 'risk_scored' exists")
        else:
            print("❌ Table 'risk_scored' not found")
            return False
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM risk_scored")
        row_count = cursor.fetchone()[0]
        print(f"✅ Current rows in table: {row_count}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'risk_scored'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✅ Indexes: {', '.join(indexes)}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ PostgreSQL test FAILED: {e}\n")
        return False


def test_kafka():
    """Test Kafka connection"""
    print("=" * 60)
    print("TEST 2: Kafka Connection")
    print("=" * 60)
    
    try:
        from kafka import KafkaProducer
        from kafka.errors import NoBrokersAvailable
        import json
        
        # Try to connect
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=5000
        )
        
        print("✅ Connected to Kafka broker")
        
        # Send test message
        test_topic = 'test-connectivity'
        test_message = {'test': 'message', 'timestamp': 'now'}
        
        future = producer.send(test_topic, test_message)
        producer.flush()
        
        print(f"✅ Sent test message to topic '{test_topic}'")
        
        producer.close()
        
        print("\n✅ Kafka test PASSED\n")
        return True
        
    except NoBrokersAvailable:
        print("\n❌ Kafka test FAILED: No brokers available")
        print("   Make sure Redpanda is running:")
        print("   docker ps | grep redpanda\n")
        return False
    except Exception as e:
        print(f"\n❌ Kafka test FAILED: {e}\n")
        return False


def test_dotenv():
    """Test python-dotenv"""
    print("=" * 60)
    print("TEST 3: Environment Variables")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Create a test .env file if it doesn't exist
        env_file = ".env.test"
        with open(env_file, 'w') as f:
            f.write("TEST_VAR=test_value\n")
        
        load_dotenv(env_file)
        
        test_var = os.getenv("TEST_VAR")
        
        if test_var == "test_value":
            print("✅ python-dotenv working correctly")
            print(f"   Loaded: TEST_VAR={test_var}")
        else:
            print("❌ python-dotenv not loading variables correctly")
            return False
        
        # Clean up
        os.remove(env_file)
        
        print("\n✅ Environment variables test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Environment variables test FAILED: {e}\n")
        return False


def test_insert_and_query():
    """Test inserting a scored event and querying it"""
    print("=" * 60)
    print("TEST 4: Insert & Query Scored Event")
    print("=" * 60)
    
    try:
        import psycopg2
        from datetime import datetime
        
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="credit_risk",
            user="credit",
            password="risk"
        )
        
        cursor = conn.cursor()
        
        # Insert test event
        test_loan_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO risk_scored (
                loan_id, purpose, term, loan_amnt, annual_inc, dti,
                int_rate_pct, revol_util_pct, delinq_2yrs, inq_last_6mths,
                credit_history_years, emp_length_yrs,
                dti_band, util_band, rate_band,
                early_warning_flag, risk_tier, reasons
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id, event_time
        """, (
            test_loan_id,
            'test',
            '36 months',
            10000.0,
            50000.0,
            25.0,
            12.5,
            50.0,
            0.0,
            1.0,
            5.0,
            3.0,
            'Moderate',
            'Moderate',
            'Moderate',
            0,
            'Low',
            'Test event'
        ))
        
        inserted_id, event_time = cursor.fetchone()
        conn.commit()
        
        print(f"✅ Inserted test event:")
        print(f"   ID: {inserted_id}")
        print(f"   Loan ID: {test_loan_id}")
        print(f"   Event Time: {event_time}")
        
        # Query it back
        cursor.execute("""
            SELECT loan_id, risk_tier, reasons
            FROM risk_scored
            WHERE id = %s
        """, (inserted_id,))
        
        result = cursor.fetchone()
        
        if result:
            loan_id, risk_tier, reasons = result
            print(f"\n✅ Queried event back:")
            print(f"   Loan ID: {loan_id}")
            print(f"   Risk Tier: {risk_tier}")
            print(f"   Reasons: {reasons}")
        else:
            print("\n❌ Could not query event back")
            return False
        
        # Clean up test data
        cursor.execute("DELETE FROM risk_scored WHERE id = %s", (inserted_id,))
        conn.commit()
        print(f"\n✅ Cleaned up test event (ID: {inserted_id})")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Insert & Query test PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Insert & Query test FAILED: {e}\n")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INFRASTRUCTURE CONNECTIVITY TESTS")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("PostgreSQL", test_postgres()))
    results.append(("Kafka", test_kafka()))
    results.append(("Environment Variables", test_dotenv()))
    results.append(("Insert & Query", test_insert_and_query()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print("=" * 60)
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("Infrastructure is ready for streaming!\n")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please check the errors above and fix before proceeding.\n")
        sys.exit(1)
