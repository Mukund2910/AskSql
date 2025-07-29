import streamlit as st
from streamlit_chat import message
from sqlalchemy.engine.url import make_url
import re
import base64
import os
from sqlalchemy import create_engine, exc

# Page configuration
st.set_page_config(
    page_title="AskSQL",
    page_icon="👨‍💻",
    layout="wide"
)

# Database configuration
DB_CONFIG = {
    "MySQL": {"port": 3306, "prefix": "mysql"},
    "PostgreSQL": {"port": 5432, "prefix": "postgresql"},
    "SQLite": {"port": None, "prefix": "sqlite"}
}

def init_session_state():
    """Initialize session state variables"""
    session_defaults = {
        'connected': False,
        'past': [],
        'generated': [],
        'db_uri': "",
        'db_type': "",
        'processing': False,
        'mermaid_images': {}
    }
    for key, value in session_defaults.items():
        st.session_state.setdefault(key, value)

def validate_db_connection(db_uri: str, db_type: str, schema: str):
    """Validate actual database connection"""
    try:
        if db_type == "SQLite":
            if not os.path.exists(schema):
                raise ValueError(f"Database file '{schema}' not found")
            # Test SQLite connection
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                pass
        else:
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                pass
        return True
    except exc.SQLAlchemyError as e:
        raise ValueError(f"Connection failed: {str(e)}") from e

def process_mermaid_content(content: str):
    """Convert mermaid code blocks to image URLs and return cleaned text with image list"""
    image_urls = []
    
    def replace_mermaid(match):
        mermaid_code = match.group(1).strip()
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        url = f"https://mermaid.ink/svg/{encoded}"
        image_urls.append(url)
        return ""  # Remove mermaid code from text content

    cleaned_text = re.sub(
        r'```mermaid(.*?)```',
        replace_mermaid,
        content,
        flags=re.DOTALL
    ).strip()
    
    return cleaned_text, image_urls

def database_connection_form():
    """Render improved database connection form"""
    with st.form("db_connection"):
        st.subheader("🔑 Database Connection")
        
        db_type = st.selectbox(
            "Database Type", 
            list(DB_CONFIG.keys()),
            help="Select your database management system"
        )
        
        # Contextual help message
        if db_type == "SQLite":
            st.caption("💡 Enter path to your SQLite database file (e.g. 'data/my_db.db')")
        else:
            st.caption("💡 Enter your database server credentials")

        # Database path/name input
        schema_label = "📁 Database Path" if db_type == "SQLite" else "📚 Database Name"
        schema = st.text_input(
            schema_label,
            placeholder="my_database.db" if db_type == "SQLite" else "my_database",
            help="SQLite: Path to .db file\nOthers: Database name"
        )

        # Server details for non-SQLite
        if db_type != "SQLite":
            st.markdown("---")
            st.subheader("🌐 Server Configuration")
            host, port = st.columns(2)
            with host:
                host_input = st.text_input("Host", value="localhost", help="Database server host address")
            with port:
                port_input = st.number_input("Port", value=DB_CONFIG[db_type]["port"], help="Database server port")

            st.subheader("🔐 Authentication")
            username = st.text_input("Username", help="Database username")
            password = st.text_input("Password", type="password", help="Database password")

        if st.form_submit_button("🚀 Connect", use_container_width=True):
            try:
                # Build connection URI
                if db_type == "SQLite":
                    db_uri = f"{DB_CONFIG[db_type]['prefix']}:///{schema}"
                else:
                    db_uri = f"{DB_CONFIG[db_type]['prefix']}://{username}:{password}@{host_input}:{port_input}/{schema}"

                # Validate connection
                with st.spinner("🔒 Testing connection..."):
                    # Syntax validation
                    make_url(db_uri)
                    # Actual connection test
                    validate_db_connection(db_uri, db_type, schema)

                # Update session state if successful
                st.session_state.update({
                    'connected': True,
                    'db_uri': db_uri,
                    'db_type': db_type
                })
                st.toast("✅ Connection Established!", icon="🎉")
                
            except Exception as e:
                st.session_state.connected = False
                st.error(f"**Connection failed:** {str(e)}")
                st.markdown("ℹ️ Check your:")
                st.markdown("- Database server status  \n- Authentication credentials  \n- Network connectivity")
                st.stop()

def handle_query_processing():
    """Process user query with error handling"""
    try:
        from src.crew import SolveUserQueryCrew
        crew = SolveUserQueryCrew().solve_query_crew()
        result = crew.kickoff(inputs={
            'db_uri': st.session_state.db_uri,
            'query': st.session_state.past[-1],
            'database': st.session_state.db_type.lower()
        })
        response = str(getattr(result, 'result', str(result)))
        
        # Handle edge cases
        if not response:
            return "Received empty response from query processor", []
        if "```mermaid" in response and "```" not in response:
            return "⚠️ Invalid Mermaid syntax in response", []
            
        return process_mermaid_content(response)
    except Exception as e:
        return f"🚨 **Error Processing Query**\n\n{str(e)}", []

def chat_interface():
    """Chat interface with proper image handling"""
    st.subheader(f"💬 Chat With Your {st.session_state.db_type} Database")
    
    # Display initial greeting
    if not st.session_state.generated:
        with st.container():
            message("""Hey there! 👋 Your Database Assistant is here to help! I can assist you with the following:
💬 Chat with your database using everyday language
🔍 Dive into your database structure
📊 Explore your data
📈 Create visual ER diagrams
💾 Manage your database entities""", is_user=False, avatar_style="bottts-neutral")

    # Display chat messages
    for i in range(len(st.session_state.past)):
        # User message
        message(st.session_state.past[i], is_user=True,avatar_style="fun-emoji")
        
        # Bot response
        if i < len(st.session_state.generated):
            text_content, image_urls = st.session_state.generated[i]
            
            # Text content
            if text_content:
                message(text_content, is_user=False,avatar_style="bottts-neutral")
            
            # Images with proper scaling
            if image_urls:
                with st.container():
                    for img_idx, url in enumerate(image_urls):
                        st.image(
                            url,
                            use_container_width=True,
                            output_format="SVG",
                            caption=f"Diagram {img_idx+1}"
                        )

    # User input handling
    if st.session_state.connected and not st.session_state.processing:
        query = st.chat_input("🔍 Enter your database query...")
        if query:
            st.session_state.past.append(query)
            st.session_state.processing = True
            st.rerun()

    # Process query
    if st.session_state.processing:
        with st.spinner("🔍 Analyzing..."):
            text_response, image_urls = handle_query_processing()
            st.session_state.generated.append((text_response, image_urls))
            st.session_state.processing = False
            st.rerun()

def render_sidebar():
    """Simplified sidebar controls"""
    with st.sidebar:
        st.markdown("### 🛠️ Controls")
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("""
        ## 📖 Guide
        1. Connect to database
        2. Interact with the Database in Natural Language
        3. Provide detailed and well-explained questions/tasks for optimal results.
        """)

def main():
    """Main application flow"""
    init_session_state()
    st.title("👨‍💻🔍⛃ AskSQL - Database Chat Assistant")
    render_sidebar()
    
    if not st.session_state.connected:
        database_connection_form()
    else:
        chat_interface()

if __name__ == "__main__":
    main()