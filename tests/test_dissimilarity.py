"""Test of the module pygamma.continuum"""

import tempfile
import numpy as np
from pygamma.continuum import Continuum
from pygamma.dissimilarity import Categorical_Dissimilarity
from pygamma.dissimilarity import Sequence_Dissimilarity
from pygamma.dissimilarity import Positional_Dissimilarity
from pygamma.dissimilarity import Combined_Categorical_Dissimilarity
from pygamma.dissimilarity import Combined_Sequence_Dissimilarity

from pyannote.core import Annotation, Segment

import pytest


def test_categorical_dissimilarity():
    continuum = Continuum()
    annotation = Annotation()
    annotation[Segment(1, 5)] = 'Carol'
    annotation[Segment(6, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Carol'
    annotation[Segment(7, 20)] = 'Alice'
    continuum['liza'] = annotation
    annotation = Annotation()
    annotation[Segment(2, 6)] = 'Carol'
    annotation[Segment(7, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Alice'
    annotation[Segment(8, 10)] = 'Alice'
    annotation[Segment(7, 19)] = 'Jeremy'
    continuum['pierrot'] = annotation
    categories = ['Carol', 'Bob', 'Alice', 'Jeremy']
    cat = np.array([[0, 0.5, 0.3, 0.7], [0.5, 0., 0.6, 0.4],
                    [0.3, 0.6, 0., 0.7], [0.7, 0.4, 0.7, 0.]])

    cat_dis = Categorical_Dissimilarity(
        'diarization',
        list_categories=categories,
        categorical_dissimilarity_matrix=cat,
        DELTA_EMPTY=0.5)

    assert cat_dis[['Carol', 'Carol']] == 0.
    assert cat_dis[['Carol', 'Jeremy']] == 0.35
    assert cat_dis[['Carol', 'Jeremy']] == cat_dis[['Jeremy', 'Carol']]


def test_sequence_dissimilarity():
    continuum = Continuum()
    annotation = Annotation()
    annotation[Segment(1, 5)] = ('a', 'b', 'b')
    annotation[Segment(6, 8)] = ('a', 'b')
    annotation[Segment(12, 18)] = ('a', 'c', 'c', 'c')
    annotation[Segment(7, 20)] = ('b', 'b', 'c', 'c', 'a')
    continuum['liza'] = annotation
    annotation = Annotation()
    annotation[Segment(2, 6)] = ('a', 'b', 'b')
    annotation[Segment(7, 8)] = ('a')
    annotation[Segment(12, 18)] = ('b', 'c', 'b', 'c')
    annotation[Segment(8, 10)] = ('a', 'a')
    annotation[Segment(7, 19)] = ('b', 'b', 'a', 'c', 'a')
    continuum['pierrot'] = annotation
    annotation = Annotation()

    annotation[Segment(1, 6)] = ('a', 'b', 'b')
    annotation[Segment(8, 10)] = ('a', 'b')
    annotation[Segment(7, 19)] = ('a', 'c', 'b', 'c')
    annotation[Segment(19, 20)] = ('a', 'c')

    continuum['hadrien'] = annotation
    symbols = ['a', 'b', 'c', 'd']
    cat = np.array([[0, 0.5, 0.3, 0.7], [0.5, 0., 0.6, 0.4],
                    [0.3, 0.6, 0., 0.7], [0.7, 0.4, 0.7, 0.]])

    seq_dis = Sequence_Dissimilarity(
        'SR', list_admitted_symbols=symbols, symbol_dissimlarity_matrix=cat)

    assert seq_dis[[('a', 'c', 'a', 'c'), ('a', 'c', 'a', 'c')]] == 0.0
    assert seq_dis[[('a', 'c', 'a', 'c'), ('a', 'c', 'b', 'c')]] == 0.125
    assert seq_dis[[('a', 'c', 'a', 'c'),
                    ('a', 'c', 'b', 'c')]] == seq_dis[[('a', 'c', 'b', 'c'),
                                                       ('a', 'c', 'a', 'c')]]


def test_positional_dissimilarity():
    continuum = Continuum()
    annotation = Annotation()
    annotation[Segment(1, 5)] = 'Carol'
    annotation[Segment(6, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Carol'
    annotation[Segment(7, 20)] = 'Alice'
    continuum['liza'] = annotation
    annotation = Annotation()
    annotation[Segment(2, 6)] = 'Carol'
    annotation[Segment(7, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Alice'
    annotation[Segment(8, 10)] = 'Alice'
    annotation[Segment(7, 19)] = 'Jeremy'
    continuum['pierrot'] = annotation
    categories = ['Carol', 'Bob', 'Alice', 'Jeremy']

    pos_dis = Positional_Dissimilarity('diarization', DELTA_EMPTY=0.5)

    list_dis = []
    for liza_unit in continuum['liza'].itersegments():
        for pierrot_unit in continuum['pierrot'].itersegments():
            list_dis.append(pos_dis[[liza_unit, pierrot_unit]])
    assert list_dis == pytest.approx([
        0.03125, 1.62, 0.78125, 2.0, 2.88, 0.5, 0.05555555555555555,
        0.36734693877551017, 0.5, 2.0, 0.6245674740484429, 0.36734693877551017,
        0.0008, 0.26888888888888884, 0.06786703601108032, 2.4200000000000004,
        2.2959183673469385, 0.05555555555555555, 1.125, 0.0
    ], 0.001)
    assert pos_dis[[liza_unit,
                    pierrot_unit]] == pos_dis[[pierrot_unit, liza_unit]]
    assert pos_dis[[liza_unit, liza_unit]] == 0
    assert pos_dis[[liza_unit]] == 1 * 0.5


def test_combi_categorical_dissimilarity():
    continuum = Continuum()
    annotation = Annotation()
    annotation[Segment(1, 5)] = 'Carol'
    annotation[Segment(6, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Carol'
    annotation[Segment(7, 20)] = 'Alice'
    continuum['liza'] = annotation
    annotation = Annotation()
    annotation[Segment(2, 6)] = 'Carol'
    annotation[Segment(7, 8)] = 'Bob'
    annotation[Segment(12, 18)] = 'Alice'
    annotation[Segment(8, 10)] = 'Alice'
    annotation[Segment(7, 19)] = 'Jeremy'
    continuum['pierrot'] = annotation
    categories = ['Carol', 'Bob', 'Alice', 'Jeremy']

    cat = np.array([[0, 0.5, 0.3, 0.7], [0.5, 0., 0.6, 0.4],
                    [0.3, 0.6, 0., 0.7], [0.7, 0.4, 0.7, 0.]])
    combi_dis = Combined_Categorical_Dissimilarity(
        'diarization',
        list_categories=categories,
        DELTA_EMPTY=0.5,
        categorical_dissimilarity_matrix=cat)
    pos_dis = Positional_Dissimilarity('diarization', DELTA_EMPTY=0.5)
    cat_dis = Categorical_Dissimilarity(
        'diarization',
        list_categories=categories,
        categorical_dissimilarity_matrix=cat,
        DELTA_EMPTY=0.5)

    list_dis = []
    for liza_unit in continuum['liza'].itersegments():
        for pierrot_unit in continuum['pierrot'].itersegments():
            list_dis.append(combi_dis[[liza_unit, pierrot_unit], [
                continuum['liza'][liza_unit], continuum['pierrot'][
                    pierrot_unit]
            ]])
    assert list_dis == pytest.approx([
        0.03125, 1.87, 1.13125, 2.15, 3.03, 0.75, 0.05555555555555555,
        0.5673469387755101, 0.8, 2.3, 0.774567474048443, 0.6673469387755102,
        0.3508, 0.26888888888888884, 0.06786703601108032, 2.4200000000000004,
        2.5459183673469385, 0.40555555555555556, 1.275, 0.15
    ], 0.001)
    assert combi_dis[[liza_unit, pierrot_unit], [
        continuum['liza'][liza_unit], continuum['pierrot'][pierrot_unit]
    ]] == combi_dis[[pierrot_unit, liza_unit], [
        continuum['pierrot'][pierrot_unit], continuum['liza'][liza_unit]
    ]]
    assert combi_dis[[liza_unit, liza_unit], [
        continuum['liza'][liza_unit], continuum['liza'][liza_unit]
    ]] == 0
    assert combi_dis[[liza_unit], [continuum['liza'][liza_unit]]] == 1 * 0.5


def test_combi_sequence_dissimilarity():
    continuum = Continuum()
    annotation = Annotation()
    annotation[Segment(1, 5)] = ('a', 'b', 'b')
    annotation[Segment(6, 8)] = ('a', 'b')
    annotation[Segment(12, 18)] = ('a', 'c', 'c', 'c')
    annotation[Segment(7, 20)] = ('b', 'b', 'c', 'c', 'a')
    continuum['liza'] = annotation
    annotation = Annotation()
    annotation[Segment(2, 6)] = ('a', 'b', 'b')
    annotation[Segment(7, 8)] = ('a')
    annotation[Segment(12, 18)] = ('b', 'c', 'b', 'c')
    annotation[Segment(8, 10)] = ('a', 'a')
    annotation[Segment(7, 19)] = ('b', 'b', 'a', 'c', 'a')
    continuum['pierrot'] = annotation
    annotation = Annotation()

    annotation[Segment(1, 6)] = ('a', 'b', 'b')
    annotation[Segment(8, 10)] = ('a', 'b')
    annotation[Segment(7, 19)] = ('a', 'c', 'b', 'c')
    annotation[Segment(19, 20)] = ('a', 'c')

    continuum['hadrien'] = annotation

    symbols = ['a', 'b', 'c', 'd']
    cat = np.array([[0, 0.5, 0.3, 0.7], [0.5, 0., 0.6, 0.4],
                    [0.3, 0.6, 0., 0.7], [0.7, 0.4, 0.7, 0.]])

    combi_dis = Combined_Sequence_Dissimilarity(
        'SR',
        list_admitted_symbols=symbols,
        DELTA_EMPTY=0.5,
        symbol_dissimlarity_matrix=cat)
    list_dis = []
    for liza_unit in continuum['liza'].itersegments():
        for pierrot_unit in continuum['pierrot'].itersegments():
            list_dis.append(combi_dis[[liza_unit, pierrot_unit], [
                continuum['liza'][liza_unit], continuum['pierrot'][
                    pierrot_unit]
            ]])
    assert list_dis == pytest.approx([
        0.03125, 1.9533333333333334, 1.08125, 2.25, 3.1174999999999997,
        0.6666666666666666, 0.3055555555555556, 0.7173469387755101, 0.625,
        2.2875, 0.9245674740484429, 0.7673469387755102, 0.030799999999999998,
        0.5988888888888888, 0.2578670360110803, 2.6950000000000003,
        2.6709183673469385, 0.26555555555555554, 1.4125, 0.1375
    ], 0.001)
    assert combi_dis[[liza_unit, pierrot_unit], [
        continuum['liza'][liza_unit], continuum['pierrot'][pierrot_unit]
    ]] == combi_dis[[pierrot_unit, liza_unit], [
        continuum['pierrot'][pierrot_unit], continuum['liza'][liza_unit]
    ]]
    assert combi_dis[[liza_unit, liza_unit], [
        continuum['liza'][liza_unit], continuum['liza'][liza_unit]
    ]] == 0
    assert combi_dis[[liza_unit], [continuum['liza'][liza_unit]]] == 1 * 0.5
