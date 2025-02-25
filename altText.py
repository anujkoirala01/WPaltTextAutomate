from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
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
initial_image_id = "9830"  # Example image ID, replace with the actual one

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
            # Try to find the "Uploaded to:" element first
            try:
                uploaded_to_element = driver.find_element(By.CSS_SELECTOR, '.uploaded-to')
                post_title = uploaded_to_element.text.strip() if uploaded_to_element else None
            except Exception as e:
                post_title = None  # Set post_title to None if 'Uploaded to:' is not found

            # If no valid "Uploaded to:" field found, skip this image and go to the next one
            if not post_title or post_title == "Uploaded to:":
                print("No valid 'Uploaded to:' field found. Skipping to next image.")
                click_next_button()  # Click "Next" to proceed to the next image
                return  # Exit the loop and skip the current image

            # Clean and process the post title (same as before)
            post_title = post_title.replace("Uploaded to: ", "")
            post_title = re.sub(r" [\-\–—].*", "", post_title)
            print("Alt Text Value:", post_title)
            print("Caption Value:", post_title)
            print("Post Title (Before Dash):", post_title)

            # Find the Caption input field (this is always available)
            caption_input = driver.find_element(By.ID, 'attachment-details-two-column-caption')

            # Check if the Alt Text field exists (it will not exist for video files)
            try:
                alt_text_input = driver.find_element(By.ID, 'attachment-details-two-column-alt-text')
                alt_text_exists = True
            except Exception as e:
                alt_text_exists = False  # Alt Text field does not exist for videos

            # Check for the file type (image/jpeg or mp4)
            file_type_element = driver.find_element(By.CSS_SELECTOR, '.file-type')
            file_type = file_type_element.text.strip()  # Get the text of the file type (e.g., "image/jpeg" or "video/mp4")
            print(f"File type: {file_type}")

            # If the file type is image/jpeg, fill both Alt Text and Caption
            if "image" in file_type and alt_text_exists:
                alt_text_input.send_keys(Keys.CONTROL + "a")  # Clear the existing text
                alt_text_input.send_keys(post_title)

            # Always fill the Caption field
            caption_input.send_keys(Keys.CONTROL + "a")  # Clear the existing text
            caption_input.send_keys(post_title)

            # Trigger the change event (if required)
            if alt_text_exists:
                alt_text_input.send_keys(Keys.TAB)  # Only trigger the alt text if it exists
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

def click_next_button():
    try:
        # Try to find the "Next" button using the class 'right' and click it
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "right"))
        )
        next_button.click()
        time.sleep(3)  # Wait for the next image to load
        return True  # Return True if "Next" is successfully clicked
    except Exception as e:
        print("Next button not clickable or not found, attempting to load more images...")

        try:
            # Close the current image modal by clicking on the close button
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "media-modal-close"))
            )
            close_button.click()
            print("Image modal closed. Proceeding to load more images...")
            time.sleep(3)  # Wait for the page to load

            # Count the number of images before clicking "Load More"
            initial_images = driver.find_elements(By.CSS_SELECTOR, ".attachment")
            initial_image_count = len(initial_images)
            print(f"Initial image count: {initial_image_count}")

            # Wait for the "Load More" button to be clickable
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "button.load-more.button-primary"))
            )
            load_more_button.click()
            print("Load More button clicked. Waiting for new images to load...")
            time.sleep(5)  # Wait a bit longer to allow new images to load on the page

            # Wait for new images to appear, indicating "Load More" worked
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".attachment"))
            )

            # Count the total number of images after clicking "Load More"
            new_images = driver.find_elements(By.CSS_SELECTOR, ".attachment")
            new_image_count = len(new_images)
            print(f"New image count after Load More: {new_image_count}")

            new_image_id = new_images[initial_image_count].get_attribute("data-id")
            print(f"New image ID found: {new_image_id}")

            # Find and click on the newly loaded image with the new image ID
            new_image = driver.find_element(By.CSS_SELECTOR, f'.attachment[data-id="{new_image_id}"]')
            new_image.click()
            time.sleep(5)

            # Now that the new image is clicked, fill the alt text and caption
            fill_alt_and_caption(new_image_id)

            # After filling the details, click the "Next" button again
            return click_next_button()  # Attempt to click the next button again after filling the details
        except Exception as e:
            print("Load More button not found or not clickable. Exiting.")
            return False  # If no "Load More" or "Next" button was found, return False

    return False  # Return False if the Next button was clicked or failed


# Start the login process
login_to_wp()

# Start with the initial image ID
current_image_id = initial_image_id

# Loop to process images
while True:
    if current_image_id == initial_image_id:
        # For the first image, navigate to the media item page
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
