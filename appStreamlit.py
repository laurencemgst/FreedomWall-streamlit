import streamlit as st
import sqlite3
from datetime import datetime
import random

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('freedom_wall.db')
    return conn

# Function to check if the user exists
def user_exists(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user

# Function to create a new user
def create_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to authenticate user
def authenticate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user

# Function to get all posts
def get_posts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT posts.id, users.username, posts.content, posts.created_at, posts.user_id FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC')
    posts = cur.fetchall()
    conn.close()
    random.shuffle(posts)
    return posts

# Function to add a new post
def add_post(user_id, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()
    conn.close()

# Function to delete a post
def delete_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Freedom Wall", page_icon=":guardsman:", layout="centered")
st.markdown("<h1 style='text-align: center;'>Freedom Wall Feed</h1>", unsafe_allow_html=True)

#sidebar title
st.sidebar.title("FREEDOM WALL")

# Check if user is logged in
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# If the user is logged in, show their username in the sidebar
if st.session_state.user_id is not None:
    username = st.session_state.username
    st.sidebar.title(f"Welcome back, {username}")
    st.sidebar.write(f"Logged in as: {username}")
    
    # Post option visible to logged-in users only
    st.sidebar.subheader("Post to the Freedom Wall")
    content = st.sidebar.text_area("What's on your mind?", key="post_content")
    post_button = st.sidebar.button("Post", key="post_button")
    
    if post_button and content:
        add_post(st.session_state.user_id, content)
        st.sidebar.success("Your post has been added!")

else:
    st.sidebar.title("Login or Sign Up")
    # Login form
    username_input = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")
    
    if login_button:
        user = authenticate_user(username_input, password_input)
        if user:
            # Update session state and rerun the app
            st.session_state.user_id = user[0]  # Store the user ID in session
            st.session_state.username = username_input  # Store the username in session
            st.sidebar.success(f"Welcome back, {username_input}!")
            st.rerun()  # Refresh the page immediately
        else:
            st.sidebar.error("Invalid credentials. Please try again.")

    # Sign up form
    st.sidebar.subheader("Don't have an account?")
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")
    sign_up_button = st.sidebar.button("Sign Up")
    
    if sign_up_button:
        if user_exists(new_username):
            st.sidebar.error("Username already exists.")
        else:
            create_user(new_username, new_password)
            st.sidebar.success(f"Account created for {new_username}. You can now log in!")

# Always display the feed, regardless of whether logged in or not
posts = get_posts()

if not posts:
    st.write("No posts to display yet!")

posts = get_posts()
for post in posts:
    post_id, username, content, created_at, user_id = post
    # Format the post content and timestamp
    post_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    
    # Create columns for the post content and delete button
    col1, col2 = st.columns([3, 1])  # 3 parts for the post, 1 part for the delete button
    
    # Display post content in the first column (col1)
    with col1:
        st.markdown(f"**{username}** - *Posted on {post_time}*")
        st.write(content)
    
    # If the user is logged in and is the owner of the post, show the delete button in the second column (col2)
    if st.session_state.user_id == user_id:  # Check if logged-in user is the post owner
        with col2:
            delete_button = st.button(f"Delete", key=f"delete_{post_id}")
            if delete_button:
                delete_post(post_id)
                st.rerun()  # Refresh the feed after deletion
                st.success("Your post has been deleted!")
    
    st.markdown("---")  # Divider line after each post
