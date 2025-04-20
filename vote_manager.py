# vote_manager.py

import psycopg2
import os
import logging
from datetime import datetime
from psycopg2.extras import DictCursor

# Get the database URL from the environment variable set by Heroku
DATABASE_URL = os.environ.get('DATABASE_URL')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/vote_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set.")
        raise ValueError("Database connection URL not found.")
    
    # Fix for Heroku PostgreSQL URL format
    db_url = DATABASE_URL
    if db_url.startswith("postgres://"):
        logger.info("Converting postgres:// URL to postgresql:// format")
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Connect using the URL, requiring SSL
        logger.info(f"Connecting to database with URL: {db_url[:25]}...") # Log only the beginning for security
        conn = psycopg2.connect(db_url, sslmode='require')
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error connecting to database: {e}")
        # Print to stdout for Heroku logs
        print(f"DATABASE CONNECTION ERROR: {str(e)}")
        raise

def init_db():
    """Initialize the database by creating the votes table if it doesn't exist."""
    logger.info("Initializing database...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("Creating votes table if it doesn't exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                user_query TEXT,
                bot_response TEXT,
                evaluation_json TEXT,
                vote TEXT CHECK(vote IN ('yes', 'no')),
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully")
        
        # Verify the table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'votes')")
        table_exists = cursor.fetchone()[0]
        logger.info(f"Votes table exists: {table_exists}")
        
        if table_exists:
            # Count rows in the table
            cursor.execute("SELECT COUNT(*) FROM votes")
            row_count = cursor.fetchone()[0]
            logger.info(f"Votes table contains {row_count} rows")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Print to stdout for Heroku logs
        print(f"DATABASE INIT ERROR: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def record_vote(user_query, bot_response, evaluation_json, vote, comment=""):
    """Record a vote in the database."""
    logger.info(f"Attempting to record vote: {vote}")
    if vote not in ["yes", "no"]:
        logger.error(f"Invalid vote value: {vote}")
        raise ValueError("Vote must be 'yes' or 'no'")

    sql = """
        INSERT INTO votes (user_query, bot_response, evaluation_json, vote, comment)
        VALUES (%s, %s, %s, %s, %s)
    """

    conn = None
    try:
        logger.info("Getting database connection...")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.info("Executing INSERT query...")
        cursor.execute(sql, (user_query, bot_response, evaluation_json, vote, comment))
        conn.commit()
        logger.info(f"Vote recorded successfully: {vote}")
        
        # Verify the insertion
        cursor.execute("SELECT COUNT(*) FROM votes WHERE vote = %s", (vote,))
        count = cursor.fetchone()[0]
        logger.info(f"Total votes with value '{vote}': {count}")
        
        cursor.close()
    except Exception as e:
        logger.error(f"Error recording vote: {e}")
        # Print to stdout for Heroku logs
        print(f"DATABASE RECORD ERROR: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
    
def fetch_votes(limit=None, offset=0, vote_filter=None, start_date=None, end_date=None):
    """
    Fetch votes with optional filtering and pagination

    Args:
        limit: Maximum number of votes to return (None for all)
        offset: Number of votes to skip
        vote_filter: Filter by vote type ('yes' or 'no')
        start_date: Filter votes from this date (inclusive, format 'YYYY-MM-DD')
        end_date: Filter votes up to this date (inclusive, format 'YYYY-MM-DD')

    Returns:
        List of dictionaries containing vote data
    """
    conn = None
    try:
        conn = get_db_connection()
        # Use DictCursor to return rows as dictionaries
        cursor = conn.cursor(cursor_factory=DictCursor)

        query = "SELECT id, user_query, bot_response, evaluation_json, vote, comment, timestamp FROM votes"
        conditions = []
        params = []

        if vote_filter:
            conditions.append("vote = %s")
            params.append(vote_filter)

        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                conditions.append("DATE(timestamp) >= %s")
                params.append(start_date)
            except Exception as e:
                logger.error(f"Invalid start_date format: {start_date} - {e}")

        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                conditions.append("DATE(timestamp) <= %s")
                params.append(end_date)
            except Exception as e:
                logger.error(f"Invalid end_date format: {end_date} - {e}")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC"

        if limit is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Fetched {len(rows)} votes")
        return rows
    except Exception as e:
        logger.error(f"Error executing fetch_votes query: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_vote_statistics():
    """
    Get statistics about the votes
    
    Returns:
        Dictionary containing vote statistics
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total votes
        cursor.execute("SELECT COUNT(*) FROM votes")
        total_votes = cursor.fetchone()[0]
        
        # Get yes votes
        cursor.execute("SELECT COUNT(*) FROM votes WHERE vote = 'yes'")
        yes_votes = cursor.fetchone()[0]
        
        # Get no votes
        cursor.execute("SELECT COUNT(*) FROM votes WHERE vote = 'no'")
        no_votes = cursor.fetchone()[0]
        
        # Get votes with comments
        cursor.execute("SELECT COUNT(*) FROM votes WHERE comment != ''")
        votes_with_comments = cursor.fetchone()[0]
        
        # Get votes per day (last 30 days)
        # PostgreSQL syntax for date operations
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM votes 
            WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days' 
            GROUP BY DATE(timestamp) 
            ORDER BY date
        """)
        votes_per_day = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        logger.info("Vote statistics retrieved successfully")
        
        return {
            "total_votes": total_votes,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "yes_percentage": (yes_votes / total_votes * 100) if total_votes > 0 else 0,
            "no_percentage": (no_votes / total_votes * 100) if total_votes > 0 else 0,
            "votes_with_comments": votes_with_comments,
            "votes_per_day": votes_per_day
        }
    except Exception as e:
        logger.error(f"Error retrieving vote statistics: {e}")
        return {
            "total_votes": 0,
            "yes_votes": 0,
            "no_votes": 0,
            "yes_percentage": 0,
            "no_percentage": 0,
            "votes_with_comments": 0,
            "votes_per_day": {}
        }
    finally:
        if conn:
            conn.close()
