import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

previous_statuses = {}


def get_class_status(driver, crn):
    classes = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for row in soup.select('tbody tr[data-id]'):
        class_info = {}
        class_info['courseReferenceNumber'] = row['data-id']

        for cell in row.find_all('td'):
            if 'data-property' in cell.attrs:
                property_name = cell['data-property']
                class_info[property_name] = cell.get_text(strip=True)
            elif 'data-id' in cell.attrs:
                property_name = 'link'
                class_info[property_name] = cell.find('a')['href']

        status_cell = row.find('td', {'data-property': 'status'})
        if status_cell:
            class_info['status'] = status_cell.get_text(strip=True)

        if class_info['courseReferenceNumber'] == crn:
            classes.append(class_info)
            print(f"Tracking class with CRN: {crn}, Class Title: {class_info.get('courseTitle', 'Unknown')}")
            break

    return classes


def is_class_full(status):
    try:
        return "0 of" in status or "FULL" in status.upper()
    except (IndexError, ValueError):
        print(f"Error parsing status: {status}")
        return False


def notify_user(class_name, crn):
    sender_email = config.SENDER_EMAIL
    receiver_email = config.RECEIVER_EMAIL
    password = config.EMAIL_PASSWORD

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Class Spot Update: {class_name} (CRN: {crn})"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Class {class_name} with CRN {crn} now has seats available."
    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Notification sent to", receiver_email)
    except smtplib.SMTPRecipientsRefused:
        print(f"Recipient address rejected: {receiver_email}")
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"SMTP Authentication Error: {auth_error}")
    except Exception as e:
        print(f"Failed to send notification: {e}")


def open_new_tab(driver, url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "s2id_txt_subject")))


def enter_course_info(driver, subject, course_number):
    subject_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "s2id_txt_subject")))
    subject_dropdown.click()
    subject_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "s2id_autogen1")))
    subject_input.send_keys(subject)
    subject_input.send_keys(Keys.RETURN)
    time.sleep(2)

    course_number_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txt_courseNumber")))
    course_number_input.send_keys(course_number)
    course_number_input.send_keys(Keys.RETURN)
    time.sleep(2)


def check_classes(driver, classes_to_track):
    global previous_statuses
    base_url = "https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"

    driver.get(base_url)
    time.sleep(2)

    browse_classes_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "classSearchLink")))
    browse_classes_link.click()
    time.sleep(2)

    term_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "select2-choice")))
    term_dropdown.click()
    time.sleep(2)

    fall_2024_option = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='202408']")))
    fall_2024_option.click()
    time.sleep(2)

    continue_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "term-go")))
    continue_button.click()
    time.sleep(2)

    if classes_to_track:
        crn, subject, course_number = classes_to_track[0]
        enter_course_info(driver, subject, course_number)

    for crn, subject, course_number in classes_to_track[1:]:
        open_new_tab(driver, base_url)
        enter_course_info(driver, subject, course_number)

    while classes_to_track:
        for index, (crn, subject, course_number) in enumerate(classes_to_track):
            driver.switch_to.window(driver.window_handles[index])
            driver.refresh()

            enter_course_info(driver, subject, course_number)

            classes = get_class_status(driver, crn)
            for class_info in classes:
                class_id = class_info.get('courseReferenceNumber')
                class_name = class_info.get('courseTitle')
                current_status = class_info.get('status', '')

                if class_id:
                    previous_status = previous_statuses.get(class_id, '')
                    if not is_class_full(current_status):
                        print(f"Spot available for class {class_name} (CRN: {crn})!")
                        notify_user(class_name, crn)
                        classes_to_track.pop(index)
                        previous_statuses.pop(class_id, None)
                        break

                    previous_statuses[class_id] = current_status

        if not classes_to_track:
            print("No more classes to track. Terminating the program.")
            break

        time.sleep(5)

    return False


if __name__ == "__main__":
    classes_to_track = []

    while True:
        crn = input("Enter the CRN of the class you want to track: ")
        subject = input("Enter the subject of the class you want to track: ").strip()
        course_number = input("Enter the course number of the class you want to track: ").strip()

        classes_to_track.append((crn, subject, course_number))

        more_classes = input("Would you like to track another class? (y/n): ")
        if more_classes.lower() != 'y':
            break

    driver_path = config.CHROME_DRIVER_PATH
    options = webdriver.ChromeOptions()
    options.binary_location = config.CHROME_BINARY_PATH
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    print("Starting to track classes...")

    try:
        check_classes(driver, classes_to_track)
    finally:
        driver.quit()
