def approve_email(draft: dict) -> str:
    """
    Returns:
      "y" -> approved
      "n" -> rejected (generate new draft)
      "q" -> quit
    """
    print("\n--- Email Draft ---\n")
    print("Subject:", draft["subject"])
    print("\n" + draft["body"])
    print("-------------------\n")

    while True:
        answer = input("Send this email? (y = send / n = regenerate / q = quit): ").strip().lower()
        if answer in ["y", "n", "q"]:
            return answer
        print("Please type y, n, or q.")
