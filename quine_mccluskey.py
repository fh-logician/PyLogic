"""
Copyright (c) 2019 Jonah Pierce

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall
be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

class QM:
    """
    A QM class that simplifies a Boolean Algebraic function in either SOP (Sum of Products) format
    or POS (Product of Sums) format

    :param variables: A str of variables that the Boolean Algebra function uses
    :param values: A list of decimal values where the function evaluates to 1 (true)
    :param dont_cares: A list of decimal values for the dont cares of the function
    :param is_maxterm: Whether or not to use this QM object as a Maxterm function
    """

    class Minterm:
        """
        A Minterm class that holds combined decimal values together
        If this Minterm is acting like a Maxterm, the resulting string will be different
            Instead of being in SOP format, it will be in POS format

        :param values: The decimal values this Minterm contains
        :param variables: A str of variables that this Minterm uses
        :param is_maxterm: Whether or not this Minterm is acting like a Maxterm
        """

        def __init__(self, values, variables, *, is_maxterm = False):
            self.values = sorted(values)
            self.variables = variables
            self.is_maxterm = is_maxterm

        def __eq__(self, minterm):
            return len(minterm.variables) == len(self.variables) and minterm.values == self.values

        def __str__(self):

            # Set a compare value to get a bit pattern similar to (01-0)
            compare = self.values[0]
            bit_pattern = list(bin(compare)[2:].rjust(len(self.variables), "0"))

            # Iterate through all the decimals in the Minterm to retrieve a final bit pattern
            for decimal in self.values:

                # By getting an XOR and an AND value, we can compare the decimal value
                #   with the compare value to determine if the two numbers can be combined
                xor_value = bin(decimal ^ compare)[2:].rjust(len(self.variables), "0")
                and_value = bin(decimal & compare)[2:].rjust(len(self.variables), "0")

                # The numbers can be combined, and a "-" results from it, if the XOR value at
                #   a specific offset (based on the amount of variables) is 1
                for offset in range(len(self.variables)):
                    if xor_value[offset] == "0":
                        bit_pattern[offset] = and_value[offset]
                    else:
                        bit_pattern[offset] = "-"

            # Return a joined string of the variables ANDed in this Minterm if this Minterm
            #   is acting like a normal Minterm, other wise OR them together
            return "{}".format(" OR " if self.is_maxterm else " AND ").join([
                "{}{}".format(
                    "NOT " if bit_pattern[bit] == ("1" if self.is_maxterm else "0") else "",
                    self.variables[bit]
                )
                for bit in range(len(bit_pattern))
                if bit_pattern[bit] != "-"
            ])

        def valid(self, dont_cares):
            """
            Determines if this Minterm is invalid by checking if the values of this Minterm
            consist of only dont care values

            :param dont_cares: A list of values for the dont cares
            :return: bool
            """

            # Count all the values in this Minterm where a dont care value exists
            count = 0
            for dont_care in dont_cares:
                for value in self.values:
                    if value in dont_care.values:
                        count += 1

            # If the count of dont cares is equivalent to the length of the values, this
            #   Minterm does not matter and is therefore invalid
            return count != len(self.values)

        def combine(self, minterm):
            """
            Attempts to combine this Minterm with another Minterm

            :param minterm: The Minterm to combine this Minterm with
            :return: Minterm or None
                This will return None if the Minterm's cannot be combined
            """

            # Check to make sure that the specified Minterm has the same length of values
            #   and that the specified Minterm is not equivalent to this Minterm
            if len(self.values) != len(minterm.values) or self == minterm:
                return None

            # Iterate through all the values in the specifed Minterm
            #   if the specified Minterm has a value that is in this Minterm
            #   these Minterms cannot be combined
            for self_value in self.values:
                for minterm_value in minterm.values:
                    if self_value == minterm_value:
                        return None

            # Iterate through all the values in this Minterm and the specified Minterm
            #   at this point, the Minterms will have the same length of values
            for i in range(len(self.values)):
                count = 0

                # Do an XOR operation on each bit by shifting through offsets
                #   based on the amount of variables
                for offset in range(len(self.variables)):
                    if (self.values[i] ^ minterm.values[i]) & (1 << offset) != 0:
                        count += 1

                    # If there is more than 1 difference in between the two decimal values
                    #   this Minterm automatically cannot be combined with the specified Minterm
                    if count > 1:
                        return None

            # This Minterm can be combined with the new Minterm
            #   combine the Minterms and their values but make sure no copies of the value exist
            #   just in case
            # Then return the new combined Minterm
            new_values = []
            for value in (self.values + minterm.values):
                if value not in new_values:
                    new_values.append(value)
            return QM.Minterm(new_values, self.variables, is_maxterm = self.is_maxterm)

    def __init__(self, variables, values, *, dont_cares = [], is_maxterm = False):
        self.variables = variables
        self.is_maxterm = is_maxterm

        # Create Minterms/Maxterms out of each given value
        #   and for the dont cares
        self.values = [
            self.Minterm([value], variables, is_maxterm = is_maxterm)
            for value in sorted(values)
        ]
        self.dont_cares = [
            self.Minterm([value], variables)
            for value in sorted(dont_cares)
        ]

    def solve(self):
        """
        Solves the Boolean Algebra function and returns a string representation
        of the simplified function.

        :return: str
        """

        # Sort the Minterms by the amount of values they cover
        #   and keep track of the current function and which decimal values
        #   have been covered
        minterms = sorted(
            self.__solve(self.values + self.dont_cares),
            key = lambda minterm: len(minterm.values)
        )
        function = []
        covered = []

        # Check for all essential prime implicants by finding which values are only in 1 minterm
        for value in self.values:
            value = value.values[0]
            count = 0
            last_minterm = None
            for minterm in minterms:
                if value in minterm.values:
                    last_minterm = minterm
                    count += 1

            # The last_minterm only covers 1 value, this must be an essential prime implicant
            #   add the minterm to the function list and add all decimal values
            #   to the covered list
            if count == 1 and last_minterm:
                function.append(last_minterm)
                covered += [ value for value in last_minterm.values if value not in covered ]
                minterms.remove(last_minterm) # Remove the minterm from the minterms list
                                              # we don't want to add it to the functions list again

        # Check for the prime implicants that cover the most values in other minterms
        for value in self.values:
            value = value.values[0]
            if value not in covered:

                # Iterate through all the minterms that cover the current value
                value_minterms = []
                for minterm in minterms:
                    if value in minterm.values:
                        value_minterms.append(minterm)

                # Look for the minterm which covers the most uncovered values
                best_minterm = value_minterms[0]
                best_cover = len([ value for value in best_minterm.values if value not in covered ])
                for minterm in value_minterms:
                    minterm_cover = len([ value for value in minterm.values if value not in covered ])
                    if minterm_cover > best_cover:
                        best_minterm = minterm
                        best_cover = minterm_cover

                # Add the best_minterm to the function and remove it from the minterms
                #   we don't want to add it again
                #   Also add the covered values that the best_minterm covers
                function.append(best_minterm)
                minterms.remove(best_minterm)
                covered += [ value for value in best_minterm.values if value not in covered ]

        # Return a joined string of each Minterm in the resulting function ORed together
        #   if this QM function is a Maxterm function, AND them together
        if self.is_maxterm:
            return " AND ".join([ "({})".format(str(minterm)) for minterm in function ])
        return " OR ".join([str(minterm) for minterm in function])

    def __solve(self, minterms, unused = []):
        """
        A helper method that recursively simplifies each Minterm with one another until it can't
        be simplified any more. This method returns a list of unused Minterms

        :param minterms: A list of Minterms to combine
        :param unused: Any unused minterms that must be passed through which will make up the essential prime implicants and prime implicants
        :return: list
        """

        # Check if there are no minterms, return all the unused values
        if len(minterms) == 0:
            return unused

        # There are more than 1 minterm
        else:

            # Keep track of all unused and combined Minterms
            used = []
            combined = []

            # Compare each Minterm with every other Minterm to see if they can be combined
            for i in range(len(minterms)):
                m_one = minterms[i]
                for j in range(i + 1, len(minterms)):
                    m_two = minterms[j]
                    m_combine = m_one.combine(m_two)

                    # If they can be combined, keep track of the used minterms
                    #   and add the combined Minterm if it does not already exist
                    if m_combine is not None:
                        used.append(m_one)
                        used.append(m_two)
                        if m_combine not in combined:
                            combined.append(m_combine)

            # Find all unused Minterms that come from the minterms list and the unused list
            #   for every pass that happens in the __solve method, the unused Minterms cannot
            #   be combined with the previous group since the Minterm values are of different lengths
            unused = [ minterm for minterm in (minterms + unused) if (minterm not in used and minterm.valid(self.dont_cares))]
            return self.__solve(combined, unused)
