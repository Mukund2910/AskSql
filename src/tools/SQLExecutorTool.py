from typing import Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from crewai.tools import BaseTool

class SQLExecutorTool(BaseTool):
    """Tool for executing SQL commands in a database."""
    
    name: str = "SQLExecutor"
    description: str = "Executes SQL commands on a database. Input should be a valid SQL query string."
    db_uri: str = Field(..., description="Database connection URI")

    def __init__(self, db_uri: str):
        """Initialize and validate database connection."""
        super().__init__(db_uri=db_uri)
        # Test database connection during initialization
        engine = create_engine(self.db_uri)
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))  # Simple test query
        except SQLAlchemyError as e:
            raise ValueError(f"Failed to connect to database: {str(e)}") from e

    def _run(self, sql_command: str) -> dict:
        """Execute an SQL command on the connected database."""
        try:
            engine = create_engine(self.db_uri)
            with engine.connect() as connection:
                result = connection.execute(text(sql_command))
                if result.returns_rows:
                    columns = result.keys()
                    rows = [dict(zip(columns, row)) for row in result.fetchall()]
                    return {
                        "status": "success",
                        "data": rows,
                        "message": "Query executed successfully."
                    }
                else:
                    connection.commit()
                    return {
                        "status": "success",
                        "data": None,
                        "message": "Data manipulation command executed successfully."
                    }
        except SQLAlchemyError as e:
            return {
                "status": "error",
                "data": None,
                "message": f"SQL execution failed: {str(e)}"
            }
