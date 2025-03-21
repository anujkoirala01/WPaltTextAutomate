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
    
    # Click on the tab with data-tab-slug="tour-settings"
    try:
        tab_element = driver.find_element(By.CSS_SELECTOR, '[data-tab-slug="tour-settings"]')
        tab_element.click()
        print('Tab clicked successfully!')
    except Exception as e:
        print('Error clicking the tour-settings tab:', e)
        return

    # Wait for content to load
    time.sleep(3)

    # Get the price input field and clean up the value
    try:
        price_input = driver.find_element(By.CSS_SELECTOR, '[data-slug="tour-price-text"]')
        if price_input and price_input.get_attribute('value'):
            price_value = price_input.get_attribute('value').replace('$', '')  # Clean up the $ symbol
            print('Price value:', price_value)
            price = float(price_value)  # Convert the price value to a float
            print('Price as a number:', price)
    except Exception as e:
        print('Error getting the price input:', e)
        return

    # Click on the tab with data-tab-slug="date-price"
    try:
        date_price_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab-slug="date-price"]')
        date_price_tab.click()
        print('Date price tab clicked.')
    except Exception as e:
        print('Error clicking the date-price tab:', e)
        return

    # Wait for the date price tab content to load
    time.sleep(3)

    # Click on the element with class="tourmaster-html-option-tabs-template-title"
    try:
        option_title = driver.find_element(By.CSS_SELECTOR, '.tourmaster-html-option-tabs-template-title')
        option_title.click()
        print('Option title clicked.')
    except Exception as e:
        print('Error clicking the option title:', e)
        return

    # Wait for the option content to load
    time.sleep(3)

    # Uncheck the checkbox for "2024" if it's checked
    try:
        year2024_checkbox = driver.find_element(By.CSS_SELECTOR, '[data-tabs-slug="year"][value="2024"]')
        if year2024_checkbox and year2024_checkbox.is_selected():
            year2024_checkbox.click()
            print('Year 2024 checkbox unchecked.')
    except Exception as e:
        print('Error unchecking year 2024 checkbox:', e)

    # Click on the checkbox for "2026" if it's not already clicked
    try:
        year2026_checkbox = driver.find_element(By.CSS_SELECTOR, '[data-tabs-slug="year"][value="2026"]')
        if year2026_checkbox and not year2026_checkbox.is_selected():
            year2026_checkbox.click()
            print('Year 2026 checkbox clicked.')
    except Exception as e:
        print('Error clicking year 2026 checkbox:', e)

    # Click on the second package tab if it exists
    try:
        package_tabs = driver.find_elements(By.CSS_SELECTOR, '.tourmaster-html-option-tabs-template-title')
        if len(package_tabs) > 1:
            package_tabs[1].click()  # Index 1 refers to the second element
            print('Second package tab clicked.')
    except Exception as e:
        print('Error clicking the second package tab:', e)
        return

    # Wait for the content to load after clicking the second package tab
    time.sleep(3)

    # Click on the input field with data-tabs-slug="person-price" and set the value
    try:
        person_price_input = driver.find_element(By.CSS_SELECTOR, '[data-tabs-slug="person-price"]')
        person_price_input.clear()  # Clear any existing value
        person_price_input.send_keys(price_value)  # Set the price value in the input field
        print('Price value passed into person-price input:', price_value)
    except Exception as e:
        print('Error setting person price input:', e)

    # Trigger change event to simulate user interaction (if required)
    try:
        person_price_input.send_keys(Keys.TAB)  # Simulate tabbing away to trigger any necessary events
    except Exception as e:
        print('Error triggering input change event:', e)

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
    # Get the post ID from the user input
    post_id = input("Please enter the WordPress Post ID (or type 'exit' to quit): ")
    
    if post_id.lower() == 'exit':
        print("Exiting the script.")
        break  # Exit the loop if the user types 'exit'
    
    # Pass the post ID dynamically when performing actions
    perform_actions(post_id)

    # Hold the browser open for 10 seconds so you can verify if it worked
    print("Waiting for 10 seconds to verify the changes...")
    time.sleep(10)

# Close the browser after the loop finishes (if user exits)
driver.quit()
