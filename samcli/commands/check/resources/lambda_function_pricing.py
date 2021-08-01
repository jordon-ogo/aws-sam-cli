"""
Object to contain Lambda function pricing info.
"""
from typing import List, Tuple
import click

from samcli.commands.check.lib.ask_question import ask


class LambdaFunctionPricing:
    """
    Pricing for lambda funcitons will be hanled differently to all other resources.
    Lambda funciton priocing is based off of the performance of all lambda function,
    not an individual one. Therefore, all of that data can eb stored in a class object
    rather than a random lambda function object. This data gets stored in the graph.
    - number_of_requests are the expected amount of requests all lambda funcitons
      will experience in a given month
    - average_duration is the average duration of all lambda functions
    - allocated_memory [128MB - 10GB] is how much memory the user wants to allocate
      to their lambda funcitons
    - allocated_memory_unit [MB, GB] is the unit of memory for the amount entered
    """

    number_of_requests: int
    average_duration: int
    allocated_memory: float
    allocated_memory_unit: str

    _max_num_requests: int
    _min_memory_amount: int
    _max_memory_amount: int
    _max_duration: int

    def __init__(self):
        self.number_of_requests: int = None
        self.average_duration: int = None
        self.allocated_memory: float = None
        self.allocated_memory_unit: str = None

        self._max_num_requests: int = 1000000000000000000000
        self._min_memory_amount: int = 128
        self._max_memory_amount: int = 10000
        self._max_duration: int = 900000

    def ask_lambda_function_questions(self) -> None:
        """Lambda function pricing questions"""

        user_input_requests = ask(
            "What are the total number of requests expected from all lambda functions in a given month?",
            1,
            self._max_num_requests,
        )
        self.number_of_requests = user_input_requests

        user_input_duration = ask(
            "What is the expected average duration of all lambda functions (ms)?", 1, self._max_duration
        )
        self.average_duration = user_input_duration

        user_input_memory, user_input_unit = self._ask_memory(
            'Enter the amount of memory allocated (128MB - 10GB), followed by a ":", '
            "followed by a valid unit of measurement [MB|GB]"
        )
        self.allocated_memory = user_input_memory
        self.allocated_memory_unit = user_input_unit

    def _validate_memory_input(self, user_input_split: List) -> bool:
        """Checks if user input correct memory amount and unit

        Args:
            user_input_split (List): User enterd data [memory_amount, memory_unit]

        Returns:
            [type]: [description]
        """
        if len(user_input_split) != 2:
            click.echo("Please enter a valid input.")
            return False

        memory_amount = user_input_split[0]
        memory_unit = user_input_split[1]
        valid_units = ["MB", "GB"]

        try:
            float(memory_amount)
        except ValueError:  # Not a valid number
            click.echo("Please enter a valid amount of memory.")
            return False

        if memory_unit not in valid_units:
            click.echo("Please enter a valid memory unit.")
            return False

        # At this point, memory_amount and memory_unit are both valid inputs. Now test if memory_amount is within range

        memory_amount_float = float(memory_amount)

        if memory_unit == "GB":
            # Convert to MB for testing range
            memory_amount_float *= 1000

        if (
            memory_amount_float < self._min_memory_amount or memory_amount_float > self._max_memory_amount
        ):  # units are in MB
            click.echo("Please enter a valid amount of memory within the range.")
            return False

        return True

    def _ask_memory(self, question: str) -> Tuple[float, str]:
        """Ask user memory pricing question for lambda functions

        Args:
            question (str): The question to ask the user

        Returns:
            str: memory amount and unit
        """
        valid_user_input = False
        user_input_split = []
        while not valid_user_input:
            user_input = click.prompt(text=question, type=str)
            user_input_split = user_input.split(":")
            if self._validate_memory_input(user_input_split):
                valid_user_input = True

        return user_input_split[0], user_input_split[1]
