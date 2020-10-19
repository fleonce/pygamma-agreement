#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2020 CoML

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Rachid RIAD & Hadrien TITEUX
"""
##########
Alignement and disorder
##########

"""
from abc import ABCMeta, abstractmethod
from collections import Counter
from typing import List, Tuple, Optional
from typing import TYPE_CHECKING

import numpy as np

from .dissimilarity import AbstractDissimilarity

if TYPE_CHECKING:
    from .continuum import Continuum, Unit, Annotator

UnitsTuple = Tuple[Tuple['Annotator', 'Unit']]


class SetPartitionError(Exception):
    """Exception raised for errors in the partition of units of continuum.

    Attributes:
        message -- explanation of the error
    """


class AbstractAlignment(metaclass=ABCMeta):

    @property
    @abstractmethod
    def disorder(self) -> float:
        """Compute the disorder for the alignement

        >>> aligment.disorder
        ... 0.123

        """

    @abstractmethod
    def compute_disorder(self, dissimilarity: AbstractDissimilarity) -> float:
        """Compute the disorder for that alignment"""


class UnitaryAlignment:
    """Unitary Alignment

    Parameters
    ----------
    n_tuple :
        n-tuple where n is the number of annotators of the continuum
        This is a list of (annotator, segment) couples
    dissimilarity :
        combined_dissimilarity
    """

    def __init__(self, n_tuple: UnitsTuple):
        self._n_tuple = n_tuple
        self._disorder: Optional[float] = None

    @property
    def n_tuple(self):
        return self._n_tuple

    @n_tuple.setter
    def n_tuple(self, n_tuple: UnitsTuple):
        self._n_tuple = n_tuple
        self._disorder = None

    @property
    def disorder(self) -> float:
        if self._disorder is None:
            raise ValueError("Disorder hasn't been computed. "
                             "Call `compute_disorder()` first to compute it.")
        else:
            return self._disorder

    def compute_disorder(self, dissimilarity: AbstractDissimilarity):
        # building a fake continuum
        from .continuum import Continuum
        continuum = Continuum()
        for annotator, unit in self._n_tuple:
            continuum.add(annotator, unit.segment, unit.annotation)

        disorder_args = dissimilarity.build_args(continuum)
        unit_ids = np.zeros(len(self._n_tuple), dtype=np.int32)
        unit_ids = unit_ids.reshape((1, len(self._n_tuple)))
        self._disorder = dissimilarity(unit_ids, *disorder_args)[0]
        return self._disorder


class Alignment(AbstractAlignment):
    """Alignment

    Parameters
    ----------
    continuum :
        Continuum where the alignment is from
    set_unitary_alignments :
        set of unitary alignments that make a partition of the set of
        units/segments
    """

    def __init__(self,
                 continuum: 'Continuum',
                 set_unitary_alignments: List[UnitaryAlignment]):
        self.set_unitary_alignments = set_unitary_alignments
        self.continuum = continuum
        self._disorder: Optional[float] = None

        # set partition tests for the unitary alignments
        # TODO : this has to be tested
        # TODO: maybe check for temporal coherence of each "tier" (seg n < seg n + 1)
        # TODO: check that each unitary alignment has the same number of annotators
        continuum_tuples = set()
        for annotator, units in self.continuum:
            continuum_tuples.update(set((annotator, segment) for segment in units.key()))

        alignment_tuples = list()
        for unitary_alignment in self.set_unitary_alignments:
            for (annotator, unit) in unitary_alignment.n_tuple:
                alignment_tuples.append((annotator, unit.segment))

        # let's first look for missing ones, then for repeated assignments
        missing_tuples = set(alignment_tuples) - continuum_tuples
        if missing_tuples:
            repeated_tuples_str = ', '.join(f"{annotator}->{segment}"
                                            for annotator, segment in missing_tuples)

            raise SetPartitionError(f'{repeated_tuples_str} '
                                    f'not in the set of unitary alignments')

        tuples_counts = Counter(alignment_tuples)
        repeated_tuples = {tup for tup, count in tuples_counts.items() if count > 1}
        if repeated_tuples:
            repeated_tuples_str = ', '.join(f"{annotator}->{segment}"
                                            for annotator, segment in repeated_tuples)

            raise SetPartitionError(f'{repeated_tuples_str} '
                                    f'are found more than once in the set '
                                    f'of unitary alignments')

    @property
    def num_alignments(self):
        return len(self.set_unitary_alignments)

    @property
    def disorder(self):
        if self._disorder is None:
            self._disorder = (sum(u_align.disorder for u_align
                                  in self.set_unitary_alignments)
                              / self.num_alignments)
        return self._disorder

    def compute_disorder(self, dissimilarity: AbstractDissimilarity):
        alignments_sum = 0
        for unit_align in self.set_unitary_alignments:
            try:
                alignments_sum += unit_align.disorder
            except ValueError:
                alignments_sum += unit_align.compute_disorder(dissimilarity)
        self._disorder = alignments_sum / self.num_alignments
        return self._disorder
