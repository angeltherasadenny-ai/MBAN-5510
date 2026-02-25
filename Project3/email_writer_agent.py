import random


def write_email(student: dict, research: dict) -> dict:
    name = research.get("name", "Michael Zhang")

    subject_options = [
        f"Research Project Interest – {student['name']}",
        f"Research Opportunity Inquiry – {student['name']}",
        f"Student Research Interest – {student['name']}",
    ]

    opening_options = [
        f"I’m {student['name']}, a {student['program']} student at {student['university']}.",
        f"My name is {student['name']}, and I’m currently studying {student['program']} at {student['university']}.",
        f"My name is {student['name']}. I’m studying {student['program']} at {student['university']}.",
    ]

    interest_options = [
        "I wanted to ask if there may be an opportunity to work with you on a research project.",
        "I’m reaching out to ask if you might be open to having a student support you on a research project.",
        "I’m writing to express my interest in contributing to a research project you are currently working on.",
    ]

    why_options = [
        "I reviewed your faculty profile and found your work especially interesting.",
        "Your research focus strongly aligns with my interests in analytics and applied decision-making.",
        "I read your profile and was especially interested in your work applying analytics to real-world problems.",
    ]

    ask_options = [
        "If possible, I would be grateful for a short meeting to learn more about your current work and how I could contribute.",
        "If you are available, I would really appreciate the chance to meet briefly and ask about possible research opportunities.",
        "If you’re open to it, I would love to connect briefly to discuss whether there may be a way I can support a project.",
    ]

    closing_options = [
        "Thank you for your time.",
        "Thank you very much for your time and consideration.",
        "Thank you — I really appreciate it.",
    ]

    # Pick random pieces
    subject = random.choice(subject_options)

    opening = random.choice(opening_options)
    interest = random.choice(interest_options)
    why = random.choice(why_options)
    ask = random.choice(ask_options)
    closing = random.choice(closing_options)

    # Neat email formatting (paragraphs)
    body = f"""Dear Dr. {name},


{opening} {interest}

{why} {ask}

{closing}

Kind regards,  
{student['name']}
"""

    return {"subject": subject, "body": body}
