
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

app = Flask(__name__)

@app.route("/track", methods=["GET"])
def track():
    tracking_code = request.args.get("code")
    if not tracking_code:
        return jsonify({"error": "يرجى إرسال رقم التتبع عبر ?code="}), 400

    try:
        print("🚀 بدء التتبع لرقم:", tracking_code)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        print("🌍 فتح موقع البريد المصري...")
        driver.get("https://egyptpost.gov.eg/ar-eg/home/eservices/track-and-trace/")
        time.sleep(5)

        input_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@maxlength='13']")))
        input_box.clear()
        input_box.send_keys(tracking_code)

        print("🔘 الضغط على زر التتبع...")
        track_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "custBtn")))
        track_btn.click()

        print("⏳ في انتظار النتائج...")
        time.sleep(7)

        statuses = driver.find_elements(By.CLASS_NAME, "order__container")
        tracking_info = []

        for status in statuses:
            try:
                step_type = status.find_element(By.CLASS_NAME, "process").text
                details = [e.text for e in status.find_elements(By.TAG_NAME, "p") if e.text.strip()]
                tracking_info.append({
                    "المرحلة": step_type,
                    "التفاصيل": details[1:]
                })
            except Exception as step_err:
                continue

        driver.quit()
        return jsonify({"code": tracking_code, "result": tracking_info})

    except TimeoutException:
        driver.quit()
        return jsonify({"error": "انتهى وقت الانتظار. ربما الموقع تغيّر أو بطئ جداً."}), 500
    except Exception as e:
        driver.quit()
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
