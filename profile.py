class User:
  def __init__(self, name: str = "Human", student_id: str = "ID", password: str = "Pass") -> None:
    """Creates a user object with the given name, student_id, and password.

    Args:
        name (str): How the bot calls the user.
        student_id (str): Student's Official ID
        password (str): Password for the student's account
    """
    self.name = name
    self.student_id = student_id
    self.password = password