from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
url = os.getenv("WP_URL")
username = os.getenv("USER_LOGIN")
user_Pass = os.getenv("PASSWORD")

# Initialize WebDriver (assuming ChromeDriver is installed)
driver = webdriver.Chrome()

# Function to login to WordPress
def login_to_wp():
    driver.get(url)  # Go to WordPress login page

    # Find and fill in the username and password fields, then submit
    driver.find_element(By.ID, "user_login").send_keys(username)
    driver.find_element(By.ID, "user_pass").send_keys(user_Pass)
    driver.find_element(By.ID, "wp-submit").click()

    # Wait for login to complete (adjust the wait time if necessary)
    time.sleep(3)

    # Check if login is successful (you can modify this condition as needed)
    if "Dashboard" in driver.title:
        print("Logged in successfully.")
    else:
        print("Login failed. Please check your credentials.")
        driver.quit()

# Function to perform the entire sequence of actions after login
def perform_actions(post_id):
    wp_url = f"{url}/post.php?post={post_id}&action=edit"
    driver.get(wp_url)  # Navigate to the post edit page
    time.sleep(3)  # Wait for the page to load

    # Step 1: Click on the element with class 'rank-math-toolbar-score bad-fk'
    try:
        element = driver.find_element(By.CSS_SELECTOR, '.rank-math-toolbar-score.bad-fk')
        element.click()
        print('Element clicked successfully!')
    except Exception as e:
        print('Element not found or error occurred:', e)

    # Step 2: Get the post title and tagify input
    try:
        post_title = driver.find_element(By.CSS_SELECTOR, '.editor-document-bar__post-title')
        tagify_input = driver.find_element(By.CSS_SELECTOR, '.tagify__input')
        
        title_text = post_title.text
        
        # Step 3: Split the title by any dash (hyphen, en dash, em dash)
        first_part = title_text.split('–')[0].split('—')[0].split('-')[0].strip()
        
        # Step 4: Split the first part into words and take only the first two words
        first_two_words = " ".join(first_part.split()[:2])  # Get the first two words

        # Simulate a click on the tagify input to focus it
        tagify_input.click()
        print('Tagify input clicked.')

        # Insert the first two words into the tagify input field (simulating typing)
        tagify_input.clear()  # Clear any existing value
        tagify_input.send_keys(first_two_words)  # Insert the first two words
        
        # Trigger the input change event
        tagify_input.send_keys(Keys.TAB)  # Simulate tabbing away to trigger any necessary events
        time.sleep(3)
        
        print(f'First two words from the first part set to tagify input: {first_two_words}')
    except Exception as e:
        print('Error:', e)

    # Now, click on the "Save" button
    try:
        save_button = driver.find_element(By.CSS_SELECTOR, '.components-button.editor-post-publish-button.editor-post-publish-button__button.is-primary.is-compact')
        save_button.click()
        print('Save button clicked.')
    except Exception as e:
        print('Error clicking the save button:', e)

# Start by logging into WordPress
login_to_wp()

# Start a loop that asks for the post ID after completing the actions for a post
while True:
    # # Get the post ID from the user input
    # post_id = input("Please enter the WordPress Post ID (or type 'exit' to quit): ")
    
    # if post_id.lower() == 'exit':
    #     print("Exiting the script.")
    #     break  # Exit the loop if the user types 'exit'
    # List of post IDs

    post_ids = [
    7541, 7545, 7722, 7733, 7748, 7751, 7754, 7761, 
    7764, 7767, 7770, 7781, 7784, 7787, 7790, 7793, 7798, 7801, 7804, 7807, 
    7810, 7811, 7814, 7817, 7820, 7823, 7828, 7833, 7836, 7839, 7842, 7845, 
    7849, 7851, 7854, 7857, 7860, 7865, 7866, 7871, 7876, 7879, 7882, 7885, 
    7886, 7889, 7894, 7899, 7918, 7921, 7931, 7932, 7937, 7942, 7945, 7948, 
    7953, 7957, 7960, 7963, 7966, 7969, 7972, 7975, 7978, 7981, 7984, 7987, 
    7990, 7993, 7996, 7999, 8007, 8010, 8013, 8014, 8017, 8020, 8023, 8026, 
    8035, 8039, 8042, 8046, 8055, 8058, 8061, 8064, 8067, 8071, 8074, 8077, 
    8080, 8083, 8086, 8089, 8092, 8095, 8098, 8172, 8929, 8936, 8942, 8949, 
    8952, 8970, 9625, 9628, 9632, 9635, 9638, 9665, 9678, 9713, 9719, 9725, 
    9778, 9784, 9790, 9798, 9849, 9863, 9871, 9877, 9884, 9892, 9899, 9906, 
    9912, 9918, 10160, 10162, 10188, 10220, 10272, 10278, 10293
    ]
    #7876, 7882, 8007, 7999, 8010, 9871

    # Pass the post ID dynamically when performing actions
    for post_id in post_ids:
        perform_actions(post_id)
        # Hold the browser open for 10 seconds so you can verify if it worked
        print("Waiting for 10 seconds to verify the changes...")
        time.sleep(10)

    # Close the browser after the loop finishes (if user exits)
    driver.quit()
