import streamlit as st
import yaml
import streamlit_authenticator as stauth
import os
from pathlib import Path

def load_config():
    """
    Load authentication configuration from YAML file
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = Path("config.yaml")
    if not config_path.exists():
        st.error("Authentication configuration file not found.")
        st.stop()
        
    with open(config_path) as file:
        config = yaml.safe_load(file)
        
    return config

def setup_auth():
    """
    Setup authentication for the application
    
    Returns:
        tuple: (authenticator, authentication_status, username)
    """
    # Initialize session state variables for authentication
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'name' not in st.session_state:
        st.session_state.name = None
        
    # Load config and create authenticator
    config = load_config()
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Get authentication status
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    # Update session state
    st.session_state.authentication_status = authentication_status
    st.session_state.username = username
    st.session_state.name = name
    
    return authenticator, authentication_status, username

def check_auth():
    """
    Check if user is authenticated
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if st.session_state.authentication_status:
        return True
    elif st.session_state.authentication_status == False:
        st.error('Username/password is incorrect')
        return False
    elif st.session_state.authentication_status is None:
        st.warning('Please enter your username and password')
        return False
        
def get_user_info():
    """
    Get current user information
    
    Returns:
        dict: User information including username and name
    """
    return {
        'username': st.session_state.username,
        'name': st.session_state.name
    }

def is_admin():
    """
    Check if current user is an admin
    
    Returns:
        bool: True if admin, False otherwise
    """
    return st.session_state.username == 'admin'