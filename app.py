from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
import re

# Load .env variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["998P"]
users = db["users"]
subscriptions = db["subscriptions"]
registrations = db["registrations"]
contact_messages = db["contact_messages"]
survey_responses = db["survey_responses"]

def generate_trn():
    last_trn_doc = survey_responses.find_one(sort=[("trn", -1)])
    if last_trn_doc and last_trn_doc.get("trn"):
        last_trn = last_trn_doc["trn"]
        match = re.match(r"T-(\d{5})", last_trn)
        if match:
            serial_number = int(match.group(1))
            new_serial_number = serial_number + 1
            return f"T-{new_serial_number:05d}"
    return "T-02805"

# ---------------- Helper Functions for Validation ----------------
def validate_name(name):
    if not re.match(r"^[a-zA-Z\s\.]+" , name):
        return "Invalid name format. Only letters, spaces, and periods are allowed."
    return None

def validate_email(email):
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return "Invalid email format."
    return None

def validate_mobile(mobile):
    if not re.match(r"^\d{10}$", mobile):
        return "Invalid mobile number format. Must be 10 digits."
    return None

# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html", current_path=request.path)

@app.route("/about-us")
def about_us():
    return render_template("about-us.html", current_path=request.path)

@app.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        message = request.form.get("message")

        if not all([name, email, mobile, message]):
            return jsonify({"status": "danger", "message": "All fields are required!"}), 400

        name_error = validate_name(name)
        email_error = validate_email(email)
        mobile_error = validate_mobile(mobile)

        if name_error:
            return jsonify({"status": "danger", "message": name_error}), 400

        if email_error:
            return jsonify({"status": "danger", "message": email_error}), 400

        if mobile_error:
            return jsonify({"status": "danger", "message": mobile_error}), 400

        contact_data = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "message": message,
            "createdAt": datetime.utcnow()
        }
        contact_messages.insert_one(contact_data)
        return jsonify({"status": "success", "message": "Your message has been sent successfully!"}), 200
    return render_template("contact-us.html", current_path=request.path)

@app.route("/professionals")
def professionals():
    return render_template("professionals.html", current_path=request.path)

@app.route("/products-and-services")
def products_and_services():
    return render_template("products-and-services.html", current_path=request.path)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return jsonify({"status": "danger", "message": "Permanent registration is currently suspended. Please fill the survey form to get a temporary registration number."}), 401

    return render_template("register.html", current_path=request.path)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([email, password]):
            return jsonify({"status": "danger", "message": "Both email and password are required!"}), 400
        else:
            return jsonify({"status": "danger", "message": "Access restricted. Wrong credentials or Permanent Membership required to log in."}), 401

    return render_template("login.html", current_path=request.path)


@app.route("/submit-survey", methods=["POST"])
def submit_survey():
    try:
        # Personal Details
        full_name = request.form.get("fullName")
        mobile_number = request.form.get("mobileNumber")
        email_id = request.form.get("emailId")
        location = request.form.get("location")
        registration_no = request.form.get("registrationNo")
        referred_by = request.form.get("referredBy")

        # Check if emailId or mobileNumber already exists
        if survey_responses.find_one({"$or": [{"emailId": email_id}, {"mobileNumber": mobile_number}]}):
            return jsonify({"status": "danger", "message": "Email ID or Mobile Number is already registered."}), 409 # Conflict

        # Section A: About You
        practicing_as = request.form.getlist("practicingAs")
        how_operate = request.form.get("howOperate")

        # Extract license numbers
        ca_license = request.form.get("caLicense")
        cs_license = request.form.get("csLicense")
        lawyer_license = request.form.get("lawyerLicense")
        ip_license = request.form.get("ipLicense")
        cma_license = request.form.get("cmaLicense")
        valuer_license = request.form.get("valuerLicense")

        # New Section A Questions
        annual_income = request.form.get("annualIncome")
        practice_location = request.form.get("practiceLocation")
        experience = request.form.get("experience")
        team_members = request.form.get("teamMembers")
        junior_compensation = request.form.get("juniorCompensation")

        # Section B: Understanding Professional Challenges and Discussing Probable Solutions
        pain_points = request.form.getlist("painPoints")
        other_pain_points_text = request.form.get("otherPainPointsText")

        junior_issues = request.form.getlist("juniorIssues")
        other_junior_issues_text = request.form.get("otherJuniorIssuesText")

        # Manual Activities (Existing)
        data_entry = request.form.get("dataEntry")
        drafting_manual = request.form.get("draftingManual")
        calculations = request.form.get("calculations")
        research = request.form.get("research")
        reviewing_work = request.form.get("reviewingWork")

        it_tool_barriers = request.form.getlist("itToolBarriers")
        other_it_barriers_text = request.form.get("otherITBarriersText")

        # Section C: Impact of AI on my Practice (Existing aiChallenges, New aiView)
        ai_challenges = request.form.getlist("aiChallenges")
        other_ai_challenges_text = request.form.get("otherAIChallengesText")
        ai_view = request.form.get("aiView")

        # Section D: Budget Expectations for Tech-enabled Growth
        ai_software_likelihood = request.form.get("aiSoftwareLikelihood")
        referral_fee_likelihood = request.form.get("referralFeeLikelihood")

        # Validate required fields with specific messages
        if not (full_name and mobile_number and email_id and location):
            return jsonify({"status": "danger", "message": "Personal details (Full Name, Mobile Number, Email ID, Location) are required!"}), 400

        if not practicing_as:
            return jsonify({"status": "danger", "message": "Question 1 is empty. Please complete it before submitting the survey."}), 400

        # Validate if selected practicingAs checkboxes have corresponding license numbers if required
        for profession in practicing_as:
            license_field = request.form.get(f"{profession.lower()}License")
            if not license_field:
                return jsonify({"status": "danger", "message": f"Please enter the license number for {profession}."}), 400

        if not how_operate:
            return jsonify({"status": "danger", "message": "Question 2 is empty. Please complete it before submitting the survey."}), 400

        if not annual_income:
            return jsonify({"status": "danger", "message": "Question 3 is empty. Please complete it before submitting the survey."}), 400

        if not practice_location:
            return jsonify({"status": "danger", "message": "Question 4 is empty. Please complete it before submitting the survey."}), 400

        if not experience:
            return jsonify({"status": "danger", "message": "Question 5 is empty. Please complete it before submitting the survey."}), 400

        if not team_members:
            return jsonify({"status": "danger", "message": "Question 6 is empty. Please complete it before submitting the survey."}), 400

        if not junior_compensation:
            return jsonify({"status": "danger", "message": "Question 7 is empty. Please complete it before submitting the survey."}), 400

        if not pain_points:
            return jsonify({"status": "danger", "message": "Question 8 is empty. Please complete it before submitting the survey."}), 400

        if "otherPainPoints" in pain_points and not other_pain_points_text:
            return jsonify({"status": "danger", "message": "Please specify the other pain point in question 8."}), 400

        if not junior_issues:
            return jsonify({"status": "danger", "message": "Question 9 is empty. Please complete it before submitting the survey."}), 400
        
        if "otherJuniorIssues" in junior_issues and not other_junior_issues_text:
            return jsonify({"status": "danger", "message": "Please specify the other junior issue in question 9."}), 400

        if not (data_entry and drafting_manual and calculations and research and reviewing_work):
            return jsonify({"status": "danger", "message": "Question 10 is empty. Please complete it before submitting the survey."}), 400

        if not it_tool_barriers:
            return jsonify({"status": "danger", "message": "Question 11 is empty. Please complete it before submitting the survey."}), 400
        
        if "otherITBarriers" in it_tool_barriers and not other_it_barriers_text:
            return jsonify({"status": "danger", "message": "Please specify the other IT tool barrier in question 11."}), 400

        if not ai_challenges:
            return jsonify({"status": "danger", "message": "Question 12 is empty. Please complete it before submitting the survey."}), 400

        if "otherAIChallenges" in ai_challenges and not other_ai_challenges_text:
            return jsonify({"status": "danger", "message": "Please specify the other AI challenge in question 12."}), 400

        if not ai_view:
            return jsonify({"status": "danger", "message": "Question 13 is empty. Please complete it before submitting the survey."}), 400

        if not ai_software_likelihood:
            return jsonify({"status": "danger", "message": "Question 14 is empty. Please complete it before submitting the survey."}), 400

        if not referral_fee_likelihood:
            return jsonify({"status": "danger", "message": "Question 15 is empty. Please complete it before submitting the survey."}), 400

        # Validate name, email, mobile (existing validations)
        name_error = validate_name(full_name)
        email_error = validate_email(email_id)
        mobile_error = validate_mobile(mobile_number)

        if name_error:
            return jsonify({"status": "danger", "message": name_error}), 400
        if email_error:
            return jsonify({"status": "danger", "message": email_error}), 400
        if mobile_error:
            return jsonify({"status": "danger", "message": mobile_error}), 400

        # Construct practicing_as_details to store both selected professions and their licenses
        practicing_as_details = {}
        for profession in practicing_as:
            license_number = request.form.get(f"{profession.lower()}License")
            practicing_as_details[profession] = license_number if license_number else ""

        survey_data = {
            "fullName": full_name,
            "mobileNumber": mobile_number,
            "emailId": email_id,
            "location": location,
            "registrationNo": registration_no,
            "referredBy": referred_by,
            "practicingAs": practicing_as_details,
            "howOperate": how_operate,
            "annualIncome": annual_income,
            "practiceLocation": practice_location,
            "experience": experience,
            "teamMembers": team_members,
            "juniorCompensation": junior_compensation,
            "painPoints": pain_points,
            "otherPainPointsText": other_pain_points_text if "otherPainPoints" in pain_points else "",
            "juniorIssues": junior_issues,
            "otherJuniorIssuesText": other_junior_issues_text if "otherJuniorIssues" in junior_issues else "",
            "manualActivities": {
                "dataEntry": data_entry,
                "draftingManual": drafting_manual,
                "calculations": calculations,
                "research": research,
                "reviewingWork": reviewing_work
            },
            "itToolBarriers": it_tool_barriers,
            "otherITBarriersText": other_it_barriers_text if "otherITBarriers" in it_tool_barriers else "",
            "aiChallenges": ai_challenges,
            "otherAIChallengesText": other_ai_challenges_text if "otherAIChallenges" in ai_challenges else "",
            "aiView": ai_view,
            "aiSoftwareLikelihood": ai_software_likelihood,
            "referralFeeLikelihood": referral_fee_likelihood,
            "createdAt": datetime.utcnow()
        }

        trn = generate_trn()
        survey_data["trn"] = trn

        survey_responses.insert_one(survey_data)
        return jsonify({"status": "success", "message": "Survey submitted successfully! Your Temporary Registration Number (TRN) is", "trn": trn}), 200
    except Exception as e:
        return jsonify({"status": "danger", "message": f"Error submitting survey: {e}"}), 500

# ---------- Subscription ----------
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email:
        email_error = validate_email(email)
        if email_error:
            return jsonify({"status": "error", "message": email_error}), 400

        if subscriptions.find_one({"email": email}):
            return jsonify({"status": "info", "message": "You are already subscribed."}), 200
        else:
            subscriptions.insert_one({"email": email, "createdAt": datetime.utcnow()})
            return jsonify({"status": "success", "message": "Successfully subscribed."}), 200
    else:
        return jsonify({"status": "danger", "message": "Please enter a valid email address."}), 400

@app.route("/thank-you-professionals")
def thank_you_professionals():
    return render_template("thank-you-professionals.html", current_path=request.path)

@app.route("/platform-t&c")
def platform_t_and_c():
    return render_template("platform-t&c.html", current_path=request.path)

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html", current_path=request.path)

@app.route("/survey-t&c")
def survey_t_and_c():
    return render_template("survey-t&c.html", current_path=request.path)

# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
