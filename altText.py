from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
url = os.getenv("WP_URL")
username = os.getenv("USER_LOGIN")
user_Pass = os.getenv("PASSWORD")

# Set up your WordPress login credentials here
WP_URL = url
USERNAME = username
PASSWORD = user_Pass

# Initialize WebDriver (assuming ChromeDriver is installed)
driver = webdriver.Chrome()  # Replace with WebDriverManager if needed

# Hardcoded initial image ID
initial_image_id = "10649"  # Example image ID, replace with the actual one

# Login to WordPress Admin
def login_to_wp():
    driver.get(WP_URL)  # Go to WordPress login page

    # Find and fill in the username and password fields, then submit
    driver.find_element(By.ID, "user_login").send_keys(USERNAME)
    driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
    driver.find_element(By.ID, "wp-submit").click()

    # Wait for login to complete (adjust the wait time if necessary)
    time.sleep(3)

    # Check if login is successful (you can modify this condition as needed)
    if "Dashboard" in driver.title:
        print("Logged in successfully.")
    else:
        print("Login failed. Please check your credentials.")
        driver.quit()

# Function to extract image ID from the URL
def extract_image_id():
    url = driver.current_url
    image_id = re.search(r"item=(\d+)", url)
    if image_id:
        return image_id.group(1)
    else:
        print("Image ID not found!")
        return None

# Function to fill Alt Text and Caption based on the post title (Uploaded To)
def fill_alt_and_caption(image_id):
    if not image_id:
        print("Image ID not found!")
        return

    # Wait until the modal is fully loaded and the elements are available
    while True:
        try:
            alt_text_input = driver.find_element(By.ID, 'attachment-details-two-column-alt-text')
            caption_input = driver.find_element(By.ID, 'attachment-details-two-column-caption')
            uploaded_to_element = driver.find_element(By.CSS_SELECTOR, '.uploaded-to')

            if alt_text_input and caption_input and uploaded_to_element:
                # Get the post title (Uploaded To) from the element with class "uploaded-to"
                post_title = uploaded_to_element.text.strip()

                # Remove the "Uploaded to: " prefix
                post_title = post_title.replace("Uploaded to: ", "")

                # Use a regex to match everything before the first dash (–)
                post_title = re.sub(r" -.*", "", post_title)

                # Log the current alt text and caption values
                print("Alt Text Value:", post_title)
                print("Caption Value:", post_title)
                print("Post Title (Before Dash):", post_title)

                # Set the Alt Text and Caption fields with the post title
                alt_text_input.send_keys(Keys.CONTROL + "a")  # Clear the existing text
                alt_text_input.send_keys(post_title)

                caption_input.send_keys(Keys.CONTROL + "a")  # Clear the existing text
                caption_input.send_keys(post_title)

                # Trigger the change event (if required)
                alt_text_input.send_keys(Keys.TAB)
                caption_input.send_keys(Keys.TAB)

                break  # Exit the loop once values are set
        except Exception as e:
            print("Waiting for the input fields...")
            time.sleep(0.5)  # Check every 500ms to see if the input fields are ready

# Function to open the image URL (navigate to the image edit page)
def navigate_to_media_item(image_id):
    # Navigate to the image edit page using the image ID
    driver.get(f'{WP_URL}/upload.php?item={image_id}')
    time.sleep(3)  # Wait for the page to load

# Function to click the "Next" button and go to the next image
def click_next_button():
    try:
        # Find the "Next" button using the class 'right' and click it
        next_button = driver.find_element(By.CLASS_NAME, "right")
        next_button.click()
        time.sleep(3)  # Wait for the next image to load
    except Exception as e:
        print("Next button not found, or end of images reached.")
        return False  # Return False if no "Next" button is found
    return True

# Start the login process
login_to_wp()

# Start with the initial image ID
current_image_id = initial_image_id

# Loop to process images
while True:
    # Navigate to the image edit page with the current image ID
    navigate_to_media_item(current_image_id)

    # Fill Alt and Caption for the current image
    fill_alt_and_caption(current_image_id)

    # Wait for 5 seconds before looking for the "Next" button
    print("Waiting for 5 seconds before looking for the Next button...")
    time.sleep(5)

    # Try to find the "Next" button by class and click it
    if not click_next_button():
        print("No more images found. Exiting.")
        break  # If no "Next" button is found, exit the loop

    # After clicking Next, wait another 5 seconds for the next image to load
    print("Waiting for 5 seconds after clicking Next...")
    time.sleep(5)

    # Extract the next image ID from the URL (if available)
    new_image_id = extract_image_id()

    # If no new image ID is found, stop the loop
    if not new_image_id:
        print("No new image ID found. Exiting.")
        break

    # Update the current image ID for the next iteration
    current_image_id = new_image_id

# End the script and close the browser
driver.quit()
