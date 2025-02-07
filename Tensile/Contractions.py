#################################################################################
# Copyright (C) 2019 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell cop-
# ies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IM-
# PLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNE-
# CTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
################################################################################

from .DataType import DataType
from . import Hardware
from . import Properties
from .SolutionStructs import Solution as OriginalSolution
from .Utils import state, state_key_ordering


@state_key_ordering
class FreeIndex:
    StateKeys = ['isA', 'i', 'c', 'd']

    def __init__(self, isA, i=None, c=None, d=None):
        self.isA = isA
        self.i = i # index into A or B (depending on isA)
        self.c = c
        self.d = d

@state_key_ordering
class BatchIndex:
    StateKeys = ['a', 'b', 'c', 'd']
    def __init__(self, a=None, b=None, c=None, d=None):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

@state_key_ordering
class BoundIndex:
    StateKeys = ['a', 'b']
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b


class ProblemType:
    StateKeys = ['operationIdentifier', 'aType', 'bType', 'cType', 'dType',
                 'useBeta', 'highPrecisionAccumulate']
    @classmethod
    def FromOriginalState(cls, d):
        indices = [None]*d['TotalIndices']
        freeIndices  = []
        batchIndices = []
        boundIndices = []

        for i in d['IndicesSummation']:
            bi = BoundIndex()
            indices[i] = bi
            boundIndices.append(bi)

        for i in range(0,d["NumIndicesC"]):
            if i in d['IndicesBatch']:
                bi = BatchIndex(c=i, d=i)
                indices[i] = bi
                batchIndices.append(bi)
            else:
                assert i in d['IndicesFree']
                if i in d['IndexAssignmentsA']:
                    fi = FreeIndex(isA=True, i=d["IndexAssignmentsA"].index(i), c=i, d=i)
                elif i in d['IndexAssignmentsB']:
                    fi = FreeIndex(isA=False, i=d["IndexAssignmentsB"].index(i), c=i, d=i)
                else:
                    raise RuntimeError("free index %u not in ia or ib"%i)
                indices[i] = fi
                freeIndices.append(fi)

        for ia, ic in enumerate(d['IndexAssignmentsA']):
            indices[ic].a = ia

        for ib, ic in enumerate(d['IndexAssignmentsB']):
            indices[ic].b = ib

        for idx in indices:
            assert idx is not None
            idxState = state(idx)
            for (key, value) in list(idxState.items()):
                assert value is not None

        rv = cls()
        rv.indices = indices
        rv.freeIndices = freeIndices
        rv.batchIndices = batchIndices
        rv.boundIndices = boundIndices
        rv.aDims = len(d['IndexAssignmentsA'])
        rv.bDims = len(d['IndexAssignmentsB'])
        rv.cDims = d['NumIndicesC']
        rv.dDims = rv.cDims

        rv.aConjugate = d['ComplexConjugateA']
        rv.bConjugate = d['ComplexConjugateB']

        srcType = DataType(d['DataType'])
        dstType = DataType(d['DestDataType']) if 'DestDataType' in d else srcType

        rv.aType = srcType
        rv.bType = srcType
        rv.cType = dstType
        rv.dType = dstType

        rv.highPrecisionAccumulate = False
        if 'HighPrecisionAccumulate' in d:
            rv.highPrecisionAccumulate = d['HighPrecisionAccumulate']

        if 'SetConstStrideA' in d:
            rv.setConstStrideA = d['SetConstStrideA']
        if 'SetConstStrideB' in d:
            rv.setConstStrideB = d['SetConstStrideB']

        rv.useBeta = True
        if 'UseBeta' in d:
            rv.useBeta = d['UseBeta']

        rv.batched = d['Batched']

        return rv

    def __init__(self, freeIndices=None, batchIndices=None, boundIndices=None, aDims=None, bDims=None, cDims=None, dDims=None):
        self.convolution = None
        self.freeIndices  = freeIndices
        self.batchIndices = batchIndices
        self.boundIndices = boundIndices
        self.aDims = aDims
        self.bDims = bDims
        self.cDims = cDims
        self.dDims = dDims

    @property
    def indexNames(self):
        aNames = ['_'] * self.aDims
        bNames = ['_'] * self.bDims
        cNames = ['_'] * self.cDims

        allIndexNames = 'ijklmnopqrstuvwxyz'
        index = 0

        dNames = list([allIndexNames[index+i] for i in range(self.cDims)])
        index += len(dNames)

        sumNames = list([allIndexNames[index+i] for i in range(len(self.boundIndices))])
        index += len(sumNames)

        for free in self.freeIndices:
            if free.isA:
                aNames[free.i ] = dNames[free.d]
            else:
                bNames[free.i ] = dNames[free.d]
            cNames[free.c] = dNames[free.d]

        for batch in self.batchIndices:
            name = dNames[batch.d]
            aNames[batch.a] = name
            bNames[batch.b] = name
            cNames[batch.c] = name

        for i, bound in enumerate(self.boundIndices):
            name = sumNames[i]
            aNames[bound.a] = name
            bNames[bound.b] = name

        aNames = ''.join(aNames)
        bNames = ''.join(bNames)
        cNames = ''.join(cNames)
        dNames = ''.join(dNames)
        sumNames = ''.join(sumNames)

        return (aNames, bNames, cNames, dNames, sumNames)

    @property
    def operationIdentifier(self):
        (aNames, bNames, cNames, dNames, sumNames) = self.indexNames

        aOp = 'C' if self.aConjugate else ''
        bOp = 'C' if self.bConjugate else ''

        return '_'.join(['Contraction', sumNames,
                         'A' + aNames + aOp,
                         'B' + bNames + bOp,
                         'C' + cNames,
                         'D' + dNames])

    def predicates(self, includeBatch=False, includeOperation=False, includeType=False):
        predicates = []

        #if includeBatch and not self.batched:
        #    predicates.append(ProblemPredicate("BatchSizeEqual", index=0, value=1))

        if includeOperation:
            predicates.append(ProblemPredicate("OperationIdentifierEqual", value=self.operationIdentifier))
            if not self.useBeta:
                predicates.append(ProblemPredicate("BetaZero"));

        if includeType:
            predicates.append(ProblemPredicate("TypesEqual", value=(self.aType, self.bType, self.cType, self.dType)))
            predicates.append(ProblemPredicate("HighPrecisionAccumulate", value=self.highPrecisionAccumulate))

        return predicates

class ProblemPredicate(Properties.Predicate):
    @classmethod
    def FromOriginalKeyPair(cls, pair):
        (key, value) = pair
        # TODO - change to use SetConstStrideB
        if key == 'PackBatchDims' and value==1:
            return cls("StrideBEqual", index=2, value=0)
        if key == 'AssertMinApproxSize':
            if value == 0 or value == 1:
                return None
            elif value == 2:
                return cls('MaxProblemSizeGreaterThan', value=1)
            elif value == 3:
                return cls('MaxProblemSizeGreaterThan', value=32)
            else:
                raise RuntimeError("Unknown Approx size: {}".format(value))

        if key.endswith('Multiple'):
            if value == 1:
                return None

            if key == "AssertFree0ElementMultiple":
                tag = "FreeSizeAMultiple"
                index = 0
            elif key == "AssertFree1ElementMultiple":
                tag = "FreeSizeBMultiple"
                index = 0
            elif key == "AssertSummationElementMultiple":
                tag = "BoundSizeMultiple"
                index = 0
            else:
                raise RuntimeError("Unknown Multiple Value: {}".format(key))

            return cls(tag, index=index, value=value)

        if key == 'VectorWidth' and value > 1:
            return cls('LeadingFreeSizesGreaterOrEqual', value=value)

        if key.startswith('Assert'):
            raise RuntimeError("Unknown assertion key: {}".format(key))

    @classmethod
    def FromOriginalState(cls, d, problemType, morePreds=[]):
        problemTypePreds = problemType.predicates(True, True, True)

        return super().FromOriginalState(d, problemTypePreds + morePreds)

class SizeMapping:
    StateKeys = ['workGroup',
                 'macroTile',
                 'threadTile',
                 'depthU',
                 'staggerU',
                 'globalSplitU',
                 'staggerStrideShift',
                 'workGroupMapping',
                 'packBatchDims',
                 'persistentKernel',
                 'sourceKernel',
                 ]

    @classmethod
    def FromOriginalState(cls, d):
        return cls(workGroup          = d['WorkGroup'],
                   macroTile          = cls.ReadOriginalMacroTile(d),
                   threadTile         = d['ThreadTile'],
                   workGroupMapping   = d['WorkGroupMapping'],
                   staggerU           = d['StaggerU'] if 'StaggerU' in d else 0,
                   depthU             = d['DepthU'],
                   globalSplitU       = d['GlobalSplitU'],
                   staggerStrideShift = d['_staggerStrideShift'] if '_staggerStrideShift' in d else 0,
                   packBatchDims      = d['PackBatchDims'] if 'PackBatchDims' in d else 0,
                   persistentKernel   = d['PersistentKernel'] if 'PersistentKernel' in d else 0,
                   sourceKernel       = d['KernelLanguage'] == 'Source',
                   )

    @classmethod
    def ReadOriginalMacroTile(cls, d):
        rv = [1,1,1]
        rv[0] = d['MacroTile0']
        rv[1] = d['MacroTile1']
        return rv

    def __init__(self, **kwargs):
        for (key, value) in list(kwargs.items()):
            setattr(self, key, value)

class Solution:
    StateKeys = ['name',
                'problemType',
                'hardwarePredicate',
                'problemPredicate',
                'sizeMapping',
                'debugKernel',
                'info',
                'index',
                'ideals']
    HiddenKeys = ['originalSolution']

    @classmethod
    def FromOriginalState(cls, d, deviceInfo=None):
        rv = cls()


        if 'SolutionNameMin' in d:
            rv.name = d['SolutionNameMin']

        rv.problemType = ProblemType.FromOriginalState(d['ProblemType'])

        rv.problemPredicate = ProblemPredicate.FromOriginalState(d, rv.problemType)

        if 'DebugKernel' in d:
            rv.debugKernel = d['DebugKernel']

        if 'SolutionIndex' in d:
            rv.index = d['SolutionIndex']

        rv.info = cls.ReadOriginalInfo(d)

        rv.sizeMapping = SizeMapping.FromOriginalState(d)
        if 'Ideals' in d:
            rv.ideals = d['Ideals']
        else:
            rv.ideals = {}

        if d['KernelLanguage'] == 'Assembly':
            if 'ISA' not in d:
                d['ISA'] = list(map(int,deviceInfo[1][3:6]))

            rv.hardwarePredicate = Hardware.HardwarePredicate.FromISA(d['ISA'])
        else:
            d['ISA'] = [0,0,0]

        rv.originalSolution = OriginalSolution(d)

        return rv

    @classmethod
    def ReadOriginalInfo(cls, d):
        return dict([(key, str(value)) for (key, value) in list(d.items()) if key != 'ProblemType'])

    def __init__(self, **kwargs):
        self.name = None
        self.problemType = None
        self.hardwarePredicate = Hardware.HardwarePredicate('TruePred')
        self.problemPredicate = ProblemPredicate('TruePred')
        self.sizeMapping = None
        self.debugKernel = False
        self.info = {}
        self.index = None
        self.ideals = {}

        for key, value in kwargs:
            if key not in Solution.StateKeys and key not in Solution.HiddenKeys:
                raise KeyError("{0} is not a property of Solution.".format(key))

            setattr(self, key, value)

