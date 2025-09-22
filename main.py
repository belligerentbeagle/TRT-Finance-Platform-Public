import streamlit as st
import src.utils.userAuthentication as userAuth
import streamlit_authenticator as stauth

# st.set_page_config(page_title="TRT Finance Platform", page_icon="🧑‍🎨", layout="centered", initial_sidebar_state="auto", menu_items=None)

def main():
    st.session_state.version = "1.0"
    config = userAuth.load_config()
    authenticator = userAuth.create_authenticator(config)
    userAuth.authenticate_user(authenticator)


    if st.session_state["authentication_status"]:

        pg = st.navigation({
            "Main Features": [
                st.Page("src/modules/Home.py", title="Home", icon="🏠", default=True),
                st.Page("src/modules/BankStatementAnalyser.py", title="Update Payments", icon="🏦", url_path="BankStatementAnalyser"),
                st.Page("src/modules/InvoiceAndClass.py", title="Invoice Generation (Once/Term)", icon="🧾", url_path="invoiceCreation"),],
            
            "Create Students/Parents/Terms/Classes": [
                st.Page("src/modules/ManageStudentAndParent.py", title="Manage Students & Parents", icon="👨🏻‍🎓", url_path="manageStudents"),
                st.Page("src/modules/ManageTermAndClass.py", title="Manage Terms & Class Rates", icon="🎲", url_path="manageTermAndClass"),
            ],

            "Account": [st.Page(userAuth.logout, title="Logout", icon="👋", url_path="logout")],  
        })

        pg.run()

if __name__ == "__main__":
    main()