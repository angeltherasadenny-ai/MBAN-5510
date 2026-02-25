import os
from dotenv import load_dotenv

from research_agent import research_michael
from email_writer_agent import write_email
from approval_agent import approve_email
from email_sender import send_email


def main():
    load_dotenv()

    profile_url = os.getenv("MICHAEL_PROFILE_URL", "").strip()
    if not profile_url:
        print("ERROR: MICHAEL_PROFILE_URL missing in .env")
        return

    student = {
        "name": os.getenv("STUDENT_NAME", "Your Name"),
        "program": os.getenv("STUDENT_PROGRAM", "MBAN"),
        "university": os.getenv("STUDENT_UNIVERSITY", "Saint Mary's University"),
    }

    test_receiver = os.getenv("TEST_RECEIVER")

    research = research_michael(profile_url)

    while True:
        draft = write_email(student, research)

        decision = approve_email(draft)

        if decision == "y":
            send_email(draft["subject"], draft["body"], test_receiver)
            break

        if decision == "n":
            print("Okay — generating a new draft...\n")
            continue

        if decision == "q":
            print("Cancelled. Email not sent.")
            break


if __name__ == "__main__":
    main()