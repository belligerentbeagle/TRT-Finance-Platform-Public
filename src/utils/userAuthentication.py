import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import yaml
from yaml.loader import SafeLoader

def load_config():
    with open("src/config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def create_authenticator(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator

def logout():
    st.session_state.authenticator.logout('Logout', 'main')


def authenticate_user(authenticator):
    name, authentication_status, username = authenticator.login(max_login_attempts=10, fields={'Form name': 'TRT Tuition Centre'})

    if st.session_state["authentication_status"]:
        with st.sidebar:
            st.session_state.authenticator = authenticator
            try:
                st.success(f'Welcome *{st.session_state["name"]}*')
                st.session_state["name"] = name
                st.session_state["username"] = username
            except:
                st.success(f'Welcome')
        return True
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')
        return False
    elif st.session_state["authentication_status"] == None:
        st.warning('Please enter your username and password')
        return False
