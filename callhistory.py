from call import Call


class CallHistory:
    """A class for recording incoming and outgoing calls for a particular number

    === Public Attributes ===
    incoming_calls:
         Dictionary of incoming calls. Keys are tuples containing a month and a
         year, values are a List of Call objects for that month and year.
    outgoing_calls:
         Dictionary of outgoing calls. Keys are tuples containing a month and a
         year, values are a List of Call objects for that month and year.
    """
    incoming_calls: dict[tuple[int, int], list[Call]]
    outgoing_calls: dict[tuple[int, int], list[Call]]

    def __init__(self) -> None:
        """ Create an empty CallHistory.
        """
        self.outgoing_calls = {}
        self.incoming_calls = {}

    def register_outgoing_call(self, call: Call) -> None:
        """ Register a Call <call> into this outgoing call history
        """
        month = call.time.month
        year = call.time.year
        self.outgoing_calls.setdefault((month, year), []).append(call)

    def register_incoming_call(self, call: Call) -> None:
        """ Register a Call <call> into this incoming call history
        """
        month = call.time.month
        year = call.time.year
        self.incoming_calls.setdefault((month, year), []).append(call)

    # ----------------------------------------------------------
    # NOTE: You do not need to understand the implementation of
    # the following methods, to be able to solve this assignment
    # but feel free to read them to get a sense of what these do.
    # ----------------------------------------------------------

    def get_monthly_history(self, month: int = None, year: int = None) -> \
            tuple[list[Call], list[Call]]:
        """ Return all outgoing and incoming calls for <month> and <year>,
        as a Tuple containing two lists in the following order:
        (outgoing calls, incoming calls)

        If <month> and <year> are both None, then return all calls from this
        call history.

        Precondition:
        - <month> and <year> are either both specified, or are both missing/None
        - if <month> and <year> are specified (non-None), they are both valid
        monthly cycles according to the input dataset
        """
        monthly_history = ([], [])
        if month is not None and year is not None:
            if (month, year) in self.outgoing_calls:
                for call in self.outgoing_calls[(month, year)]:
                    monthly_history[0].append(call)

            if (month, year) in self.incoming_calls:
                for call in self.incoming_calls[(month, year)]:
                    monthly_history[1].append(call)
        else:
            for entry in self.outgoing_calls:
                for call in self.outgoing_calls[entry]:
                    monthly_history[0].append(call)
            for entry in self.incoming_calls:
                for call in self.incoming_calls[entry]:
                    monthly_history[1].append(call)
        return monthly_history


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'call'
                                               ''
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
