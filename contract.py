import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class and should not be directly instantiated.

    Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class MTMContract(Contract):
    """ Contract with no end date, no initial term deposit, and no free minutes.
    """
    start: datetime.date
    bill: Optional[Bill]

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """
        Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        bill.set_rates("MTM", MTM_MINS_COST)


class TermContract(Contract):
    """Contract with a start and end date, commitment required until end date.
    Includes an initial large term deposit added to the first month's bill.
    Early cancellation forfeits the deposit, while completion
    returns the deposit to the customer.

    === Public Attributes ===
    end:
        ending date for the contract, the contract can go past this date.
    commit:
        tracks if term commitment period has been completed.

    === Representation Invariants ===
    end > start
    """
    start: datetime.date
    bill: Optional[Bill]
    end: datetime.date
    commit: bool

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """Create a TermContract with an <end> date and
        <start> date, which starts as inactive.
        The <commit> parameter is set to False by default.
        """
        Contract.__init__(self, start)
        self.end = end
        self.commit = False

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """Advance to a new month in the contract, corresponding to <month>
        and <year>.This may be the first month of the contract.
        Store the <bill> argument in the contract and set the appropriate rate
        per minute and fixed cost.
        -If <month> and <year> match the <end> date’s
        month and year, set <commit> to True.
        """
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(TERM_DEPOSIT)

        if month == self.end.month and year == self.end.year:
            self.commit = True

        self.bill = bill
        bill.set_rates("TERM", TERM_MINS_COST)
        bill.add_fixed_cost(TERM_MONTHLY_FEE)

    def cancel_contract(self) -> float:
        """
        Return the amount owed in order to close the phone line associated
        with this TermContract. Return the deposit to the customer
        iff <commit> is True. Otherwise, forfeit the deposit.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """
        cost = self.bill.get_cost()
        if self.commit:
            cost -= TERM_DEPOSIT
        self.start = None
        self.end = None
        return cost

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        free = TERM_MINS - self.bill.free_min
        call_duration = ceil(call.duration / 60.0)

        if free > 0:
            used_free = min(call_duration, free)
            self.bill.add_free_minutes(used_free)
            self.bill.add_billed_minutes(call_duration - used_free)
        else:
            self.bill.add_billed_minutes(call_duration)


class PrepaidContract(Contract):
    """A pre-paid Contract that has a start date, no end date,
    and an associated balance.

    === Public Attributes ===
    balance:
        A balance on account associated with this contract.
    """
    start: datetime.date
    bill: Optional[Bill]
    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        """Create a PrepaidContract with the <start> date and
        set negative <balance> as initial credit.

        Precondition:
        - balance >= 0
        """
        Contract.__init__(self, start)
        self.balance = -1 * balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """Advance to a new month in the contract.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute along with any carry-over balance.

        -If <balance> has less than a credit of $10, add $25 of credit.
        """
        if self.bill:
            self.balance = self.bill.get_cost()
        if self.balance > -10:
            self.balance -= 25

        self.bill = bill
        bill.add_fixed_cost(self.balance)
        bill.set_rates("PREPAID", PREPAID_MINS_COST)

    def cancel_contract(self) -> float:
        """Return the amount owed in order to close the phone line associated
        with this PrepaidContract.

        -If balance is non-negative, return the amount owed.
        -If balance is negative, return 0.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """
        self.start = None
        cost = self.bill.get_cost()
        if self.bill.get_cost() < 0:
            cost = 0
        self.balance = 0
        return cost


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
